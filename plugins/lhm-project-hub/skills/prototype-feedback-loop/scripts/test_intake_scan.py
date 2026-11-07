"""Scanner contract tests use fake provider boundary; no live model/API proof."""
import copy
import hashlib
import json
import os
import sqlite3
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from intake_scan import Scanner, Worker, canonical, directory_fd, bounded_bytes, trusted_gmail_authentication, interpretation_safety_args, reject_unexpected_tool_events, review_input, search_page, validate_extraction
from workspace_gmail import parse_raw_mime


REG = {'account': 'michael@example.com', 'senders': ['tara@example.com'], 'threads': ['1a1a8d364f7f2f43'],
    'review_start': '2026-11-05T00:00:00+11:00', 'client_label': 'Blue Dragonfly', 'cockpit_id': 1,
    'preview_url': 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/'}


def native_page(message='1a1af9e9eeb719cb', thread='1a1a8d364f7f2f43', cursor=None):
    return (f"Found 1 messages matching 'query':\n\n📧 MESSAGES:\n  1. Message ID: {message}\n"
        f"     Web Link: https://mail.google.com/#all/{message}\n     Thread ID: {thread}\n"
        + (f"📄 PAGINATION: To get the next page, call search_gmail_messages again with page_token='{cursor}'" if cursor else ''))


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        message = EmailMessage()
        message['From'] = 'Tara <tara@example.com>'
        message['Date'] = 'Fri, 6 Nov 2026 17:19:18 +1030'
        message['Subject'] = 'Luminary Counselling feedback'
        message['Authentication-Results'] = 'mx.google.com; dkim=pass header.i=@example.com; dmarc=pass header.from=example.com'
        message.set_content('For Luminary Counselling, please change the logo.\n')
        message.add_attachment(b'image bytes', maintype='image', subtype='png', filename='image.png', cid='<sun>')
        self.raw = message.as_bytes()
        self.prepared = parse_raw_mime(self.raw, message_id='1a1af9e9eeb719cb', account=REG['account'], image_root=self.root / 'images')
        self.result = {'kind': 'feedback', 'related': True, 'relation_quote': 'For Luminary Counselling, please change the logo.',
            'reason': 'A direct change request', 'items': [{'id': '1', 'request': 'Use an illustrated sun logo.'}],
            'images': [{'content_id': 'sun', 'sha256': hashlib.sha256(b'image bytes').hexdigest(),
                        'visual_description': 'A hand-drawn golden sun face.', 'nearby_context': 'Please change the logo.'}]}

    def test_numbered_items_and_visual_review_produce_verified_manifest(self):
        images = validate_extraction(self.result, self.prepared, REG, REG['threads'][0])
        self.assertEqual(images[0]['status'], 'verified')
        self.assertIn('golden sun', images[0]['context'])

    def test_unmapped_thread_requires_literal_prototype_quote(self):
        self.result['relation_quote'] = 'that website'
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            validate_extraction(self.result, self.prepared, REG, '1a1afefeaf44048e')
        self.result['relation_quote'] = 'For Luminary Counselling, please change the logo.'
        self.assertEqual(len(validate_extraction(self.result, self.prepared, REG, '1a1afefeaf44048e')), 1)

    def test_missing_or_swapped_image_blocks(self):
        for images in ([], [dict(self.result['images'][0], content_id='other')], [dict(self.result['images'][0], sha256='a'*64)]):
            result = dict(self.result, images=images)
            with self.subTest(images=images), self.assertRaises(ValueError):
                validate_extraction(result, self.prepared, REG, REG['threads'][0])

    def test_empty_visual_interpretation_blocks(self):
        self.result['images'][0]['visual_description'] = ''
        with self.assertRaises(ValueError):
            validate_extraction(self.result, self.prepared, REG, REG['threads'][0])

    def test_noop_cannot_contain_changes(self):
        self.result['kind'] = 'acknowledgement'
        with self.assertRaisesRegex(ValueError, 'requested changes'):
            validate_extraction(self.result, self.prepared, REG, REG['threads'][0])

    def test_numbers_must_start_at_one(self):
        self.result['items'][0]['id'] = '2'
        with self.assertRaisesRegex(ValueError, 'numbered'):
            validate_extraction(self.result, self.prepared, REG, REG['threads'][0])

    def test_email_cannot_add_authority_fields(self):
        self.result['repository'] = 'michaellhm/live-client'
        with self.assertRaisesRegex(ValueError, 'closed schema'):
            validate_extraction(self.result, self.prepared, REG, REG['threads'][0])

    def test_registered_sender_and_window_independent_of_model(self):
        review_input(self.prepared, REG, REG['threads'][0])
        for packet in (dict(self.prepared, sender='other@example.com'), dict(self.prepared, received_at='2020-01-01T00:00:00+00:00')):
            with self.assertRaises(ValueError):
                review_input(packet, REG, REG['threads'][0])

    def test_nonimage_attachment_requires_separate_capability(self):
        self.prepared['attachments'][0]['mime_type'] = 'application/pdf'
        with self.assertRaisesRegex(ValueError, 'separate verified'):
            review_input(self.prepared, REG, REG['threads'][0])

    def test_native_extraction_command_is_readonly_and_attaches_images(self):
        work = self.root / 'work'
        work.mkdir(mode=0o700)
        seen = {}
        def run(command, **kwargs):
            seen.update(command=command, kwargs=kwargs)
            output = Path(command[command.index('--output-last-message') + 1])
            output.write_text(json.dumps(self.result)); output.chmod(0o600)
            return SimpleNamespace(returncode=0, stdout=json.dumps({'type': 'thread.started', 'thread_id': '12345678-1234-1234-1234-123456789abc'}) + '\n')
        with patch('intake_scan.os.fchown'):
            result, reviewer = Worker(runner=run).extract(self.prepared, REG, REG['threads'][0], work)
        self.assertEqual(result, self.result)
        self.assertEqual(reviewer, 'codex:12345678-1234-1234-1234-123456789abc')
        self.assertIn('--ignore-user-config', seen['command'])
        self.assertIn('--strict-config', seen['command'])
        self.assertIn('code_mode_host', seen['command'])
        self.assertIn('shell_tool', seen['command'])
        self.assertIn('web_search="disabled"', seen['command'])
        self.assertIn('skills.include_instructions=false', seen['command'])
        self.assertIn('--ephemeral', seen['command'])
        self.assertIn('--sandbox', seen['command'])
        self.assertIn('read-only', seen['command'])
        self.assertIn('--image', seen['command'])
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', seen['command'])
        self.assertIn('untrusted data', seen['kwargs']['input'])
        self.assertIn('Exclude quoted original messages, forwarded history and signatures', seen['kwargs']['input'])

    def test_nonimage_never_reaches_model_command(self):
        self.prepared['attachments'][0]['mime_type'] = 'application/pdf'
        called = []
        with self.assertRaisesRegex(ValueError, 'separate verified'):
            Worker(runner=lambda *args, **kwargs: called.append(args)).extract(self.prepared, REG, REG['threads'][0], self.root / 'work')
        self.assertEqual(called, [])

    def test_already_queued_message_skips_gmail_and_model(self):
        state = self.root / 'state'
        state.mkdir(mode=0o700)
        (state / 'state').mkdir(mode=0o700)
        database = state / 'state' / 'queue.sqlite'
        with sqlite3.connect(database) as db:
            db.execute('CREATE TABLE messages (account TEXT, message_id TEXT, site TEXT, packet TEXT)')
            db.execute('INSERT INTO messages VALUES (?,?,?,?)',
                (REG['account'], '1a1af9e9eeb719cb', 'luminary-counselling', json.dumps({'thread_id': REG['threads'][0]})))
        database.chmod(0o600)
        called = []
        class Fake:
            def raw(self, *args): called.append('raw')
            def extract(self, *args): called.append('extract')
        real_fstat = os.fstat
        def root_stat(fd):
            info = real_fstat(fd)
            return SimpleNamespace(st_mode=info.st_mode, st_uid=0)
        scanner = Scanner(state, Fake(), self.root / 'scan')
        with patch('intake_scan.os.fstat', side_effect=root_stat):
            result = scanner.one('luminary-counselling', REG, {'message_id': '1a1af9e9eeb719cb', 'thread_id': REG['threads'][0]})
        self.assertEqual(result['classification'], 'already_queued')
        self.assertEqual(called, [])

    def test_runtime_symlink_never_chowns_external_directory(self):
        work = self.root / 'malicious-work'
        work.mkdir(mode=0o700)
        outside = self.root / 'outside'
        outside.mkdir(mode=0o700)
        (work / 'runtime').symlink_to(outside, target_is_directory=True)
        with patch('intake_scan.os.fchown') as chown:
            with self.assertRaises(OSError):
                Worker(runner=lambda *args, **kwargs: self.fail('must not launch')).extract(self.prepared, REG, REG['threads'][0], work)
        chown.assert_not_called()

    def test_directory_creation_and_reads_reject_intermediate_symlink(self):
        outside = self.root / 'outside'
        outside.mkdir()
        secret = outside / 'data'
        secret.write_bytes(b'not input')
        link = self.root / 'link'
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            directory_fd(link / 'nested', create=True)
        self.assertFalse((outside / 'nested').exists())
        with self.assertRaises(OSError):
            bounded_bytes(link / 'data', 100)

    def test_root_promotion_contains_raw_extraction_and_image_hashes(self):
        outer = self
        class Fake:
            def raw(self, message, account, work):
                raw = work / 'message.eml'; raw.write_bytes(outer.raw)
                return {'raw_path': str(raw), 'packet': parse_raw_mime(outer.raw, message_id=message, account=account, image_root=work / 'images')}
            def extract(self, *args):
                return outer.result, 'codex:12345678-1234-1234-1234-123456789abc'
        scanner = Scanner(self.root / 'state', Fake(), self.root / 'scan')
        with patch('intake_scan.os.fchown'):
            record = scanner.one('luminary-counselling', REG, {'message_id': '1a1af9e9eeb719cb', 'thread_id': REG['threads'][0]})
        envelope = json.loads(Path(record['inbox_path']).read_text())
        self.assertEqual(envelope['schema_version'], 1)
        self.assertEqual(envelope['packet']['cockpit_id'], '1')
        self.assertEqual(envelope['evidence']['packet_sha256'], hashlib.sha256(canonical(envelope['packet'])).hexdigest())
        self.assertEqual(Path(envelope['evidence']['raw_path']).read_bytes(), self.raw)
        receipt = json.loads(Path(envelope['evidence']['extraction_receipt_path']).read_text())
        self.assertEqual(receipt['reviewer'], record['reviewer'])
        self.assertEqual(receipt['attachment_count'], 1)
        self.assertTrue(Path(envelope['packet']['images'][0]['private_ref']).is_relative_to(self.root / 'state'))


class SearchTests(unittest.TestCase):
    def test_native_page_and_pagination(self):
        rows, cursor = search_page(native_page(cursor='token123'))
        self.assertEqual(rows, [{'message_id': '1a1af9e9eeb719cb', 'thread_id': REG['threads'][0]}])
        self.assertEqual(cursor, 'token123')
        self.assertEqual(search_page("No messages found for query: 'from:tara'"), ([], None))

    def test_truncated_page_or_missing_ids_fail(self):
        for text in (native_page().replace('Found 1', 'Found 2'), native_page(thread='unknown'), native_page() + "\n📄 PAGINATION: truncated"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                search_page(text)

    def test_all_pages_and_mapped_thread_read(self):
        class Fake:
            def __init__(self): self.calls = []
            def query(self, tool, args):
                self.calls.append((tool, args))
                if tool == 'get_gmail_thread_content': return 'Mapped context'
                if args.get('page_token'): return native_page(message='1a1afefeaf44048e', thread='1a1afefeaf44048e')
                return native_page(cursor='next')
        fake = Fake()
        rows = Scanner('/unused', fake).candidates(REG)
        self.assertEqual(len(rows), 2)
        self.assertEqual(fake.calls[0][0], 'get_gmail_thread_content')
        self.assertEqual(fake.calls[-1][1]['page_token'], 'next')

    def test_repeated_cursor_fails_closed(self):
        class Fake:
            def query(self, tool, args):
                return 'Mapped context' if tool == 'get_gmail_thread_content' else native_page(cursor='same')
        with self.assertRaisesRegex(ValueError, 'repeated'):
            Scanner('/unused', Fake()).candidates(REG)

    def test_worker_query_rejects_send_before_spawning(self):
        seen = []
        with self.assertRaises(ValueError):
            Worker(runner=lambda *args, **kwargs: seen.append(args)).query('send_gmail_message', {})
        self.assertEqual(seen, [])

    def test_gmail_reads_start_as_worker_with_child_restrictions_and_unique_units(self):
        import types
        seen=[]
        def run(command,**kwargs):
            seen.append((command,kwargs))
            return types.SimpleNamespace(returncode=0,stdout=json.dumps({'result':'mapped context'}))
        worker=Worker(runner=run)
        self.assertEqual(worker.query('get_gmail_thread_content',{'thread_id':'abc'}),'mapped context')
        worker.raw('abc','account@example.com',Path('/fixed/private/work'))
        units=[]
        for command,kwargs in seen:
            self.assertEqual(command[0],'/usr/bin/systemd-run')
            self.assertIn('--property=User=codexworker',command)
            self.assertIn('--property=Group=codexworker',command)
            self.assertIn('--property=NoNewPrivileges=true',command)
            self.assertIn('--property=ProtectSystem=full',command)
            self.assertNotIn('/usr/sbin/runuser',command)
            units.append(next(value for value in command if value.startswith('--unit=')))
            self.assertEqual(kwargs['timeout'],180)
        self.assertNotEqual(*units)
        self.assertEqual(seen[0][0][-5:],['worker-query','--tool','get_gmail_thread_content','--arguments','{"thread_id": "abc"}'])

    def test_failed_account_read_holds_without_exposing_connector_output(self):
        import types
        worker=Worker(runner=lambda *args,**kwargs:types.SimpleNamespace(returncode=1,stdout='private connector output'))
        with self.assertRaisesRegex(RuntimeError,'^private Gmail read failed or response exceeded bound$'):
            worker.query('get_gmail_thread_content',{})



class ReceivingAuthenticationTests(unittest.TestCase):
    valid = 'mx.google.com; dkim=pass header.i=@gmail.com header.s=20260707; dmarc=pass (p=NONE sp=QUARANTINE dis=NONE) header.from=gmail.com'

    def raw(self, *headers):
        message = EmailMessage()
        message['From'] = 'Prototype Client <prototype.client@gmail.com>'
        message['Date'] = 'Fri, 6 Nov 2026 17:19:18 +1030'
        for header in headers:
            message['Authentication-Results'] = header
        message.set_content('Client feedback')
        return message.as_bytes()

    def test_observed_gmail_header_shape_with_comments_and_header_i(self):
        result = trusted_gmail_authentication(self.raw(self.valid), 'prototype.client@gmail.com')
        self.assertEqual(result, {'authserv_id': 'mx.google.com', 'from_domain': 'gmail.com', 'dmarc': 'pass', 'dkim': 'pass'})

    def test_topmost_untrusted_or_failed_header_cannot_use_lower_pass(self):
        for top in ('attacker.example; dkim=pass header.i=@gmail.com; dmarc=pass header.from=gmail.com',
                    'mx.google.com; dkim=fail header.i=@gmail.com; dmarc=fail header.from=gmail.com'):
            with self.subTest(top=top), self.assertRaisesRegex(ValueError, 'held:'):
                trusted_gmail_authentication(self.raw(top, self.valid), 'prototype.client@gmail.com')

    def test_missing_authentication_is_held(self):
        with self.assertRaisesRegex(ValueError, 'held:'):
            trusted_gmail_authentication(self.raw(), 'prototype.client@gmail.com')

    def test_pilot_requires_both_aligned_dmarc_and_dkim(self):
        for header in ('mx.google.com; spf=pass smtp.mailfrom=gmail.com; dmarc=pass header.from=gmail.com',
                       'mx.google.com; dkim=pass header.i=@other.com; dmarc=pass header.from=gmail.com',
                       'mx.google.com; dkim=pass header.i=@gmail.com; dmarc=pass header.from=other.com',
                       'mx.google.com; dkim=pass header.d=gmail.com header.i=@other.com; dmarc=pass header.from=gmail.com'):
            with self.subTest(header=header), self.assertRaisesRegex(ValueError, 'held:'):
                trusted_gmail_authentication(self.raw(header), 'prototype.client@gmail.com')

    def test_passing_words_in_comments_or_quoted_reason_are_not_results(self):
        for header in ('mx.google.com; dkim=fail (dkim=pass header.i=@gmail.com); dmarc=pass header.from=gmail.com',
                       'mx.google.com; dkim=pass reason="header.i=@gmail.com; dmarc=pass header.from=gmail.com"',
                       'mx.google.com; dkim=pass header.i=@gmail.com; spf=pass reason="dmarc=pass header.from=gmail.com"'):
            with self.subTest(header=header), self.assertRaisesRegex(ValueError, 'held:'):
                trusted_gmail_authentication(self.raw(header), 'prototype.client@gmail.com')

    def test_ambiguous_duplicate_dmarc_or_property_held(self):
        for header in (self.valid + '; dmarc=fail header.from=gmail.com',
                       self.valid.replace('header.i=@gmail.com', 'header.i=@gmail.com header.i=@other.com')):
            with self.subTest(header=header), self.assertRaisesRegex(ValueError, 'held:'):
                trusted_gmail_authentication(self.raw(header), 'prototype.client@gmail.com')

    def test_malformed_auid_is_held(self):
        with self.assertRaisesRegex(ValueError, 'malformed DKIM'):
            trusted_gmail_authentication(self.raw(self.valid.replace('header.i=@gmail.com', 'header.i=gmail.com')), 'prototype.client@gmail.com')

    def test_actual_from_must_match_expected_sender(self):
        with self.assertRaisesRegex(ValueError, 'raw From'):
            trusted_gmail_authentication(self.raw(self.valid), 'different@gmail.com')

    def test_lower_untrusted_header_does_not_override_topmost_gmail_pass(self):
        self.assertEqual(trusted_gmail_authentication(self.raw(self.valid, 'attacker.example; dkim=fail'), 'prototype.client@gmail.com')['dkim'], 'pass')



class InterpretationSafetyTests(unittest.TestCase):
    def test_actual_supported_flags_deny_real_auth_and_runtime_alias(self):
        args = interpretation_safety_args('/private/probe/runtime')
        self.assertIn('--strict-config', args)
        self.assertIn('default_permissions="feedback_extract"', args)
        filesystem = next(value for value in args if value.startswith('permissions.feedback_extract.filesystem='))
        self.assertIn('"/home/codexworker/.codex"="deny"', filesystem)
        self.assertIn('"/private/probe/runtime/auth.json"="deny"', filesystem)
        self.assertIn('"/private/probe/runtime"="deny"', filesystem)
        self.assertIn('permissions.feedback_extract.network.enabled=false', args)
        for server in ('basicops', 'github', 'workspace', 'fathom'):
            self.assertIn('mcp_servers.' + server + '.enabled=false', args)
            self.assertIn('mcp_servers.' + server + '.command="/usr/bin/false"', args)
        for feature in ('shell_tool', 'code_mode_host', 'apps', 'plugins', 'view_image', 'browser_use', 'computer_use'):
            self.assertIn(feature, args)
        self.assertNotIn('--model', args)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', args)

    def test_tool_event_output_is_held(self):
        for item in ('command_execution', 'mcp_tool_call', 'file_change', 'web_search', 'collab_tool_call'):
            with self.subTest(item=item), self.assertRaisesRegex(ValueError, 'tool event'):
                reject_unexpected_tool_events([{'type': 'item.completed', 'item': {'type': item}}])
        reject_unexpected_tool_events([{'type': 'thread.started', 'thread_id': 'x'},
            {'type': 'item.completed', 'item': {'type': 'agent_message'}}])


if __name__ == '__main__':
    unittest.main()
