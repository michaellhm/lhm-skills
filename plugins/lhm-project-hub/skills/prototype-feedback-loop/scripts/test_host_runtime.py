"""Host coordinator fault tests. Fakes prove contracts, never live deployment."""
import copy
import fcntl
import json
import io
import tarfile
import os
import tempfile
import unittest
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import quote

import host_runtime as mod
from adapters import ReconcileRequired


class FakeTed:
    def __init__(self):
        self.cockpit = {'id': 1, 'project': {'id': 68635}, 'section': {'id': mod.STAGE},
                        'status': 'In Progress', 'url': 'https://app.basicops.com/cockpit'}
        self.tasks, self.messages, self.routes = {}, {}, {}
        self.writes, self.submits = [], 0
        self.timeout = None
        self.running = True
        self.identity = mod.TED
        self.list_calls = 0
        self.exit_on_task_lookup = False
        self.exit_before_submit = False

    def basicops(self, name, args):
        if name == 'get_current_user': return {'id': self.identity}
        if name == 'get_task': return copy.deepcopy(self.cockpit if args['taskId'] == 1 else self.tasks[args['taskId']])
        if name == 'list_tasks_in_project':
            self.list_calls += 1
            if self.exit_on_task_lookup and self.list_calls == 2:
                self.cockpit['section']['id'] = 999
            return {'data': copy.deepcopy(list(self.tasks.values()))}
        if name == 'list_messages_in_task':
            if args['limit'] > 50: raise ValueError('provider page limit')
            return {'data': copy.deepcopy(self.messages.get(args['taskId'], []))}
        if name == 'create_task':
            self.writes.append(name)
            if self.timeout == 'task-before': raise TimeoutError('unknown create outcome')
            ident = 100 + len(self.tasks)
            value = {'id': ident, 'title': args['title'], 'description': args['description'],
                     'project': {'id': args['projectId']}, 'section': {'id': args['section']},
                     'assignee': {'id': args['assignee']}, 'status': args['status'], 'url': f'https://app.basicops.com/task/{ident}'}
            self.tasks[ident] = value
            if self.timeout == 'task-after':
                self.timeout = None;raise TimeoutError('create response lost')
            return copy.deepcopy(value)
        if name == 'create_message_in_task':
            self.writes.append(name)
            values = self.messages.setdefault(args['taskId'], [])
            value = {'id': 'dm' + str(1000 + len(values)), 'user': {'id': mod.TED}, 'message': args['message']}
            values.append(value)
            if self.timeout == 'brief-after':
                self.timeout = None;raise TimeoutError('brief response lost')
            return copy.deepcopy(value)
        raise AssertionError(name)

    def route(self, action, task_id, instruction_message_id=None):
        if action == 'status':
            if self.exit_before_submit and task_id not in self.routes:
                self.cockpit['section']['id'] = 999
            return copy.deepcopy(self.routes.get(task_id, {'task_id': task_id, 'status': 'not_submitted'}))
        self.submits += 1
        thread = '3f774b8f-1df0-4b6e-8b1d-cf0628773a19'
        value = {'task_id': task_id, 'request_id': f'ted-route-{task_id}-{instruction_message_id}',
                 'provider': 'codex', 'client_id': 'blue-dragonfly', 'status': 'running' if self.running else 'queued'}
        if self.running:
            value.update(thread_id=thread, chat_url='codex://threads/' + thread + '?hostId=remote-control%3Atest-host')
        self.routes[task_id] = value
        if self.timeout == 'submit-after':
            self.timeout = None;raise TimeoutError('submit response lost')
        return copy.deepcopy(value)


