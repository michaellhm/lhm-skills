"""Scheduled sweep orchestration tests; connectors/model execution are faked."""
import fcntl
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import poll_runtime as mod


class FakeCoordinator:
    def __init__(self, eligible=True):
        self.eligible = eligible;self.closed = False;self.calls = [];self.effects = None
        self.import_state = 'scanned'

    def identity(self): self.calls.append('identity')

    def basicops(self, name, args):
        if name != 'get_task': raise AssertionError(name)
        return {'project': {'id': 68635}, 'section': {'id': 110340 if self.eligible else 999}, 'status': 'In Progress'}

    def run(self, site, action):
        self.calls.append(action)
        return {'state': self.import_state} if action == 'scan' else {'state': 'dispatched', 'task_id': 100,
            'request_id': 'ted-route-100-dm100', 'worker_status': 'running', 'raw_model_output': 'must not log'}

    def close(self): self.closed = True


class PollTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve();self.runtime = FakeCoordinator()
        self.enabled = True;self.site = 'luminary-counselling'
        for item in (patch.object(mod, 'STATE_ROOT', self.root), patch.object(mod, 'Coordinator', return_value=self.runtime),
                     patch.object(mod.os, 'geteuid', return_value=0),
                     patch.object(mod, 'registration', return_value={'cockpit_id': 1, 'stage_id': 110340}),
                     patch.object(mod, 'root_json', side_effect=lambda _: {'schema_version': 1, 'sites': {self.site: {'enabled': self.enabled}}})):
            item.start();self.addCleanup(item.stop)
        self.commands = []

    def runner(self, args, **kwargs):
        self.commands.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=json.dumps({'scan_only': True,
            'outcomes': [{'state': 'held', 'private': 'must not log'}, {'classification': 'already_queued'}]}), stderr='private diagnostic')

    def test_sweep_serializes_scan_import_dispatch_and_logs_only_summary(self):
        result = mod.sweep(self.site, runner=self.runner)
        self.assertEqual(self.runtime.calls, ['identity', 'scan', 'dispatch'])
        self.assertEqual(result['state'], 'dispatched');self.assertEqual(result['held'], 1)
        self.assertNotIn('must not log', json.dumps(result));self.assertNotIn('raw_model_output', result)
        self.assertEqual(self.commands[0][0][0], '/usr/bin/python3')
        self.assertEqual(self.commands[0][0][-2:], ['--site', self.site])
        self.assertNotIn('shell', self.commands[0][1]);self.assertTrue(self.runtime.closed)

    def test_stage_exit_pauses_before_gmail_or_task_calls(self):
        self.runtime.eligible = False
        self.assertEqual(mod.sweep(self.site, runner=self.runner)['state'], 'paused')
        self.assertFalse(self.commands);self.assertEqual(self.runtime.calls, ['identity'])

    def test_disabled_registration_does_not_scan_or_dispatch(self):
        self.enabled = False
        self.assertEqual(mod.sweep(self.site, runner=self.runner)['state'], 'paused')
        self.assertEqual(self.runtime.calls, []);self.assertFalse(self.commands)

    def test_scan_schema_failure_prevents_dispatch(self):
        bad = lambda *a, **k: SimpleNamespace(returncode=0, stdout='{"scan_only":false,"outcomes":[]}', stderr='')
        with self.assertRaises(ValueError): mod.sweep(self.site, runner=bad)
        self.assertEqual(self.runtime.calls, ['identity'])

    def test_competing_sweep_is_busy_and_does_not_touch_active_work(self):
        with (self.root/'poll.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(mod.sweep(self.site, runner=self.runner)['state'], 'busy')
        self.assertEqual(self.runtime.calls, []);self.assertFalse(self.commands)

    def test_stage_exit_during_import_does_not_release_dispatch(self):
        self.runtime.import_state = 'paused'
        self.assertEqual(mod.sweep(self.site, runner=self.runner)['state'], 'paused')
        self.assertEqual(self.runtime.calls, ['identity', 'scan'])


if __name__ == '__main__': unittest.main()
