#!/usr/bin/env python3
"""Bounded, deterministic Fathom read through the existing Codexworker MCP login."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit


CONFIG = Path('/home/codexworker/.codex/config.toml')
READ_TOOLS = {'list_meetings', 'get_meeting_transcript'}
GENERIC = {'website', 'onboarding', 'meeting', 'with', 'and', 'the', 'for', 'client',
           'strategy', 'call', 'introduction', 'intro', 'lhm', 'local', 'health', 'marketing'}
MAX_TRANSCRIPT = 120000


class SourceUnavailable(Exception):
    pass


def tokens(value):
    return set(re.findall(r'[^\W_]+', str(value).casefold(), flags=re.UNICODE))


def instant(value):
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Meeting start requires timezone')
    return parsed.astimezone(timezone.utc)


def source_url(value):
    parsed = urlsplit(str(value))
    if (parsed.scheme != 'https' or parsed.hostname not in {'fathom.video', 'www.fathom.video'}
            or parsed.username or parsed.password or parsed.port not in {None, 443}
            or not parsed.path.startswith(('/calls/', '/share/')) or len(value) > 2048):
        raise SourceUnavailable('Invalid Fathom source link')
    return value


class NativeFathom:
    """MCP stdio only; OAuth credentials stay in the existing provider-owned store."""
    def __init__(self, config=CONFIG, timeout=140):
        import tomllib
        settings = tomllib.loads(config.read_text())['mcp_servers']['fathom']
        command = settings.get('command')
        arguments = settings.get('args', [])
        if not isinstance(command, str) or not Path(command).is_absolute():
            raise SourceUnavailable('Registered Fathom command unavailable')
        if not isinstance(arguments, list) or not all(isinstance(x, str) for x in arguments):
            raise SourceUnavailable('Registered Fathom arguments invalid')
        environment = dict(os.environ)
        environment.update(settings.get('env', {}))
        environment['HOME'] = '/home/codexworker'
        # An expired login is an unavailable source, never an unattended browser invitation.
        environment['BROWSER'] = '/bin/false'
        self.process = subprocess.Popen([command, *arguments], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=environment,
            start_new_session=True)
        self.buffer = b''
        self.number = 0
        self.deadline = time.monotonic() + timeout
        try:
            self.rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                'clientInfo': {'name': 'lhm_calendar_handover_read', 'version': '1'}})
            self.send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
            listing = self.rpc('tools/list', {})
            discovered = {row.get('name') for row in listing.get('tools', [])}
            if not READ_TOOLS.issubset(discovered) or listing.get('nextCursor'):
                raise SourceUnavailable('Required Fathom read tools unavailable')
        except Exception:
            self.close()
            raise

    def send(self, message):
        self.process.stdin.write((json.dumps(message) + '\n').encode())
        self.process.stdin.flush()

    def rpc(self, method, params):
        self.number += 1
        number = self.number
        self.send({'jsonrpc': '2.0', 'id': number, 'method': method, 'params': params})
        deadline = min(self.deadline, time.monotonic() + 50)
        while time.monotonic() < deadline:
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                try:
                    response = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(response, dict):
                    continue
                if 'method' in response and 'id' in response:
                    self.send({'jsonrpc': '2.0', 'id': response['id'],
                        'error': {'code': -32601, 'message': 'Read-only unattended client'}})
                    continue
                if response.get('id') == number:
                    if 'error' in response:
                        raise SourceUnavailable('Fathom RPC unavailable')
                    return response.get('result', {})
                continue
            readable, _, _ = select.select([self.process.stdout], [], [], 1)
            if readable:
                part = os.read(self.process.stdout.fileno(), 65536)
                if not part:
                    raise SourceUnavailable('Fathom connection closed')
                self.buffer += part
                if len(self.buffer) > 4 * 1024 * 1024:
                    raise SourceUnavailable('Fathom response exceeds bound')
        raise SourceUnavailable('Fathom request timed out')

    def call(self, name, arguments):
        if name not in READ_TOOLS:
            raise SourceUnavailable('Unapproved MCP operation')
        result = self.rpc('tools/call', {'name': name, 'arguments': arguments})
        if not isinstance(result, dict) or result.get('isError'):
            raise SourceUnavailable('Fathom tool unavailable')
        text = '\n'.join(block['text'] for block in result.get('content', [])
                         if block.get('type') == 'text' and isinstance(block.get('text'), str))
        if not text.strip():
            raise SourceUnavailable('Fathom returned no readable evidence')
        return text

    def close(self):
        process = getattr(self, 'process', None)
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=3)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=3)


def parse_meetings(text):
    """Parse the deployed Fathom connector's compact list, failing on incomplete pages."""
    try:
        structured = json.loads(text)
    except json.JSONDecodeError:
        structured = None
    if isinstance(structured, dict):
        if any(structured.get(key) for key in ['next_cursor', 'nextCursor', 'has_more', 'truncated']):
            raise SourceUnavailable('Meeting pagination incomplete')
        rows = structured.get('meetings', structured.get('items', structured.get('data')))
        if not isinstance(rows, list) or len(rows) > 100:
            raise SourceUnavailable('Unknown meeting-list shape')
        result = []
        for row in rows:
            result.append({'recording_id': row['recording_id'], 'title': row['title'],
                'date': row.get('date', row.get('recording_start_time', ''))[:10],
                'url': source_url(row['url']),
                'participants': ' '.join(str(x) for x in row.get('calendar_invitees', [])),
                'recorded_by': str(row.get('recorded_by', ''))})
        return result
    if re.search(r'next[_ ]?cursor|more meetings|next page|truncat', text, re.I):
        raise SourceUnavailable('Meeting pagination incomplete')
    count = re.search(r'^Found (\d+) meeting\(s\)\.', text)
    if not count:
        if re.fullmatch(r'\s*No meetings found\.?\s*', text, re.I):
            return []
        raise SourceUnavailable('Unknown meeting-list format')
    rows = []
    pattern = re.compile(r'^- (.+?) \| (\d{4}-\d{2}-\d{2}) \| id: (\d+) \| url: (\S+)'
                         r' \| recorded by (.*?) \| (.*)$')
    for line in text.splitlines():
        if line.startswith('- '):
            match = pattern.fullmatch(line)
            if not match:
                raise SourceUnavailable('Unparsed meeting metadata')
            title, date, identifier, url, recorder, participants = match.groups()
            rows.append({'recording_id': int(identifier), 'title': title, 'date': date,
                'url': source_url(url), 'recorded_by': recorder, 'participants': participants})
    if len(rows) != int(count.group(1)) or len(rows) > 100:
        raise SourceUnavailable('Meeting-list coverage incomplete')
    return rows


