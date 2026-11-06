"""Feedback adapters. Connector callables must be bound by the authenticated host.

No credentials, shell commands, model prompts or worker authority are inferred here.
An unknown remote write is reconciled, never automatically replayed.
"""
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from email.utils import parseaddr
from pathlib import Path


class ReconcileRequired(RuntimeError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Effects:
    """Durable intent before remote mutation; safe across process death and timeouts."""
    def __init__(self, path):
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute('CREATE TABLE IF NOT EXISTS effects (key TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT)')

    def perform(self, key, payload, lookup, write, verify):
        fingerprint = digest(payload)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.db.execute('SELECT digest,state,receipt FROM effects WHERE key=?', (key,)).fetchone()
            if row and row[0] != fingerprint:
                raise ReconcileRequired('intent changed')
            fresh = row is None
            if fresh:
                self.db.execute('INSERT INTO effects VALUES (?,?,?,NULL)', (key, fingerprint, 'uncertain'))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        if row and row[1] == 'verified':
            receipt = json.loads(row[2])
            if not verify(receipt):
                raise ReconcileRequired('saved remote receipt no longer matches')
            return receipt
        # lookup must enumerate all remote pages and reject ambiguous matches.
        receipt = lookup()
        if receipt is None:
            if not fresh:
                raise ReconcileRequired('remote outcome unknown; do not repeat write')
            receipt = write()
        if not verify(receipt):
            raise ReconcileRequired('remote readback failed')
        self.db.execute('UPDATE effects SET state=?,receipt=? WHERE key=?',
                        ('verified', json.dumps(receipt, sort_keys=True), key))
        return receipt


def pages(call, name, args):
    seen = set()
    while True:
        result = call(name, args)
        yield from result['data']
        cursor = result.get('nextPage')
        if not cursor:
            return
        if cursor in seen:
            raise ValueError('repeated pagination cursor')
        seen.add(cursor)
        args = dict(args, nextPage=cursor)


class BasicOps:
    def __init__(self, call, effects, stage_id):
        self.call, self.effects, self.stage_id = call, effects, stage_id

    def eligible(self, cockpit_id):
        task = self.call('get_task', {'taskId': int(cockpit_id)})
        return (task.get('project', {}).get('id') == 68635
                and task.get('section', {}).get('id') == self.stage_id
                and not task.get('archived') and task.get('status') not in ('Complete', 'Cancelled'))

    def task(self, batch, cockpit_id, payload):
        if not self.eligible(cockpit_id):
            raise ReconcileRequired('cockpit left Prototype Feedback')
        def lookup():
            candidates = [t for t in pages(self.call, 'list_tasks_in_project',
                {'projectId': payload['projectId'], 'limit': 100})
                if t['title'] == payload['title'] and t.get('description') == payload['description']]
            if len(candidates) > 1:
                raise ReconcileRequired('multiple possible revision tasks')
            return {'task_id': candidates[0]['id']} if candidates else None
        def write():
            if not self.eligible(cockpit_id):
                raise ReconcileRequired('stage changed before create')
            created = self.call('create_task', payload)
            return {'task_id': created['id']}
        def verify(receipt):
            task = self.call('get_task', {'taskId': receipt['task_id']})
            # Description is HTML after BasicOps save; host supplies canonical HTML.
            return (all(task.get(k) == payload[k] for k in ('title', 'description'))
                    and task.get('project', {}).get('id') == payload['projectId']
                    and task.get('section', {}).get('id') == payload['section']
                    and task.get('assignee', {}).get('id') == 82491 and bool(task.get('url')))
        if payload.get('assignee') != 82491:
            raise ValueError('verified Ted identity required')
        return self.effects.perform(batch + ':task', payload, lookup, write, verify)

    def discussion(self, batch, task_id, message):
        def lookup():
            found = [m for m in pages(self.call, 'list_messages_in_task', {'taskId': task_id, 'limit': 100})
                     if m.get('message') == message]
            if len(found) > 1:
                raise ReconcileRequired('ambiguous discussion receipt')
            return {'message_id': found[0]['id']} if found else None
        def write():
            result = self.call('create_message_in_task', {'taskId': task_id, 'message': message})
            return {'message_id': result['id']}
        def verify(receipt):
            return any(m['id'] == receipt['message_id'] and m.get('message') == message
                       for m in pages(self.call, 'list_messages_in_task', {'taskId': task_id, 'limit': 100}))
        return self.effects.perform(batch + ':brief', {'task': task_id, 'message': message}, lookup, write, verify)


class Gmail:
    def __init__(self, read_thread, read_bytes, private_root):
        self.read_thread, self.read_bytes = read_thread, read_bytes
        self.root = Path(private_root)
        if self.root.is_symlink():
            raise ValueError('private root must not be symlink')
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.root.stat().st_mode & 0o077:
            raise ValueError('private root permissions too broad')

    def intake(self, message, registration, extracted, *, related_thread=False):
        headers = {h['name'].lower(): h['value'] for h in message['payload'].get('headers', [])}
        sender = parseaddr(headers.get('from', ''))[1].lower()
        if sender not in registration['senders']:
            raise ValueError('unregistered sender')
        when = datetime.fromtimestamp(int(message['internal_date']) / 1000, timezone.utc)
        if when < datetime.fromisoformat(registration['review_start']):
            raise ValueError('message precedes review window')
        if message['thread_id'] not in registration['threads'] and related_thread is not True:
            raise ValueError('separate email needs verified same-prototype classification')
        images, texts = [], []
        def visit(part):
            mime, body = part.get('mime_type', ''), part.get('body', {})
            if mime == 'text/plain' and body.get('content'):
                texts.append(body['content'])
            elif mime == 'text/html' and body.get('content') and not texts:
                texts.append(body['content'])
            elif not mime.startswith('multipart/') and (body.get('attachment_id') or part.get('filename')):
                if part.get('read_attachment_supported') is not True:
                    raise ValueError('unsupported attachment; explicit review required')
                data = self.read_bytes(message['id'], body.get('attachment_id'), part.get('part_id'))
                if not isinstance(data, bytes) or not data or len(data) != body['size']:
                    raise ValueError('missing or truncated attachment')
                sha = hashlib.sha256(data).hexdigest()
                filename = hashlib.sha256((registration['account'] + ':' + message['id'] + ':' + part['part_id']).encode()).hexdigest()
                target = self.root / filename
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600) if not target.exists() else None
                if fd is not None:
                    with os.fdopen(fd, 'wb') as out:
                        out.write(data); out.flush(); os.fsync(out.fileno())
                if target.is_symlink() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                    raise ValueError('attachment storage conflict')
                ph = {h['name'].lower(): h['value'] for h in part.get('headers', [])}
                cid = ph.get('content-id', part['part_id']).strip('<>')
                context = extracted.get('image_context', {}).get(cid)
                if not context:
                    raise ValueError('attachment needs visual review and nearby context')
                images.append({'content_id': cid, 'private_ref': str(target), 'sha256': sha,
                               'context': context, 'status': 'verified'})
            for child in part.get('parts') or []:
                visit(child)
        visit(message['payload'])
        if not texts:
            raise ValueError('missing message text')
        # Extractor is trusted host logic; email text is never evaluated as authority.
        return dict(account=registration['account'], message_id=message['id'], thread_id=message['thread_id'],
                    site=registration['site'], cockpit_id=str(registration['cockpit_id']), sender=sender,
                    received_at=when.isoformat(), source_url=registration['mail_url'] + message['id'],
                    original_text='\n'.join(texts), items=extracted['items'], images=images)


