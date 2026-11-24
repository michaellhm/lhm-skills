#!/usr/bin/env python3
"""Credential-free MCP facade for the task-bound host close-out broker."""
import json
import os
from pathlib import Path
import re
import socket
import sys

SOCKET = '/run/lhm-task-closeout/broker.sock'
REQUEST = re.compile(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*')
TOOLS = [
    {'name': 'get_closeout_context', 'description': 'Read this task’s live verified client/task binding and close-out receipts. No mutation.',
     'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}},
    *[{'name': name, 'description': description,
       'inputSchema': {'type': 'object', 'properties': {'draft_name': {'type': 'string', 'description': 'A Markdown filename directly inside this task’s drafts/ folder.'}},
                       'required': ['draft_name'], 'additionalProperties': False}}
      for name, description in [
          ('post_basicops_closeout', 'Post a prepared Markdown draft once to THIS existing BasicOps task, with readback. Leaves status and assignee unchanged. Call only when posting is authorised.'),
          ('write_knowledge_closeout', 'Create or verify an immutable close-out note under THIS registered client’s Task Close-outs folder in shared knowledge. No sync-directory access or overwrite. Call only when the knowledge write is authorised.')]]]


def session_id():
    pid = os.getppid()
    for _ in range(12):
        try:
            args = Path(f'/proc/{pid}/cmdline').read_bytes().decode().split('\0')
            for flag in ('--session-id', '--resume'):
                if flag in args:
                    value = args[args.index(flag) + 1]
                    if re.fullmatch(r'[0-9a-f-]{36}', value):
                        return value
            fields = Path(f'/proc/{pid}/status').read_text().splitlines()
            pid = int(next(line.split()[1] for line in fields if line.startswith('PPid:')))
            if pid <= 1:
                break
        except (OSError, ValueError, IndexError, StopIteration):
            break
    return None


def request_id():
    if len(sys.argv) == 2 and REQUEST.fullmatch(sys.argv[1]):
        return sys.argv[1]
    session = session_id()
    matches = []
    for run in Path('/var/lib/lhm-task-router').glob('ted-route-*'):
        try:
            receipt = json.loads((run / 'receipt.json').read_text())
            if session and receipt.get('thread_id') == session and REQUEST.fullmatch(run.name):
                matches.append(run.name)
        except (OSError, ValueError):
            continue
    if len(matches) != 1:
        raise ValueError('Cannot bind this Claude session to exactly one router task; resume through the task router.')
    return matches[0]


def call_broker(name, arguments, ident=None):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(150)
        connection.connect(SOCKET)
        connection.sendall((json.dumps({'request_id': ident or request_id(), 'operation': name, 'arguments': arguments}) + '\n').encode())
        with connection.makefile('rb') as stream:
            raw = stream.readline(131073)
        if len(raw) > 131072 or not raw.endswith(b'\n'):
            raise ValueError('Invalid host receipt')
        result = json.loads(raw)
        if result.get('error'):
            raise ValueError(result['error'])
        return result['result']


def dispatch(message):
    method = message.get('method')
    if method == 'initialize':
        version = message.get('params', {}).get('protocolVersion')
        return {'protocolVersion': version if version in {'2024-11-05', '2025-03-26', '2025-06-18'} else '2024-11-05',
                'capabilities': {'tools': {}}, 'serverInfo': {'name': 'LHMCloseout', 'version': '1.0.0'}}
    if method == 'ping':
        return {}
    if method == 'tools/list':
        return {'tools': TOOLS}
    if method == 'tools/call':
        params = message.get('params', {})
        try:
            if params.get('name') not in {tool['name'] for tool in TOOLS}:
                raise ValueError('Unsupported close-out tool')
            result = call_broker(params['name'], params.get('arguments', {}))
            return {'content': [{'type': 'text', 'text': json.dumps(result)}]}
        except Exception as exc:
            return {'isError': True, 'content': [{'type': 'text', 'text': str(exc)}]}
    raise ValueError('Method not found')


def main():
    for raw in sys.stdin.buffer:
        if len(raw) > 65536:
            return
        try:
            message = json.loads(raw)
            if 'id' not in message:
                continue
            try:
                response = {'jsonrpc': '2.0', 'id': message['id'], 'result': dispatch(message)}
            except ValueError:
                response = {'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32601, 'message': 'Method not found'}}
            print(json.dumps(response), flush=True)
        except (ValueError, TypeError):
            return


if __name__ == '__main__':
    main()