def internal_people(packet):
    """Exclude verified organiser/operator identities, not hard-coded staff names."""
    operator = packet.get('calendar_identity', '')
    if isinstance(operator, dict):
        operator = operator.get('email', '')
    operator = str(operator).strip().casefold()
    organiser = packet.get('organizer', '')
    if isinstance(organiser, dict):
        organiser = organiser.get('email', '')
    organiser = str(organiser).strip().casefold()
    addresses = {x for x in (operator, organiser) if '@' in x}
    domain = operator.split('@', 1)[1] if '@' in operator else None
    names = set()
    for address in addresses:
        names.update(tokens(address.split('@', 1)[0]))
    for person in packet.get('attendees', []):
        if not isinstance(person, dict):
            continue
        address = str(person.get('email', '')).strip().casefold()
        if address in addresses or (domain and address.endswith('@' + domain)):
            addresses.add(address)
            names.update(tokens(person.get('name', person.get('displayName', ''))))
            names.update(tokens(address.split('@', 1)[0]))
    return addresses, names


def participant_match(packet, row):
    evidence = str(row.get('participants', '')).casefold()
    evidence_tokens = tokens(evidence)
    internal_addresses, internal_names = internal_people(packet)
    for person in packet.get('attendees', []):
        if not isinstance(person, dict):
            continue
        address = str(person.get('email', '')).strip().casefold()
        if address in internal_addresses:
            continue
        name = tokens(person.get('name', person.get('displayName', '')))
        if address and re.search(r'(?<![\w.+-])' + re.escape(address) + r'(?![\w.-])', evidence):
            return 'invitee_email'
        if len(name) >= 2 and name.issubset(evidence_tokens):
            return 'invitee_name'
    # The compact connector may omit emails and Calendar may omit display names.
    # Preserve the weaker evidence explicitly rather than infer email ownership.
    named_in_title = (tokens(packet.get('summary', '')) - GENERIC - internal_names) & evidence_tokens
    if named_in_title:
        return 'title_named_invitee_only'
    return None