class Ted:
    """Requires a host-bound delegated route; never uses human message impersonation."""
    def __init__(self, submit, status, effects, eligible):
        self.submit, self.status, self.effects, self.eligible = submit, status, effects, eligible

    def dispatch(self, batch, payload):
        if not self.eligible():
            raise ReconcileRequired('cockpit left Prototype Feedback')
        if payload.get('authority_kind') != 'registered-prototype-feedback':
            raise ValueError('bound system authority required')
        def lookup():
            return self.status(batch)
        def write():
            if not self.eligible():
                raise ReconcileRequired('stage changed before submit')
            return self.submit(batch, payload)
        def verify(receipt):
            remote = self.status(batch)
            identity = ('request_id', 'task_id', 'run_id', 'chat_url')
            return (isinstance(remote, dict) and isinstance(receipt, dict)
                    and all(remote.get(k) == receipt.get(k) for k in identity)
                    and receipt.get('request_id') == batch and receipt.get('task_id') == payload['task_id']
                    and bool(receipt.get('run_id')) and bool(receipt.get('chat_url'))
                    and remote.get('status') in ('accepted', 'running', 'ready_for_review'))
        return self.effects.perform(batch + ':dispatch', payload, lookup, write, verify)


class Completion:
    """Host-bound verification and notification; no execution or publication methods.

    Each callback reads its authoritative service. Worker-supplied receipts alone
    must never implement these callbacks. http_get returns actual response bytes.
    Notifications use an idempotent delivery key and a separate delivery receipt.
    """
    def __init__(self, queue, effects, observe, remote_commit, deployment, http_get,
                 handback, notification_lookup, notify, notification_verify):
        self.queue, self.effects = queue, effects
        self.observe, self.remote_commit, self.deployment = observe, remote_commit, deployment
        self.http_get, self.handback = http_get, handback
        self.notification_lookup, self.notify = notification_lookup, notify
        self.notification_verify = notification_verify

    def _batch(self, batch, owner):
        row = self.queue.db.execute('SELECT * FROM batches WHERE id=?', (batch,)).fetchone()
        if not row or row['owner'] != owner or not all(row[k] for k in ('task_id', 'run_id', 'chat_url')):
            raise ReconcileRequired('missing or conflicting authoritative batch identity')
        return dict(row)

    def ready(self, batch, *, owner, registration):
        import re
        row = self._batch(batch, owner)
        if row['state'] not in ('active', 'ready_for_review'):
            raise ReconcileRequired('batch is not active or ready for review')
        run = self.observe(row['run_id'])
        if (not isinstance(run, dict) or run.get('run_id') != row['run_id']
                or str(run.get('task_id')) != row['task_id'] or run.get('chat_url') != row['chat_url']
                or run.get('status') != 'succeeded'):
            raise ReconcileRequired('worker result missing, unfinished, failed or identity changed')
        commit, repository, branch = run.get('commit'), run.get('repository'), run.get('branch')
        if (not isinstance(commit, str) or not re.fullmatch('[a-f0-9]{40}', commit)
                or repository != registration['repository'] or branch != registration['branch']
                or run.get('preview_url') != registration['preview_url']):
            raise ReconcileRequired('published destination does not match registered prototype')
        checks, qa = run.get('checks', {}), run.get('independent_qa', {})
        if (checks.get('desktop') is not True or checks.get('mobile') is not True
                or qa.get('status') != 'passed' or qa.get('commit') != commit
                or not run.get('worker_identity') or not qa.get('reviewer') or qa.get('reviewer') == run.get('worker_identity')
                or not re.fullmatch('[a-f0-9]{64}', str(qa.get('package_sha256', '')))):
            raise ReconcileRequired('desktop, mobile and independent exact-commit QA required')
        if self.remote_commit(repository, branch) != commit:
            raise ReconcileRequired('remote commit readback mismatch')
        deployment = self.deployment(repository, commit)
        if (not isinstance(deployment, dict) or deployment.get('commit') != commit
                or deployment.get('conclusion') != 'success'
                or deployment.get('workflow') != 'Deploy to lhmstaging' or not deployment.get('id')):
            raise ReconcileRequired('successful exact-commit deployment required')
        response = self.http_get(registration['preview_url'])
        body = response.get('body') if isinstance(response, dict) else None
        if (not isinstance(body, bytes) or not body.strip() or response.get('status') != 200
                or hashlib.sha256(body).hexdigest() != run.get('content_sha256')):
            raise ReconcileRequired('non-empty HTTP 200 preview content readback mismatch')
        handback = self.handback(row['task_id'])
        expected = {'task_id': row['task_id'], 'run_id': row['run_id'], 'commit': commit,
                    'preview_url': registration['preview_url'], 'status': 'Under Review',
                    'reviewer_id': registration['reviewer_id']}
        if (not isinstance(handback, dict) or not handback.get('receipt_id')
                or any(str(handback.get(k)) != str(v) for k, v in expected.items())):
            raise ReconcileRequired('verified BasicOps review handback required')
        # Stable evidence survives a crash between checkpoint and queue transition.
        receipt = dict(expected, receipt_id=handback['receipt_id'], deployment_id=deployment['id'],
                       content_sha256=run['content_sha256'], qa_package_sha256=qa['package_sha256'])
        self.queue.checkpoint(batch, owner=owner, handback_receipt=json.dumps(receipt, sort_keys=True))
        self.queue.ready(batch, owner=owner, verified=True)
        return receipt

    def notification(self, batch, *, owner):
        row = self._batch(batch, owner)
        if row['state'] != 'ready_for_review' or not row['handback_receipt']:
            raise ReconcileRequired('review verification must precede notification')
        handback = json.loads(row['handback_receipt'])
        key = batch + ':ready-for-review'
        payload = {'task_id': row['task_id'], 'run_id': row['run_id'], 'reviewer_id': handback['reviewer_id'],
                   'preview_url': handback['preview_url'], 'commit': handback['commit']}
        def verify(receipt):
            return (isinstance(receipt, dict) and receipt.get('delivery_key') == key
                    and receipt.get('status') == 'delivered' and bool(receipt.get('receipt_id'))
                    and self.notification_verify(key, payload, receipt) is True)
        receipt = self.effects.perform(key, payload,
            lambda: self.notification_lookup(key), lambda: self.notify(key, payload), verify)
        self.queue.checkpoint(batch, owner=owner, notification_receipt=json.dumps(receipt, sort_keys=True))
        return receipt