class FakeSourceStore:
    def __init__(self):
        self.calls = 0
        self.files = {'luminary-counselling/homepage/index.html': b'<html>current published source</html>',
                      'luminary-counselling/homepage/styles.css': b'body { color: #222; }'}
        self.link = None

    def fetch(self):
        self.calls += 1
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w') as package:
            for name, data in self.files.items():
                entry = tarfile.TarInfo(name);entry.size = len(data)
                package.addfile(entry, io.BytesIO(data))
            if self.link:
                entry = tarfile.TarInfo('luminary-counselling/homepage/linked.svg')
                entry.type = tarfile.SYMTYPE;entry.linkname = self.link
                package.addfile(entry)
        return {'base_commit': 'b'*40, 'archive': output.getvalue()}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.state = self.root/'runtime';self.state.mkdir(mode=0o700)
        self.workspaces = self.root/'workspaces';self.workspaces.mkdir()
        self.worker = self.workspaces/'blue-dragonfly';self.worker.mkdir()
        self.config = self.root/'sites.json'
        self.authority = self.root/'releases/prototype-feedback-authority/authority.json'
        self.authority.parent.parent.mkdir()
        self.site = 'luminary-counselling'
        self.reg = {'enabled': True, 'account': 'michael@example.com', 'senders': ['tara@example.com'],
                    'threads': ['1a1a8d364f7f2f43'], 'review_start': '2026-11-05T00:00:00+00:00',
                    'cockpit_id': 1, 'stage_id': mod.STAGE, 'client_id': 'blue-dragonfly', 'client_label': 'Blue Dragonfly',
                    'canonical_note': '20 Clients/Blue Dragonfly/project-management/website.md',
                    'work_folder_url': 'https://drive.google.com/drive/folders/clientfolder0000',
                    'repository': mod.REPOSITORY, 'subtree': mod.SUBTREE,
                    'preview_url': 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/',
                    'reviewer_id': mod.REVIEWER, 'worker_root': str(self.worker)}
        self.write(self.config, {'schema_version': 1, 'sites': {self.site: self.reg}}, 0o644)
        self.write(self.worker/'.workspace.json', {'provider': 'codex', 'client_id': 'blue-dragonfly', 'workspace': str(self.worker)}, 0o644)
        real_fstat = os.fstat
        def root_fstat(fd):
            value = real_fstat(fd)
            return SimpleNamespace(st_uid=0, st_gid=10001, st_mode=value.st_mode, st_nlink=value.st_nlink,
                                   st_size=value.st_size, st_mtime_ns=value.st_mtime_ns)
        for mocked in (patch.object(mod.os, 'geteuid', return_value=0), patch.object(mod.os, 'fstat', side_effect=root_fstat),
                       patch.object(mod.os, 'chown'), patch.object(mod.os, 'fchown'), patch.object(mod, 'WORKSPACES', self.workspaces)):
            mocked.start();self.addCleanup(mocked.stop)
        self.backend = FakeTed()
        self.source_store = FakeSourceStore()
        self.runtime = self.new_runtime();self.addCleanup(self.runtime.close)
        self.envelope = self.packet('1a1af9e9eeb719cb')

    @staticmethod
    def write(path, value, mode=0o600):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(mod.canonical(value) if isinstance(value, (dict, list)) else value)
        path.chmod(mode)

    def new_runtime(self):
        return mod.Coordinator(config=self.config, state_root=self.state, authority=self.authority, backend=self.backend, source_store=self.source_store)

    def packet(self, message_id, *, thread=None, text='Please revise the logo and organic texture.', images=True):
        message = EmailMessage()
        message['From'] = 'Tara <tara@example.com>';message['To'] = 'michael@example.com'
        message['Date'] = 'Fri, 06 Nov 2026 06:49:18 +0000';message['Subject'] = 'Luminary Counselling feedback'
        message['Authentication-Results'] = 'mx.google.com; dkim=pass header.i=@example.com; dmarc=pass header.from=example.com'
        message.set_content(text)
        blobs = [b'first-image', b'second-image'] if images else []
        for index, data in enumerate(blobs):
            message.add_attachment(data, maintype='image', subtype='png', filename='image.png', cid=f'<cid{index}>', disposition='inline')
        raw = message.as_bytes(policy=policy.SMTP)
        parsed = BytesParser(policy=policy.default).parsebytes(raw)
        preferred = [p.get_payload(decode=True).decode() for p in parsed.walk() if p.get_content_type() == 'text/plain']
        evidence_root = self.state/'evidence'/self.site/message_id
        raw_path = evidence_root/'message.eml';self.write(raw_path, raw)
        items = []
        for index, data in enumerate(blobs):
            path = evidence_root/f'image-{index}';self.write(path, data)
            items.append({'content_id': f'cid{index}', 'private_ref': str(path), 'sha256': mod.sha(data),
                          'context': 'Visually inspected illustration' if index == 0 else 'Visually inspected organic roots', 'status': 'verified'})
        packet = {'account': self.reg['account'], 'message_id': message_id, 'thread_id': thread or self.reg['threads'][0],
                  'site': self.site, 'cockpit_id': '1', 'sender': 'tara@example.com', 'received_at': '2026-11-06T06:49:18+00:00',
                  'source_url': 'https://mail.google.com/mail/u/?authuser=' + quote(self.reg['account'], safe='') + '#all/' + message_id,
                  'original_text': '\n'.join(preferred), 'items': [{'id': 'R1', 'request': 'Revise logo and texture'}], 'images': items}
        receipt = {'schema_version': 1, 'status': 'reviewed', 'account': packet['account'], 'message_id': message_id,
                   'thread_id': packet['thread_id'], 'raw_sha256': mod.sha(raw), 'packet_sha256': mod.sha(mod.canonical(packet)),
                   'reviewer': 'codex:516ec09f-2c39-4458-ac74-73f7818aa895', 'attachment_count': len(blobs), 'related_thread': False}
        receipt_path = evidence_root/'extraction-receipt.json';self.write(receipt_path, receipt)
        evidence = {k: receipt[k] for k in ('account', 'message_id', 'thread_id', 'raw_sha256', 'packet_sha256')}
        evidence.update(raw_path=str(raw_path), extraction_receipt_path=str(receipt_path), extraction_receipt_sha256=mod.sha(mod.canonical(receipt)))
        envelope = {'schema_version': 1, 'site': self.site, 'packet': packet, 'evidence': evidence}
        path = self.state/'inbox'/self.site/(message_id + '.json');self.write(path, envelope)
        return envelope

    def restart(self):
        # One coordinator owns state at a time; an exclusive runner lock proves old process release.
        other = self.new_runtime();self.addCleanup(other.close)
        return other

    def test_actual_bridge_uses_fixed_argv_and_json_stdin(self):
        native = mod.NativeTed()
        reply = SimpleNamespace(returncode=0, stdout='{"id":82491}', stderr='private diagnostic')
        with patch.object(mod.subprocess, 'run', return_value=reply) as run:
            self.assertEqual(native.basicops('get_current_user', {}), {'id': 82491})
        args, kwargs = run.call_args
        self.assertEqual(args[0], mod.DOCKER)
        self.assertNotIn('shell', kwargs)
        self.assertEqual(json.loads(kwargs['input']), {'kind': 'basicops', 'action': 'get_current_user', 'arguments': {}})
        with self.assertRaises(ValueError): native.basicops('send_email', {})
        with self.assertRaises(ValueError): native.route('delete', 1)

    def test_dry_run_validates_without_remote_mutations(self):
        result = self.runtime.run(self.site, 'dispatch', dry_run=True)
        self.assertEqual(result['state'], 'prepared');self.assertEqual(result['attachments'], 2)
        self.assertEqual(self.backend.writes, []);self.assertEqual(self.backend.submits, 0)
        self.assertEqual(self.runtime.queue.db.execute('SELECT count(*) FROM messages').fetchone()[0], 0)
        self.assertFalse(self.authority.exists())

    def test_full_dispatch_and_restart_reuses_task_brief_run_and_actual_chat(self):
        first = self.runtime.run(self.site, 'dispatch')
        second = self.restart().run(self.site, 'dispatch')
        self.assertEqual(first, second)
        self.assertEqual(first['state'], 'dispatched')
        self.assertEqual(self.backend.writes, ['create_task', 'create_message_in_task']);self.assertEqual(self.backend.submits, 1)
        row = self.runtime.queue.db.execute('SELECT * FROM batches').fetchone()
        self.assertEqual(row['run_id'], first['request_id']);self.assertEqual(row['chat_url'], first['chat_url'])
        grant = json.loads(self.authority.read_text())['grants'][str(first['task_id'])]
        self.assertEqual(grant['instruction_sha256'], mod.sha(self.backend.messages[first['task_id']][0]['message'].encode()))
        self.assertEqual(grant['batch_id'], first['batch_id'])
        text = self.backend.messages[first['task_id']][0]['message']
        self.assertIn('<ol><li>Revise logo and texture</li></ol>', text)
        self.assertNotIn(first['batch_id'], self.backend.tasks[first['task_id']]['title'])
        self.assertNotIn(first['batch_id'], self.backend.tasks[first['task_id']]['description'])

    def test_fresh_source_is_bound_and_visible_in_worker_brief_without_refetch_on_restart(self):
        first = self.runtime.run(self.site, 'dispatch')
        manifest_path = self.state/'sources'/first['batch_id']/'source-manifest.json'
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest['base_commit'], 'b'*40)
        self.assertEqual(manifest['subtree'], 'luminary-counselling/homepage/')
        self.assertEqual(manifest['package_sha256'], mod.sha(mod.canonical(manifest['files'])))
        self.assertEqual((Path(manifest['source_root'])/'luminary-counselling/homepage/index.html').read_bytes(), b'<html>current published source</html>')
        self.assertIn(manifest['source_root'], self.backend.messages[first['task_id']][0]['message'])
        self.assertIn('drafts/revised-source/luminary-counselling/homepage/', self.backend.messages[first['task_id']][0]['message'])
        self.restart().run(self.site, 'dispatch')
        self.assertEqual(self.source_store.calls, 1)

    def test_source_and_qa_inputs_remain_group_readable_under_private_service_umask(self):
        previous = os.umask(0o077)
        try:
            first = self.runtime.run(self.site, 'dispatch')
            manifest = json.loads((self.state/'sources'/first['batch_id']/'source-manifest.json').read_text())
            source = Path(manifest['source_root'])
            self.assertEqual(source.stat().st_mode & 0o777, 0o750)
            self.assertEqual((source/'luminary-counselling/homepage/index.html').stat().st_mode & 0o777, 0o640)
            qa = mod.protected_directory(self.state/'new-qa', group=10001)
            mod.atomic(qa/'schema.json', b'{}', mode=0o640, group=10001)
            self.assertEqual(qa.stat().st_mode & 0o777, 0o750)
            self.assertEqual((qa/'schema.json').stat().st_mode & 0o777, 0o640)
            private = mod.protected_directory(self.state/'new-private', private=True)
            mod.atomic(private/'receipt.json', b'{}')
            self.assertEqual(private.stat().st_mode & 0o777, 0o700)
            self.assertEqual((private/'receipt.json').stat().st_mode & 0o777, 0o600)
        finally:
            os.umask(previous)

    def test_existing_unreadable_shared_inputs_are_rejected_without_broadening(self):
        legacy = self.state/'legacy-qa';legacy.mkdir(mode=0o700)
        with self.assertRaises(ValueError):
            mod.protected_directory(legacy, group=10001)
        self.assertEqual(legacy.stat().st_mode & 0o777, 0o700)
        file = legacy/'source';file.write_bytes(b'old');file.chmod(0o600)
        with self.assertRaises(ValueError):
            mod.root_bytes(file, readable_group=10001)
        self.assertEqual(file.stat().st_mode & 0o777, 0o600)

    def test_source_snapshot_rejects_symlinks_and_out_of_subtree_before_task(self):
        self.source_store.link = '../../other-client/index.html'
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_source_snapshot_rejects_unrelated_static_files_before_task(self):
        self.source_store.files['other-client/homepage/index.html'] = b'other'
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_source_fetch_provenance_is_reused_after_task_timeout(self):
        self.backend.timeout = 'task-after'
        with self.assertRaises(TimeoutError): self.runtime.run(self.site, 'dispatch')
        self.source_store.files['luminary-counselling/homepage/index.html'] = b'new main after timeout'
        result = self.restart().run(self.site, 'dispatch')
        self.assertEqual(result['state'], 'dispatched');self.assertEqual(self.source_store.calls, 1)
        manifest = json.loads((self.state/'sources'/result['batch_id']/'source-manifest.json').read_text())
        self.assertEqual((Path(manifest['source_root'])/'luminary-counselling/homepage/index.html').read_bytes(), b'<html>current published source</html>')

    def test_native_source_store_uses_separate_bare_objects_and_fixed_subtree(self):
        store = self.root/'publisher/feedback-source.git';store.parent.mkdir()
        helper = self.root/'publisher-helper';self.write(helper, b'fixture module', 0o644)
        class ExistingPublisher:
            REPOSITORY = mod.REPOSITORY
            BRANCH = 'main'
            REMOTE = 'ssh://git@ssh.github.com:443/michaellhm/lhm-prototype.git'
            @staticmethod
            def ssh_env(): return {'FIXTURE_TRANSPORT': 'existing-root-only-route'}
        spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda module: None))
        commands = []
        def run(args, **kwargs):
            commands.append((args, kwargs))
            output = b'b'*40+b'\n' if args[-2:] == ['rev-parse', 'FETCH_HEAD'] else b'archive' if 'archive' in args else b''
            return SimpleNamespace(returncode=0, stdout=output, stderr=b'')
        with patch.object(mod, 'SOURCE_STORE', store), patch.object(mod, 'PUBLISHER', helper), \
             patch.object(mod.importlib.util, 'spec_from_loader', return_value=spec), \
             patch.object(mod.importlib.util, 'module_from_spec', return_value=ExistingPublisher), \
             patch.object(mod.subprocess, 'run', side_effect=run):
            result = mod.NativeSourceStore().fetch()
        self.assertEqual(result['base_commit'], 'b'*40)
        self.assertTrue(all('--git-dir='+str(store) in args for args, _ in commands))
        self.assertFalse(any('reset' in args or 'checkout' in args or 'push' in args for args, _ in commands))
        fetch = next((args, kwargs) for args, kwargs in commands if 'fetch' in args)
        self.assertEqual(fetch[0][-2:], [ExistingPublisher.REMOTE, 'main'])
        archive = next(args for args, _ in commands if 'archive' in args)
        self.assertEqual(archive[-1], 'luminary-counselling/homepage')
        self.assertNotIn('env', result)

    def test_new_feedback_does_not_rewrite_active_brief(self):
        first = self.runtime.run(self.site, 'dispatch')
        brief = self.backend.messages[first['task_id']][0]['message']
        self.packet('1a1afefeaf44048e', images=False)
        self.runtime.run(self.site, 'dispatch')
        self.assertEqual(self.backend.messages[first['task_id']][0]['message'], brief)
        self.assertEqual(self.backend.submits, 1)
        self.assertEqual(self.runtime.queue.db.execute('SELECT count(*) FROM messages WHERE batch IS NULL').fetchone()[0], 1)

    def test_remote_create_timeout_reconciles_without_replay(self):
        self.backend.timeout = 'task-after'
        with self.assertRaises(TimeoutError): self.runtime.run(self.site, 'dispatch')
        self.assertEqual(self.restart().run(self.site, 'dispatch')['state'], 'dispatched')
        self.assertEqual(self.backend.writes.count('create_task'), 1)

    def test_remote_brief_timeout_reconciles_without_replay(self):
        self.backend.timeout = 'brief-after'
        with self.assertRaises(TimeoutError): self.runtime.run(self.site, 'dispatch')
        self.assertEqual(self.restart().run(self.site, 'dispatch')['state'], 'dispatched')
        self.assertEqual(self.backend.writes.count('create_message_in_task'), 1)

    def test_remote_submit_timeout_reconciles_same_request(self):
        self.backend.timeout = 'submit-after'
        with self.assertRaises(TimeoutError): self.runtime.run(self.site, 'dispatch')
        self.assertEqual(self.restart().run(self.site, 'dispatch')['state'], 'dispatched')
        self.assertEqual(self.backend.submits, 1)

    def test_unknown_remote_create_never_blindly_retries(self):
        self.backend.timeout = 'task-before'
        with self.assertRaises(TimeoutError): self.runtime.run(self.site, 'dispatch')
        self.backend.timeout = None
        with self.assertRaises(ReconcileRequired): self.restart().run(self.site, 'dispatch')
        self.assertEqual(self.backend.writes.count('create_task'), 1)

    def test_stage_exit_before_task_write_can_resume_same_batch_after_return(self):
        self.backend.exit_on_task_lookup = True
        first = self.runtime.run(self.site, 'dispatch')
        self.assertEqual(first['state'], 'paused');self.assertEqual(self.backend.writes, [])
        self.assertIsNone(self.runtime.effects.db.execute('SELECT 1 FROM effects').fetchone())
        self.backend.cockpit['section']['id'] = mod.STAGE
        self.assertEqual(self.restart().run(self.site, 'dispatch')['state'], 'dispatched')
        self.assertEqual(self.backend.writes.count('create_task'), 1)

    def test_stage_exit_before_submit_can_resume_without_duplicate_task_or_brief(self):
        self.backend.exit_before_submit = True
        first = self.runtime.run(self.site, 'dispatch')
        self.assertEqual(first['state'], 'paused');self.assertEqual(self.backend.submits, 0)
        self.assertIsNone(self.runtime.effects.db.execute("SELECT 1 FROM effects WHERE key LIKE '%:native-submit'").fetchone())
        self.backend.exit_before_submit = False;self.backend.cockpit['section']['id'] = mod.STAGE
        self.assertEqual(self.restart().run(self.site, 'dispatch')['state'], 'dispatched')
        self.assertEqual(self.backend.writes, ['create_task', 'create_message_in_task'])
        self.assertEqual(self.backend.submits, 1)

    def test_queued_receipt_is_not_called_dispatched(self):
        self.backend.running = False
        first = self.runtime.run(self.site, 'dispatch')
        self.assertEqual(first['state'], 'submitted-awaiting-admission');self.assertIsNone(first['chat_url'])
        self.runtime.run(self.site, 'dispatch');self.assertEqual(self.backend.submits, 1)

    def test_stage_exit_stops_new_dispatch_without_stopping_existing_run(self):
        first = self.runtime.run(self.site, 'dispatch')
        self.backend.cockpit['section']['id'] = 999
        self.assertEqual(self.runtime.run(self.site, 'dispatch')['state'], 'paused')
        result = self.runtime.run(self.site, 'readback')
        self.assertEqual(result['batches'][0]['native_status']['request_id'], first['request_id'])
        self.assertEqual(self.backend.submits, 1)

    def test_wrong_connector_and_wrong_source_scope_block(self):
        self.backend.identity = mod.REVIEWER
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.backend.identity = mod.TED
        self.reg['repository'] = 'michaellhm/live-site'
        self.write(self.config, {'schema_version': 1, 'sites': {self.site: self.reg}}, 0o644)
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def authentication_header(self, headers):
        raw_path = Path(self.envelope['evidence']['raw_path'])
        message = BytesParser(policy=policy.default).parsebytes(raw_path.read_bytes())
        del message['Authentication-Results']
        for header in headers:
            message['Authentication-Results'] = header
        raw = message.as_bytes(policy=policy.SMTP);self.write(raw_path, raw)
        self.envelope['evidence']['raw_sha256'] = mod.sha(raw)
        receipt_path = Path(self.envelope['evidence']['extraction_receipt_path'])
        receipt = json.loads(receipt_path.read_text());receipt['raw_sha256'] = mod.sha(raw)
        self.write(receipt_path, receipt)
        self.envelope['evidence']['extraction_receipt_sha256'] = mod.sha(mod.canonical(receipt))
        self.write(self.state/'inbox'/self.site/(self.envelope['packet']['message_id']+'.json'), self.envelope)

    def test_missing_receiving_sender_proof_blocks_root_promoted_packet(self):
        self.authentication_header([])
        with self.assertRaisesRegex(ValueError, 'authentication'): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_lower_injected_passing_header_cannot_override_top_receiving_failure(self):
        self.authentication_header([
            'mx.google.com; dkim=fail header.i=@example.com; dmarc=fail header.from=example.com',
            'mx.google.com; dkim=pass header.i=@example.com; dmarc=pass header.from=example.com'])
        with self.assertRaisesRegex(ValueError, 'aligned'): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_passing_untrusted_authserver_above_google_is_held(self):
        self.authentication_header([
            'attacker.invalid; dkim=pass header.i=@example.com; dmarc=pass header.from=example.com',
            'mx.google.com; dkim=pass header.i=@example.com; dmarc=pass header.from=example.com'])
        with self.assertRaisesRegex(ValueError, 'topmost'): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_unaligned_dkim_pass_is_held_even_with_dmarc_pass(self):
        self.authentication_header(['mx.google.com; dkim=pass header.i=@other.example; dmarc=pass header.from=example.com'])
        with self.assertRaisesRegex(ValueError, 'aligned'): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_unreviewed_or_changed_attachment_blocks_before_task(self):
        path = Path(self.envelope['packet']['images'][0]['private_ref']);path.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_missing_mime_attachment_cannot_disappear_from_brief(self):
        self.envelope['packet']['images'].pop()
        self.reseal()
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def reseal(self):
        packet, evidence = self.envelope['packet'], self.envelope['evidence']
        evidence['packet_sha256'] = mod.sha(mod.canonical(packet))
        path = Path(evidence['extraction_receipt_path']);receipt = json.loads(path.read_text())
        receipt['packet_sha256'] = evidence['packet_sha256'];self.write(path, receipt)
        evidence['extraction_receipt_sha256'] = mod.sha(mod.canonical(receipt))
        self.write(self.state/'inbox'/self.site/(packet['message_id']+'.json'), self.envelope)

    def test_related_followup_needs_root_review_and_original_explicit_reference(self):
        self.envelope = self.packet('1a1afefeaf44048e', thread='1b1b1b1b1b1b1b1b', text='Unrelated appointment request', images=False)
        receipt_path = Path(self.envelope['evidence']['extraction_receipt_path'])
        receipt = json.loads(receipt_path.read_text());receipt['related_thread'] = True;self.write(receipt_path, receipt)
        self.envelope['evidence']['extraction_receipt_sha256'] = mod.sha(mod.canonical(receipt))
        self.write(self.state/'inbox'/self.site/'1a1afefeaf44048e.json', self.envelope)
        # Subject itself identifies Luminary, so remove that source evidence too.
        raw_path = Path(self.envelope['evidence']['raw_path'])
        raw = raw_path.read_bytes().replace(b'Luminary Counselling feedback', b'Appointment question')
        self.write(raw_path, raw);self.envelope['evidence']['raw_sha256'] = mod.sha(raw)
        receipt['raw_sha256'] = mod.sha(raw);self.write(receipt_path, receipt)
        self.envelope['evidence']['extraction_receipt_sha256'] = mod.sha(mod.canonical(receipt))
        self.write(self.state/'inbox'/self.site/'1a1afefeaf44048e.json', self.envelope)
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')

    def test_legacy_processed_pilot_ids_are_not_replayed_after_extraction_drift(self):
        self.runtime.run(self.site, 'scan')
        old = self.runtime.queue.db.execute('SELECT packet FROM messages').fetchone()[0]
        self.envelope['packet']['items'][0]['request'] = 'Different extractor wording'
        self.reseal()
        result = self.runtime.run(self.site, 'scan')
        self.assertEqual(result['messages'], ['existing-extraction-differs'])
        self.assertEqual(self.runtime.queue.db.execute('SELECT packet FROM messages').fetchone()[0], old)

    def test_existing_source_task_requires_explicit_adoption(self):
        self.backend.tasks[88] = {'id': 88, 'title': 'Blue Dragonfly: Website - Existing revision',
            'description': self.envelope['packet']['source_url'], 'status': 'In Progress', 'url': 'https://app.basicops.com/existing'}
        with self.assertRaisesRegex(ReconcileRequired, 'adoption'): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes);self.assertEqual(self.backend.submits, 0)

    def test_existing_root_grants_are_preserved(self):
        self.write(self.authority, {'schema_version': 1, 'grants': {'999': {'existing': 'preserve'}}}, 0o644)
        self.runtime.run(self.site, 'dispatch')
        self.assertEqual(json.loads(self.authority.read_text())['grants']['999'], {'existing': 'preserve'})

    def test_atomic_write_stays_on_opened_directory_when_parent_path_is_swapped(self):
        anchor = self.root/'atomic-anchor';anchor.mkdir(mode=0o750)
        moved = self.root/'moved-anchor';victim = self.root/'victim';victim.mkdir()
        (victim/'result.json').write_bytes(b'preserve unrelated bytes')
        real_open = mod.os.open
        swapped = False
        def opening(path, flags, *args, **kwargs):
            nonlocal swapped
            fd = real_open(path, flags, *args, **kwargs)
            if path == 'atomic-anchor' and flags & os.O_DIRECTORY and not swapped:
                swapped = True;anchor.rename(moved);anchor.symlink_to(victim, target_is_directory=True)
            return fd
        with patch.object(mod.os, 'open', side_effect=opening):
            mod.atomic(anchor/'result.json', b'new scoped bytes')
        self.assertEqual((moved/'result.json').read_bytes(), b'new scoped bytes')
        self.assertEqual((victim/'result.json').read_bytes(), b'preserve unrelated bytes')

    def test_directory_creation_rejects_linked_ancestor_without_touching_target(self):
        victim = self.root/'victim';victim.mkdir()
        link = self.root/'linked-parent';link.symlink_to(victim, target_is_directory=True)
        with self.assertRaises(OSError): mod.protected_directory(link/'unexpected')
        self.assertFalse((victim/'unexpected').exists())

    def test_worker_writable_parent_is_rejected_before_task_creation(self):
        self.worker.chmod(0o777)
        with self.assertRaises(ValueError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_existing_manual_pilot_source_folder_is_preserved(self):
        legacy = self.worker/'feedback-source';legacy.mkdir(mode=0o700)
        (legacy/'pilot.txt').write_bytes(b'active pilot input')
        result = self.runtime.run(self.site, 'dispatch')
        self.assertEqual((legacy/'pilot.txt').read_bytes(), b'active pilot input')
        self.assertEqual(legacy.stat().st_mode & 0o777, 0o700)
        self.assertTrue((self.worker/'feedback-source-snapshots'/result['batch_id']/'source').is_dir())
        self.assertTrue((self.worker/'feedback-assets'/result['batch_id']).is_dir())

    def test_root_scan_symlink_is_rejected(self):
        path = self.state/'inbox'/self.site/'1a1af9e9eeb719cb.json'
        target = path.with_suffix('.saved');path.rename(target);path.symlink_to(target)
        with self.assertRaises(OSError): self.runtime.run(self.site, 'dispatch')
        self.assertFalse(self.backend.writes)

    def test_exclusive_runner_lock_prevents_competing_poller(self):
        path = self.state/'runner.lock'
        with path.open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.runtime.run(self.site, 'dispatch')['state'], 'busy')
        self.assertFalse(self.backend.writes)

    def test_existing_nonwritable_audit_root_0755_preserves_private_state(self):
        self.state.chmod(0o755)
        runtime = self.restart()
        self.assertEqual(runtime.run(self.site, 'readback')['state'], 'readback')
        self.assertEqual((self.state/'state').stat().st_mode & 0o777, 0o700)
        self.state.chmod(0o777)
        with self.assertRaises(ValueError): self.new_runtime()

    def test_existing_dashed_uuid_owner_and_exact_state_queue_path(self):
        owner = '0d85cba2-98a1-4153-8101-73c5dc57ec54'
        self.write(self.state/'state/owner.json', {'owner': owner})
        self.runtime.run(self.site, 'dispatch')
        self.assertEqual(self.runtime.queue.db.execute('SELECT owner FROM batches').fetchone()[0], owner)
        self.assertTrue((self.state/'state/queue.sqlite').exists())
        self.assertFalse((self.state/'queue.sqlite3').exists())


@unittest.skipUnless(os.geteuid() == 0, 'actual root ownership smoke; never uses live paths')
class RootModeSmokeTests(unittest.TestCase):
    def test_real_group_ownership_and_modes_under_umask0077(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            previous = os.umask(0o077)
            try:
                shared = mod.protected_directory(root/'qa-source', group=10001)
                mod.atomic(shared/'schema.json', b'{}', mode=0o640, group=10001)
                private = mod.protected_directory(root/'private', private=True)
                mod.atomic(private/'receipt.json', b'{}')
            finally:
                os.umask(previous)
            for path, gid, mode in ((shared, 10001, 0o750), (shared/'schema.json', 10001, 0o640),
                                    (private, 0, 0o700), (private/'receipt.json', 0, 0o600)):
                info = path.stat()
                self.assertEqual((info.st_uid, info.st_gid, info.st_mode & 0o777), (0, gid, mode))


if __name__ == '__main__': unittest.main()
