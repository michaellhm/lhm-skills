"""Read-only Workspace Gmail transport and bounded raw MIME materialisation.

Uses the worker's existing OAuth/MCP configuration. This does not extract a
revision checklist, visually approve images, enqueue work or send email.
"""
import argparse
import asyncio
import hashlib
import json
import os
import re
import stat
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr
from pathlib import Path

ATTACHMENTS_ROOT = Path('/home/codexworker/.workspace-mcp/attachments')
CONFIG = Path('/home/codexworker/.codex/config.toml')
MAX_EML = 10 * 1024 * 1024
READ_TOOLS = frozenset(('search_gmail_messages', 'get_gmail_message_content',
                       'get_gmail_attachment_content', 'get_gmail_thread_content'))
COMMAND = '/opt/lhm-workspace-mcp/bin/workspace-mcp'
ARGS = ['--single-user', '--permissions', 'gmail:readonly', '--tool-tier', 'extended']
EXISTING_ARGS = ['--single-user', '--permissions', 'drive:full', 'docs:full',
                 'gmail:readonly+drafts+send', '--tool-tier', 'extended']


def read_saved_eml(text, *, attachments_root=ATTACHMENTS_ROOT):
    """Read one tool-produced .eml beneath a trusted root using no-follow opens."""
    matches = re.findall(r'^(?:📎 )?Saved to:\s*([^\r\n]+)\s*$', text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('expected one complete Saved to raw MIME path')
    path = Path(matches[0].strip())
    root = Path(attachments_root)
    if not path.is_absolute() or '..' in path.parts or path.suffix.lower() != '.eml':
        raise ValueError('invalid raw MIME path')
    try:
        parts = path.relative_to(root).parts
    except ValueError as exc:
        raise ValueError('raw MIME path outside private attachments root') from exc
    if not parts:
        raise ValueError('missing raw MIME filename')
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_EML:
                raise ValueError('raw MIME must be a non-empty regular file no larger than 10 MB')
            data = stream.read(MAX_EML + 1)
            after = os.fstat(stream.fileno())
            if len(data) != before.st_size or (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
                raise ValueError('raw MIME changed or was truncated during read')
            return data
    finally:
        os.close(directory)


def _private_write(root, name, data):
    """Write immutable bytes beneath a private, service-owned output directory."""
    root = Path(root)
    if root.is_symlink():
        raise ValueError('output root may not be a symlink')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = root.stat()
    if info.st_mode & 0o077 or info.st_uid != os.geteuid():
        raise ValueError('output root must be private and owned by this worker')
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
        except FileExistsError:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            with os.fdopen(fd, 'rb') as stream:
                info = os.fstat(stream.fileno())
                if (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077
                        or info.st_uid != os.geteuid() or info.st_size != len(data)
                        or stream.read(len(data) + 1) != data):
                    raise ValueError('materialised file conflicts with existing private bytes')
        else:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.fsync(directory)
    finally:
        os.close(directory)
    return str(root / name)


def parse_raw_mime(raw, *, message_id, account, image_root):
    """Return full body and attachments, explicitly pending visual/extraction review."""
    if not re.fullmatch(r'[a-f0-9]{8,64}', message_id):
        raise ValueError('invalid Gmail message ID')
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_EML:
        raise ValueError('raw MIME missing or exceeds 10 MB')
    message = BytesParser(policy=policy.default).parsebytes(raw)
    if any(part.defects for part in message.walk()):
        raise ValueError('malformed or truncated MIME')
    if len(message.get_all('From', [])) != 1 or len(message.get_all('Date', [])) != 1:
        raise ValueError('unambiguous sender and timestamp required')
    sender = parseaddr(str(message['From']))[1].lower()
    if not sender:
        raise ValueError('missing sender')
    try:
        when = parsedate_to_datetime(str(message['Date']))
    except (ValueError, TypeError) as exc:
        raise ValueError('invalid message timestamp') from exc
    if when.tzinfo is None:
        raise ValueError('message timestamp needs timezone')
    texts, html, attachments = [], [], []
    cids = set()
    for index, part in enumerate(message.walk()):
        if part.is_multipart():
            continue
        data = part.get_payload(decode=True)
        # Some transfer defects are recorded only when the payload is decoded.
        if part.defects or not isinstance(data, bytes):
            raise ValueError('invalid MIME transfer encoding')
        mime = part.get_content_type()
        filename = part.get_filename()
        disposition = part.get_content_disposition()
        if mime in ('text/plain', 'text/html') and disposition != 'attachment' and not filename:
            try:
                text = data.decode(part.get_content_charset() or 'utf-8', errors='strict')
            except (UnicodeError, LookupError) as exc:
                raise ValueError('message body cannot be decoded completely') from exc
            (texts if mime == 'text/plain' else html).append(text)
            continue
        cid = str(part.get('Content-ID', '')).strip().strip('<>')
        if cid and cid in cids:
            raise ValueError('ambiguous duplicate Content-ID')
        if cid:
            cids.add(cid)
        if not data:
            raise ValueError('empty MIME attachment')
        sha = hashlib.sha256(data).hexdigest()
        identity = hashlib.sha256((account + ':' + message_id + ':' + str(index)).encode()).hexdigest()
        private_ref = _private_write(image_root, identity, data)
        attachments.append({'part_id': str(index), 'content_id': cid or None,
            'filename': filename, 'mime_type': mime, 'disposition': disposition,
            'size_bytes': len(data), 'sha256': sha, 'private_ref': private_ref,
            'status': 'materialised', 'visually_reviewed': False})
    if not texts and not html:
        raise ValueError('message body missing')
    return {'account': account, 'message_id': message_id, 'sender': sender,
        'received_at': when.isoformat(), 'subject': str(message.get('Subject', '')),
        'rfc_message_id': str(message.get('Message-ID', '')),
        'body_text': '\n'.join(texts), 'body_html': '\n'.join(html),
        'raw_sha256': hashlib.sha256(raw).hexdigest(), 'attachments': attachments,
        'state': 'prepared', 'extraction_reviewed': False}


class WorkspaceGmail:
    """Lazy native MCP client restricted to the four Gmail read tool names."""
    def __init__(self, config=CONFIG):
        self.config = Path(config)

    @staticmethod
    def validate_tool(name):
        if name not in READ_TOOLS:
            raise ValueError('only Gmail read tools are permitted')

    def parameters(self):
        import tomllib
        config = tomllib.loads(self.config.read_text())
        server = config['mcp_servers']['workspace']
        if server.get('command') != COMMAND or server.get('args') not in (ARGS, EXISTING_ARGS):
            raise ValueError('Workspace route differs from the verified Gmail read-only configuration')
        env = server.get('env', {})
        if not isinstance(env, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in env.items()):
            raise ValueError('invalid Workspace MCP environment')
        return {'command': COMMAND, 'args': list(ARGS), 'env': {**os.environ, **env}}

    async def call(self, name, arguments):
        self.validate_tool(name)
        # Avoid requiring the SDK for parsing and deterministic tests.
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(**self.parameters())
        # Connector stderr may contain private account diagnostics. Keep it out of
        # shared output; the existing worker service retains its own private logs.
        with open(os.devnull, 'w') as private_stderr:
            async with stdio_client(params, errlog=private_stderr) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    catalog = await session.list_tools()
                    tool = next((tool for tool in catalog.tools if tool.name == name), None)
                    if tool is None:
                        raise ValueError('required Gmail read tool is unavailable')
                    # Native tool metadata uses input_schema in the installed runtime.
                    schema = getattr(tool, 'input_schema', None) or getattr(tool, 'inputSchema', None)
                    if not isinstance(schema, dict):
                        raise ValueError('Gmail tool has no readable input schema')
                    if any(key not in arguments for key in schema.get('required', [])):
                        raise ValueError('missing required Gmail read arguments')
                    result = await session.call_tool(name, arguments)
                    if getattr(result, 'is_error', False) or getattr(result, 'isError', False):
                        raise RuntimeError('Workspace Gmail read failed; inspect its private service logs')
                    return '\n'.join(block.text for block in result.content if getattr(block, 'type', None) == 'text')

    async def read_one(self, message_id, account, image_root, *, attachments_root=ATTACHMENTS_ROOT):
        text = await self.call('get_gmail_message_content', {
            'message_id': message_id, 'user_google_email': account, 'body_format': 'raw', 'full': True})
        raw = read_saved_eml(text, attachments_root=attachments_root)
        return parse_raw_mime(raw, message_id=message_id, account=account, image_root=image_root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['read-one'])
    parser.add_argument('--message-id', required=True)
    parser.add_argument('--account', required=True)
    parser.add_argument('--image-root', required=True)
    parser.add_argument('--output-root', required=True)
    args = parser.parse_args()
    packet = asyncio.run(WorkspaceGmail().read_one(args.message_id, args.account, args.image_root))
    name = hashlib.sha256((args.account + ':' + args.message_id).encode()).hexdigest() + '.json'
    path = _private_write(args.output_root, name, (json.dumps(packet, indent=2) + '\n').encode())
    # Never print connector config, OAuth state or the raw tool response.
    print(json.dumps({'state': 'prepared', 'packet': path, 'attachment_count': len(packet['attachments']),
                      'extraction_reviewed': False}))


if __name__ == '__main__':
    main()