class ScanLedger:
    """Record reviewed no-ops after host-verified sender, review window and routing.

    Holds IDs and a classification digest; never silently converts feedback into a
    no-op. Classifications are trusted extractor output, not email instructions.
    """
    def __init__(self, effects):
        self.db = effects.db
        self.db.execute('CREATE TABLE IF NOT EXISTS scan_noops (account TEXT NOT NULL, message_id TEXT NOT NULL, site TEXT NOT NULL, digest TEXT NOT NULL, PRIMARY KEY(account,message_id))')

    def record(self, message, registration, classification, *, related_thread=False):
        if classification.get('kind') not in ('acknowledgement', 'question', 'unrelated'):
            raise ValueError('feedback is not a no-op')
        if classification.get('reviewed') is not True or not classification.get('reason'):
            raise ValueError('reviewed classification and reason required')
        headers = {h['name'].lower(): h['value'] for h in message['payload'].get('headers', [])}
        sender = parseaddr(headers.get('from', ''))[1].lower()
        if sender not in registration['senders']:
            raise ValueError('unregistered sender')
        when = datetime.fromtimestamp(int(message['internal_date']) / 1000, timezone.utc)
        start = datetime.fromisoformat(registration['review_start'])
        if start.tzinfo is None or when < start:
            raise ValueError('message outside verified review window')
        if message['thread_id'] not in registration['threads'] and related_thread is not True:
            raise ValueError('unverified separate email')
        fingerprint = digest(classification)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior = self.db.execute('SELECT site,digest FROM scan_noops WHERE account=? AND message_id=?',
                (registration['account'], message['id'])).fetchone()
            if prior and tuple(prior) != (registration['site'], fingerprint):
                raise ReconcileRequired('no-op classification or site changed')
            if not prior:
                self.db.execute('INSERT INTO scan_noops VALUES (?,?,?,?)',
                    (registration['account'], message['id'], registration['site'], fingerprint))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        return 'existing' if prior else 'recorded'
