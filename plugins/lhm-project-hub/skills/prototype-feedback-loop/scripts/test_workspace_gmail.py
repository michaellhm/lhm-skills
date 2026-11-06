"""Deterministic tests only; real OAuth/MCP verification belongs to live acceptance."""
import hashlib
import asyncio
import sys
from contextlib import asynccontextmanager
from types import ModuleType, SimpleNamespace
import os
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import patch
from workspace_gmail import (ARGS, EXISTING_ARGS, COMMAND, MAX_EML, WorkspaceGmail, parse_raw_mime, read_saved_eml)


class MimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.images = self.root / 'images'
        self.message = EmailMessage()
        self.message['From'] = 'Tara <tara@example.com>'
        self.message['To'] = 'michael@example.com'
        self.message['Date'] = 'Fri, 6 Nov 2026 17:19:18 +1030'
        self.message['Subject'] = 'Prototype feedback'
        self.message.set_content('Please change the logo and roots texture.')
        self.message.add_attachment(b'first PNG bytes', maintype='image', subtype='png', filename='image.png', cid='<sun>')
        self.message.add_attachment(b'second PNG bytes', maintype='image', subtype='png', filename='image.png', cid='<roots>')

    def parse(self, raw=None):
        return parse_raw_mime(self.message.as_bytes() if raw is None else raw,
            message_id='1a1af9e9eeb719cb', account='michael@example.com', image_root=self.images)

    def test_same_filename_materialises_distinct_content_ids_hashes_and_files(self):
        packet = self.parse()
        images = packet['attachments']
        self.assertEqual([image['filename'] for image in images], ['image.png', 'image.png'])
        self.assertEqual([image['content_id'] for image in images], ['sun', 'roots'])
        self.assertNotEqual(images[0]['private_ref'], images[1]['private_ref'])
        self.assertEqual(images[0]['sha256'], hashlib.sha256(b'first PNG bytes').hexdigest())
        self.assertEqual(images[1]['sha256'], hashlib.sha256(b'second PNG bytes').hexdigest())
        self.assertTrue(all(image['status'] == 'materialised' and image['visually_reviewed'] is False for image in images))
        self.assertFalse(packet['extraction_reviewed'])
        self.assertEqual(self.parse(), packet)

    def test_duplicate_content_id_is_ambiguous(self):
        self.message.get_payload()[2].replace_header('Content-ID', '<sun>')
        with self.assertRaisesRegex(ValueError, 'duplicate Content-ID'):
            self.parse()

    def test_truncated_multipart_blocks(self):
        raw = self.message.as_bytes()
        raw = raw[:raw.rfind(b'--' + self.message.get_boundary().encode())]
        with self.assertRaisesRegex(ValueError, 'truncated MIME'):
            self.parse(raw)

    def test_symlink_image_target_blocks(self):
        packet = self.parse()
        target = Path(packet['attachments'][0]['private_ref'])
        external = self.root / 'external'
        external.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(external)
        with self.assertRaises(OSError):
            self.parse()

    def test_existing_image_with_changed_bytes_blocks(self):
        packet = self.parse()
        Path(packet['attachments'][0]['private_ref']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            self.parse()

    def test_output_directory_must_be_private(self):
        self.images.mkdir(mode=0o755)
        with self.assertRaisesRegex(ValueError, 'private'):
            self.parse()

    def test_naive_timestamp_blocks(self):
        self.message.replace_header('Date', 'Fri, 6 Nov 2026 17:19:18 -0000')
        with self.assertRaisesRegex(ValueError, 'timezone'):
            self.parse()

    def test_invalid_message_id_blocks(self):
        with self.assertRaisesRegex(ValueError, 'message ID'):
            parse_raw_mime(self.message.as_bytes(), message_id='../msg', account='michael@example.com', image_root=self.images)

    def test_sender_required(self):
        del self.message['From']
        with self.assertRaisesRegex(ValueError, 'sender'):
            self.parse()


class SavedFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'message.eml'
        self.path.write_bytes(b'raw MIME')

    def read(self, text=None):
        return read_saved_eml(text or 'Saved to: ' + str(self.path), attachments_root=self.root)

    def test_valid_saved_path(self):
        self.assertEqual(self.read(), b'raw MIME')

    def test_literal_paperclip_prefix(self):
        self.assertEqual(self.read('📎 Saved to: ' + str(self.path)), b'raw MIME')

    def test_truncated_path_blocks(self):
        with self.assertRaises(ValueError):
            self.read('Saved to: ' + str(self.path)[:-2] + '...')

    def test_multiple_paths_block(self):
        with self.assertRaises(ValueError):
            self.read('Saved to: ' + str(self.path) + '\nSaved to: ' + str(self.path))

    def test_outside_root_and_traversal_block(self):
        for path in (self.root.parent / 'outside.eml', self.root / '..' / 'message.eml'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.read('Saved to: ' + str(path))

    def test_symlink_final_file_blocks(self):
        self.path.unlink()
        self.path.symlink_to(self.root / 'missing.eml')
        with self.assertRaises(OSError):
            self.read()

    def test_symlink_intermediate_directory_blocks(self):
        (self.root / 'link').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            self.read('Saved to: ' + str(self.root / 'link/message.eml'))

    def test_oversize_and_empty_block(self):
        self.path.write_bytes(b'')
        with self.assertRaises(ValueError):
            self.read()
        with self.path.open('wb') as stream:
            stream.truncate(MAX_EML + 1)
        with self.assertRaises(ValueError):
            self.read()


class TransportTests(unittest.TestCase):
    def test_read_allowlist_rejects_writes(self):
        WorkspaceGmail.validate_tool('get_gmail_message_content')
        for tool in ('send_gmail_message', 'create_gmail_draft', 'delete_gmail_message', 'get_drive_file'):
            with self.subTest(tool=tool), self.assertRaises(ValueError):
                WorkspaceGmail.validate_tool(tool)

    def test_snake_case_error_and_private_stderr(self):
        seen = {}
        @asynccontextmanager
        async def stdio(params, errlog):
            seen['stderr'] = errlog
            yield ('read', 'write')
        class Session:
            def __init__(self, *args): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def initialize(self): pass
            async def list_tools(self):
                return SimpleNamespace(tools=[SimpleNamespace(name='get_gmail_message_content', input_schema={'required': []})])
            async def call_tool(self, *args):
                return SimpleNamespace(is_error=True, content=[])
        sdk = ModuleType('mcp')
        sdk.ClientSession = Session
        sdk.StdioServerParameters = lambda **kwargs: kwargs
        client = ModuleType('mcp.client')
        transport = ModuleType('mcp.client.stdio')
        transport.stdio_client = stdio
        adapter = WorkspaceGmail()
        with patch.dict(sys.modules, {'mcp': sdk, 'mcp.client': client, 'mcp.client.stdio': transport}), patch.object(adapter, 'parameters', return_value={}):
            with self.assertRaisesRegex(RuntimeError, 'Gmail read failed'):
                asyncio.run(adapter.call('get_gmail_message_content', {}))
        self.assertTrue(seen['stderr'].closed)
        self.assertNotEqual(seen['stderr'], sys.stderr)

    def test_config_preserves_env_without_returning_secret_in_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.toml'
            path.write_text('[mcp_servers.workspace]\ncommand = "' + COMMAND + '"\nargs = ' + repr(ARGS).replace("'", '"') + '\n[mcp_servers.workspace.env]\nEXISTING_SETTING = "preserved"\n')
            params = WorkspaceGmail(path).parameters()
            self.assertEqual(params['command'], COMMAND)
            self.assertEqual(params['args'], ARGS)
            self.assertEqual(params['env']['EXISTING_SETTING'], 'preserved')
            path.write_text('[mcp_servers.workspace]\ncommand = "' + COMMAND + '"\nargs = ' + repr(EXISTING_ARGS).replace("'", '"') + '\n')
            self.assertEqual(WorkspaceGmail(path).parameters()['args'], ARGS)
            path.write_text('[mcp_servers.workspace]\ncommand = "sh"\nargs = []\n')
            with self.assertRaisesRegex(ValueError, 'read-only'):
                WorkspaceGmail(path).parameters()


if __name__ == '__main__':
    unittest.main()
