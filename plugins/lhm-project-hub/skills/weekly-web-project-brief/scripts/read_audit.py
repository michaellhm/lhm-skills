"""Controller-observed source completion times; never infer times from old logs."""
import json
import shlex
from datetime import datetime, timezone


def capture_events(lines, output, clock=None):
    clock = clock or (lambda: datetime.now(timezone.utc))
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            output.write(line)
        else:
            if event.get('type') == 'item.completed':
                event['controller_read_at'] = clock().isoformat()
            output.write(json.dumps(event) + '\n')
        output.flush()


def source_identity(item):
    if item.get('type') == 'mcp_tool_call':
        server = str(item.get('server', '')).lower()
        source = 'basicops' if 'basicops' in server else 'meetings' if 'fathom' in server else None
        if source:
            return source, item.get('tool'), item.get('arguments', {})
    if item.get('type') == 'command_execution':
        try:
            args = shlex.split(item.get('command', ''))
            if '-lc' in args:
                args = shlex.split(args[args.index('-lc') + 1])
        except (ValueError, IndexError):
            return None
        for index, arg in enumerate(args[:-1]):
            if arg.endswith('/source_read.py') or arg == 'source_read.py':
                action = args[index + 1]
                value = args[index + 2] if len(args) > index + 2 else ''
                source = ('gmail' if action in ('gmail-search', 'gmail-get') else
                          'meetings' if action == 'vault-read' and value.startswith('50 Meetings/') else
                          'obsidian' if action in ('vault-read', 'vault-list') else None)
                if source:
                    return source, action, value
    return None


def successful(item):
    if item.get('status') != 'completed':
        return False
    if item.get('type') == 'command_execution':
        return item.get('exit_code') == 0
    result = item.get('result')
    return not item.get('error') and result is not None and not (
        isinstance(result, dict) and (result.get('isError') or result.get('is_error')))


def precise_time(value):
    if not isinstance(value, str) or 'T' not in value:
        return False
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None
    except ValueError:
        return False


def read_entry(item, log_name, evidence):
    identity = source_identity(item)
    observed = item.get('controller_read_at')
    if not identity or not successful(item) or not precise_time(observed) or not item.get('id'):
        return None
    source, tool, target = identity
    return {'read_id': log_name + ':' + item['id'], 'source': source,
            'tool': tool, 'target': target, 'read_at': observed,
            'time_basis': 'controller_received_result', 'evidence': evidence,
            'record_id': item['id']}
