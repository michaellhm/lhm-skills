import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/recover_admission.py'


class RecoveryTests(unittest.TestCase):
    def test_recovery_reuses_original_request_and_refuses_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            request_id = 'ted-route-2216403-dm2679721'
            work, queue, root = base/'work', base/'queue', base/'client'
            run, queued, task = work/request_id, queue/'runs'/request_id, root/'tasks'/request_id
            for path in [run, queued, task/'drafts']:
                path.mkdir(parents=True)
            request = {'request_id': request_id, 'provider': 'claude', 'client_id': 'ysp', 'instruction_sha256': 'hash'}
            (run/'request.json').write_text(json.dumps(request))
            (run/'workspace-location.json').write_text(json.dumps({'workspace': str(root), 'task_directory': str(task)}))
            (task/'task-context.json').write_text(json.dumps({'instruction_sha256': 'hash'}))
            (queued/'receipt.json').write_text(json.dumps({'status': 'failed', 'error': 'Existing Obsidian registry is not our generated note'}))
            def atomic(path, value): path.write_text(json.dumps(value))
            dispatch = SimpleNamespace(BASE=queue, WORK=work, ID=re.compile(r'ted-route-[0-9]+-dm[0-9]+'), verified=Mock(return_value=request), read=lambda p: p.read_text(), atomic=atomic, launch=Mock())
            workspaces = SimpleNamespace(location=Mock(return_value=root), publish_registry=Mock())
            with patch.dict(sys.modules, {'dispatch': dispatch, 'workspaces': workspaces}):
                spec = importlib.util.spec_from_file_location('registry_recovery', SOURCE)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            with patch.object(module.os, 'geteuid', return_value=0), patch.object(module.subprocess, 'run', return_value=SimpleNamespace(stdout='inactive')):
                self.assertEqual(module.recover(request_id)['status'], 'starting')
                dispatch.launch.assert_called_once_with(request, run, root)
                workspaces.publish_registry.assert_called_once()
                with self.assertRaises(ValueError): module.recover(request_id)
                self.assertEqual(dispatch.launch.call_count, 1)