def title_match(packet, row):
    _, internal_names = internal_people(packet)
    expected = tokens(packet.get('summary', '')) - GENERIC - internal_names
    observed = tokens(row.get('title', '')) - GENERIC - internal_names
    if not expected or not observed:
        return False
    return bool(expected & observed) and len(expected & observed) / min(len(expected), len(observed)) >= 0.5


def collect(packet, client_factory=NativeFathom):
    start = instant(packet['start'])
    lower, upper = start - timedelta(hours=2), start + timedelta(hours=2)
    client = None
    base = {'source': 'existing_codexworker_fathom_mcp',
            'search_window': {'after': lower.isoformat(), 'before': upper.isoformat()},
            'pagination_bound': 3, 'attendance_proven_by_calendar': False}
    try:
        client = client_factory()
        listing = client.call('list_meetings', {'created_after': lower.isoformat(),
            'created_before': upper.isoformat(), 'max_pages': 3,
            'include_summary': False, 'include_action_items': False})
        rows = parse_meetings(listing)
        candidates = [(row, participant_match(packet, row)) for row in rows if title_match(packet, row)]
        candidates = [(row, match) for row, match in candidates if match]
        if not candidates:
            return {**base, 'status': 'not_ready', 'reason': 'No uniquely matched recording available yet',
                    'inspected_meetings': len(rows), 'source_links': []}
        unique = {row['recording_id']: (row, match) for row, match in candidates}
        if len(unique) != 1:
            return {**base, 'status': 'ambiguous', 'reason': 'Multiple matching recordings; no transcript selected',
                    'matching_recordings': len(unique),
                    'source_links': [row['url'] for row, _ in unique.values()]}
        row, matching = next(iter(unique.values()))
        transcript = client.call('get_meeting_transcript',
            {'recording_id': row['recording_id'], 'url': row['url']})
        if len(transcript.strip()) < 100 or re.search(r'\b(transcript (?:is )?(?:not ready|unavailable|processing)|no transcript)\b', transcript[:500], re.I):
            return {**base, 'status': 'not_ready', 'reason': 'Matched recording transcript not available yet',
                    'recording_id': row['recording_id'], 'source_links': [row['url']]}
        transcript_bytes = transcript.encode('utf-8')
        truncated = len(transcript_bytes) > MAX_TRANSCRIPT
        if truncated:
            transcript = (transcript_bytes[:MAX_TRANSCRIPT // 2].decode('utf-8', errors='ignore')
                          + '\n[Bounded transcript: middle omitted.]\n'
                          + transcript_bytes[-MAX_TRANSCRIPT // 2:].decode('utf-8', errors='ignore'))
        return {**base, 'status': 'ready', 'recording_id': row['recording_id'],
                'meeting_title': row['title'], 'meeting_date': row['date'],
                'match_evidence': matching, 'source_links': [row['url']],
                'transcript': transcript, 'transcript_truncated': truncated,
                'coverage': 'One matched onboarding recording; separate sales/strategy sources still require research'}
    except Exception as exc:
        return {**base, 'status': 'unavailable', 'reason': 'Fathom source read did not complete',
                'error_type': type(exc).__name__, 'source_links': []}
    finally:
        if client is not None:
            client.close()


def main():
    try:
        if os.geteuid() != 10001:
            raise ValueError('Expected existing Codexworker connector identity')
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Event packet exceeds bound')
        packet = json.loads(raw)
        if not isinstance(packet, dict):
            raise ValueError('Expected event packet')
        result = collect(packet)
    except Exception as exc:
        result = {'status': 'unavailable', 'reason': 'Fathom read request invalid',
                  'error_type': type(exc).__name__, 'source_links': []}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
