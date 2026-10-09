#!/usr/bin/env python3
"""Receipt-gated snapshot and comment writer. No task-state or client messaging API."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import re
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo

_VAULT = None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def week_now():
    today = datetime.now(ZoneInfo('Australia/Melbourne')).date()
    return (today - timedelta(days=today.weekday())).isoformat()


def dependency(cfg, week):
    if date.fromisoformat(week).weekday() != 0:
        raise ValueError('Week must be a Monday')
    root = Path(cfg['report_state'])
    receipt = json.loads((root / 'receipts' / (week + '-brief.json')).read_text())
    archive = json.loads((root / 'archive' / (week + '.json')).read_text())
    if receipt.get('week') != week or receipt.get('kind') != 'brief' or receipt.get('state') != 'delivered' or not receipt.get('message_id') or receipt.get('recipients') != ['support@localhealthmarketing.com.au']:
        raise ValueError('Awaiting verified delivery')
    if archive.get('week') != week or archive.get('state') != 'archived' or not archive.get('file_id'):
        raise ValueError('Awaiting verified shared archive')
    run = root / 'runs' / archive.get('run', week)
    email = json.loads((run / 'email.json').read_text())
    if receipt.get('content_sha256') != digest(email):
        raise ValueError('Delivered report hash mismatch')
    brief = json.loads((run / 'brief.json').read_text())
    if brief.get('week') != week:
        raise ValueError('Report week mismatch')
    access = json.loads((run / 'access-receipt.json').read_text())
    research = json.loads((run / 'research-receipt.json').read_text())
    for source in ['gmail', 'obsidian', 'basicops']:
        if access.get('sources', {}).get(source, {}).get('status') != 'passed' or research.get('coverage', {}).get(source, {}).get('status') != 'complete':
            raise ValueError('Incomplete source coverage: ' + source)
    if research.get('material_gaps') != [] or research.get('coverage', {}).get('meetings', {}).get('status') not in ['complete', 'not_required']:
        raise ValueError('Report has unresolved core coverage')
    return {'week': week, 'report': brief, 'archive': archive, 'access': access, 'delivery_message_id': receipt['message_id']}


def unwrap(result):
    if result.get('isError'):
        raise RuntimeError('BasicOps tool failed')
    for block in result.get('content', []):
        if block.get('type') == 'text':
            return json.loads(block['text'])
    raise ValueError('Missing structured BasicOps response')


class BasicOps:
    def __init__(self, cfg):
        from dotenv import load_dotenv
        for env in cfg['env_files']:
            load_dotenv(env, override=False)
        if not os.environ.get('MCP_BASICOPS_API_KEY') or os.environ['MCP_BASICOPS_API_KEY'].startswith('$'):
            raise ValueError('Unresolved BasicOps credential')
        spec = importlib.util.spec_from_file_location('lily_proxy', cfg['proxy'])
        self.proxy = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.proxy)

    def call(self, name, args):
        return unwrap(self.proxy._rpc('tools/call', {'name': name, 'arguments': args}))

    def identity(self):
        if self.call('get_current_user', {}).get('id') != 82484:
            raise ValueError('Writer must authenticate as Lily 82484')

    def pages(self, name, args):
        rows, seen = [], set()
        for _ in range(100):
            result = self.call(name, dict(args, limit=100))
            if isinstance(result, list):
                rows.extend(result); return rows
            data = result.get('data')
            if not isinstance(data, list):
                raise ValueError('Unexpected pagination response')
            rows.extend(data)
            cursor = result.get('nextPage')
            if not cursor:
                return rows
            if cursor in seen:
                raise ValueError('Repeated pagination cursor')
            seen.add(cursor); args = dict(args, nextPage=cursor)
        raise ValueError('Pagination incomplete')


def discussions(api, task):
    messages = api.pages('list_messages_in_task', {'taskId': task})
    for message in messages:
        # Replies can contain the completion, correction or approval itself.
        result = api.call('list_replies_in_message', {'messageId': message['id']})
        message['loop_replies'] = result if isinstance(result, list) else result.get('data', [])
        if isinstance(result, dict) and result.get('nextPage'):
            raise ValueError('Reply coverage incomplete')
    return messages


def context(cfg, task_id):
    """Only explicit operator-reviewed mappings are writable, never fuzzy matches."""
    mapping = cfg.get('projects', {}).get(str(task_id))
    if not mapping:
        raise ValueError('Canonical overview mapping needs Kristalyn review')
    if cfg.get('vault_backend') == 'shared-drive':
        from shared_vault import Vault
        global _VAULT
        if _VAULT is None: _VAULT = Vault(cfg)
        return {key:_VAULT.read(mapping[key]) for key in ['profile','project']}
    root = Path(cfg['vault']).resolve()
    out = {}
    for key in ['profile', 'project']:
        path = (root / mapping[key]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or out-of-vault canonical ' + key)
        out[key] = {'path': mapping[key], 'text': path.read_text()}
    return out


def prepare(cfg, api, week):
    dep = dependency(cfg, week); api.identity()
    verify_archive(cfg, dep)
    tasks, boards = {}, {}
    for board in [68635, 68921]:
        rows = api.pages('list_tasks_in_project', {'projectId': board})
        boards[str(board)] = len(rows)
        for task in rows:
            if task.get('status') not in ['Complete', 'Cancelled', 'Decline'] and not task.get('archived'):
                tasks[str(task['id'])] = task
    for task_id in cfg.get('test_task_ids', []):
        tasks[str(task_id)] = api.call('get_task', {'taskId': task_id})
    snapshots, blocked = {}, []
    for task_id, task in tasks.items():
        try:
            ctx = context(cfg, task_id)
            current = api.call('get_task', {'taskId': int(task_id)})
            messages = discussions(api, int(task_id))
            snapshots[task_id] = {'task': current, 'context': ctx, 'messages': messages}
        except ValueError as error:
            blocked.append({'task_id': task_id, 'title': task.get('title'), 'reason': str(error)})
    snap = {'week': week, 'dependency': dep, 'boards': boards, 'projects': snapshots, 'blocked': blocked}
    snap['sha256'] = digest(snap)
    save(Path(cfg['state']) / week / 'snapshot.json', snap)
    return snap


def apply(cfg, api, week, plan):
    dep = dependency(cfg, week); api.identity(); verify_archive(cfg, dep)
    root = Path(cfg['state']) / week
    snap = json.loads((root / 'snapshot.json').read_text())
    if plan.get('snapshot_sha256') != snap.get('sha256'):
        raise ValueError('Plan is not bound to current snapshot')
    entries = plan.get('summaries', [])
    ids = [str(item['task_id']) for item in entries]
    if len(ids) != len(set(ids)) or any(t not in snap['projects'] for t in ids):
        raise ValueError('Duplicate or unmapped target')
    result = {'week': week, 'items': [], 'blocked': plan.get('blocked', [])}
    for item in entries:
        tid = str(item['task_id']); original = snap['projects'][tid]
        task = api.call('get_task', {'taskId': int(tid)})
        board = task.get('project', {}).get('id')
        marker = 'lily-weekly:' + week + ':' + str(board) + ':' + tid
        existing = discussions(api, int(tid))
        found = [m for m in existing if marker in json.dumps(m)]
        if found:
            result['items'].append({'task_id': tid, 'state': 'already_present', 'marker': marker}); continue
        receipt = root / ('task-' + tid + '.json')
        if receipt.exists() and json.loads(receipt.read_text()).get('state') == 'posting':
            result['items'].append({'task_id': tid, 'state': 'blocked_uncertain_post'}); continue
        current = {'task': task, 'context': context(cfg, tid), 'messages': existing}
        if digest(current) != digest(original):
            result['items'].append({'task_id': tid, 'state': 'blocked_changed_evidence'}); continue
        if board not in [68635, 68921] and int(tid) not in cfg.get('test_task_ids', []):
            raise ValueError('Target no longer on approved board')
        message = item.get('message', '').strip()
        if not message or len(message) > 12000:
            raise ValueError('Missing or oversized summary')
        message += '\n\n' + marker
        save(receipt, {'state': 'posting', 'marker': marker, 'message_sha256': digest(message)})
        try:
            api.call('create_message_in_task', {'taskId': int(tid), 'message': message})
            observed = discussions(api, int(tid))
            if not any(marker in json.dumps(m) for m in observed):
                raise ValueError('Post readback not found')
            save(receipt, {'state': 'verified', 'marker': marker})
            result['items'].append({'task_id': tid, 'state': 'posted_verified', 'marker': marker})
        except Exception:
            result['items'].append({'task_id': tid, 'state': 'blocked_uncertain_post'})
    save(root / 'result.json', result)
    return result


def verify_archive(cfg, dep):
    spec = importlib.util.spec_from_file_location('google_api', cfg['google_api'])
    google = importlib.util.module_from_spec(spec); spec.loader.exec_module(google)
    text = google.build_service('drive', 'v3').files().get_media(fileId=dep['archive']['file_id'], supportsAllDrives=True).execute().decode('utf-8-sig')
    marker = re.search(r'<!-- weekly-web-snapshot-sha256:([a-f0-9]{64}) -->', text)
    if dep['week'] not in text or dep['delivery_message_id'] not in text or not marker or hashlib.sha256(text[:marker.start()].encode()).hexdigest() != marker.group(1):
        raise ValueError('Shared archive readback does not match week')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['monitor', 'prepare', 'apply', 'complete'])
    parser.add_argument('--config', default='/opt/data/profiles/lhm_project_manager/website-loop.json')
    parser.add_argument('--plan'); parser.add_argument('--week')
    parser.add_argument('--task', type=int); parser.add_argument('--item'); parser.add_argument('--date')
    parser.add_argument('--evidence'); parser.add_argument('--source'); parser.add_argument('--actor')
    args = parser.parse_args(); cfg = json.loads(Path(args.config).read_text()); week = args.week or week_now()
    if args.mode == 'monitor':
        if datetime.now(ZoneInfo('Australia/Melbourne')).weekday() != 0:
            print('outside-monday'); return
        try:
            dependency(cfg, week)
            print(json.dumps({'week': week, 'ready': True, 'revision': cfg.get('revision')}))
        except (OSError, ValueError, KeyError):
            print('awaiting-verified-report')
        return
    state = Path(cfg['state']); state.mkdir(parents=True, exist_ok=True)
    with (state / 'writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        api = BasicOps(cfg)
        if args.mode == 'complete':
            from shared_vault import Vault, complete
            api.identity()
            record = context(cfg, str(args.task))
            # Read the current task and full discussion before touching its note.
            api.call('get_task', {'taskId':args.task}); discussions(api,args.task)
            print(json.dumps(complete(Vault(cfg),record['project']['path'],args.item,args.date,args.evidence,args.source,args.actor)))
        elif args.mode == 'prepare':
            snap = prepare(cfg, api, week)
            print(json.dumps({'snapshot': str(state / week / 'snapshot.json'), 'sha256': snap['sha256'], 'mapped': len(snap['projects']), 'blocked': len(snap['blocked'])}))
        else:
            print(json.dumps(apply(cfg, api, week, json.loads(Path(args.plan).read_text()))))


if __name__ == '__main__':
    main()
