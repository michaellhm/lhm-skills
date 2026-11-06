"""Persistent intake queue. No network, model, task creation or worker dispatch."""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
from contextlib import contextmanager
from datetime import datetime


class Queue:
    def __init__(self, path):
        # Create private files before SQLite opens them. Existing paths must be files.
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('database must be a regular file')
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS messages (
              account TEXT NOT NULL, message_id TEXT NOT NULL, site TEXT NOT NULL,
              packet TEXT NOT NULL, batch TEXT,
              PRIMARY KEY(account, message_id));
            CREATE TABLE IF NOT EXISTS batches (
              id TEXT PRIMARY KEY, site TEXT NOT NULL, state TEXT NOT NULL, owner TEXT NOT NULL,
              task_id TEXT, run_id TEXT, chat_url TEXT, handback_receipt TEXT, notification_receipt TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_site
              ON batches(site) WHERE state='active';
        ''')

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def enqueue(self, packet, *, eligible):
        if eligible is not True:
            raise ValueError('fresh verified board eligibility required')
        for key in ('account', 'message_id', 'thread_id', 'site', 'cockpit_id',
                    'sender', 'received_at', 'source_url', 'original_text'):
            if not isinstance(packet.get(key), str) or not packet[key].strip():
                raise ValueError('missing ' + key)
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', packet['site']):
            raise ValueError('invalid site')
        when = datetime.fromisoformat(packet['received_at'].replace('Z', '+00:00'))
        if when.tzinfo is None:
            raise ValueError('timestamp needs timezone')
        items = packet.get('items')
        if not isinstance(items, list) or not items:
            raise ValueError('actionable feedback items required')
        ids = []
        for item in items:
            if not isinstance(item, dict) or not item.get('id') or not item.get('request'):
                raise ValueError('invalid feedback item')
            if not isinstance(item['id'], str) or not isinstance(item['request'], str):
                raise ValueError('item ID and request must be text')
            ids.append(item['id'])
        if len(set(ids)) != len(ids):
            raise ValueError('duplicate feedback item ID')
        images = packet.get('images')
        if not isinstance(images, list):
            raise ValueError('explicit image manifest required')
        cids = []
        for image in images:
            if not isinstance(image, dict) or image.get('status') != 'verified':
                raise ValueError('image not retrieved/verified')
            if not all(isinstance(image.get(k), str) and image[k]
                       for k in ('content_id', 'private_ref', 'sha256', 'context')):
                raise ValueError('incomplete image manifest')
            if not re.fullmatch(r'[a-f0-9]{64}', image['sha256']):
                raise ValueError('invalid image digest')
            cids.append(image['content_id'])
        if len(set(cids)) != len(cids):
            raise ValueError('duplicate image content ID')
        body = json.dumps(packet, sort_keys=True, ensure_ascii=False)
        with self.transaction():
            old = self.db.execute('SELECT site FROM messages WHERE account=? AND message_id=?',
                                  (packet['account'], packet['message_id'])).fetchone()
            if old:
                if old['site'] != packet['site']:
                    raise ValueError('message already routed to another site')
                return 'existing'
            self.db.execute('INSERT INTO messages VALUES (?,?,?,?,NULL)',
                            (packet['account'], packet['message_id'], packet['site'], body))
        return 'queued'

    def claim(self, site, *, owner, eligible):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError('persisted owner token required')
        if eligible is not True:
            return None
        with self.transaction():
            old = self.db.execute("SELECT * FROM batches WHERE site=? AND state='active'",
                                  (site,)).fetchone()
            if old:
                if old['owner'] != owner:
                    return dict(id=old['id'], site=site, state='busy')
                return dict(old)  # Resume/reconcile this exact run; never replay it.
            rows = self.db.execute('SELECT * FROM messages WHERE site=? AND batch IS NULL '
                                   'ORDER BY account,message_id', (site,)).fetchall()
            if not rows:
                return None
            identity = json.dumps([[r['account'], r['message_id']] for r in rows])
            batch = 'prototype-' + hashlib.sha256(identity.encode()).hexdigest()[:32]
            self.db.execute("INSERT INTO batches(id,site,state,owner) VALUES (?,?,'active',?)",
                            (batch, site, owner))
            self.db.execute('UPDATE messages SET batch=? WHERE site=? AND batch IS NULL',
                            (batch, site))
            return dict(self.db.execute('SELECT * FROM batches WHERE id=?', (batch,)).fetchone())

    def checkpoint(self, batch, *, owner, **fields):
        if not fields or set(fields) - {'task_id', 'run_id', 'chat_url', 'handback_receipt', 'notification_receipt'}:
            raise ValueError('unsupported checkpoint')
        if any(not isinstance(v, str) or not v for v in fields.values()):
            raise ValueError('checkpoint values must be nonempty strings')
        with self.transaction():
            row = self.db.execute('SELECT * FROM batches WHERE id=?', (batch,)).fetchone()
            if not row:
                raise ValueError('unknown batch')
            if row['owner'] != owner:
                raise ValueError('batch owned by another poller')
            for key, value in fields.items():
                if row[key] and row[key] != value:
                    raise ValueError('conflicting ' + key + ': reconcile remote state')
            if fields.get('run_id') and not (row['task_id'] or fields.get('task_id')):
                raise ValueError('task checkpoint required before run')
            for key, value in fields.items():
                self.db.execute(f'UPDATE batches SET {key}=? WHERE id=?', (value, batch))

    def ready(self, batch, *, owner, verified):
        if verified is not True:
            raise ValueError('verified preview, checks and handback required')
        with self.transaction():
            row = self.db.execute('SELECT * FROM batches WHERE id=?', (batch,)).fetchone()
            if not row or not all(row[k] for k in ('task_id', 'run_id', 'chat_url', 'handback_receipt')):
                raise ValueError('missing verified review checkpoints')
            if row['owner'] != owner:
                raise ValueError('batch owned by another poller')
            self.db.execute("UPDATE batches SET state='ready_for_review' WHERE id=?", (batch,))

    def packets(self, batch):
        return [json.loads(r[0]) for r in self.db.execute(
            'SELECT packet FROM messages WHERE batch=? ORDER BY account,message_id', (batch,))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('action', choices=['enqueue', 'claim', 'packets'])
    parser.add_argument('--packet')
    parser.add_argument('--site')
    parser.add_argument('--batch')
    parser.add_argument('--owner')
    parser.add_argument('--eligible', action='store_true',
                        help='trusted adapter asserts a fresh live eligibility check')
    args = parser.parse_args()
    queue = Queue(args.db)
    if args.action == 'enqueue':
        if not args.packet:
            parser.error('--packet required')
        with open(args.packet) as source:
            result = queue.enqueue(json.load(source), eligible=args.eligible)
    elif args.action == 'claim':
        if not args.site or not args.owner:
            parser.error('--site and --owner required')
        result = queue.claim(args.site, owner=args.owner, eligible=args.eligible)
    else:
        if not args.batch:
            parser.error('--batch required')
        result = queue.packets(args.batch)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
