import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/task-router'
sys.path.insert(0,str(SOURCE))
client=types.ModuleType('client_directory');client.refresh=lambda *args:None
spaces=types.ModuleType('workspaces');spaces.provision=lambda *args:None;spaces.publish_registry=lambda:None;spaces.location=lambda *args:None
with mock.patch.dict(sys.modules,{'client_directory':client,'workspaces':spaces}):
    spec=importlib.util.spec_from_file_location('feedback_dispatch',SOURCE/'dispatch.py')
    dispatch=importlib.util.module_from_spec(spec);spec.loader.exec_module(dispatch)


class DispatchTests(unittest.TestCase):
    def test_ready_pilot_never_relaunches_completion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);queue=root/'queue.sqlite'
            database=sqlite3.connect(queue)
            database.execute('CREATE TABLE batches (run_id TEXT,state TEXT,site TEXT)')
            database.execute("INSERT INTO batches VALUES ('ted-route-123-dm456','ready_for_review','luminary-counselling')")
            database.commit();database.close();queue.chmod(0o600)
            info=types.SimpleNamespace(st_mode=0o100600,st_uid=0,st_nlink=1)
            with mock.patch.object(dispatch,'FEEDBACK_QUEUE',queue),mock.patch.object(dispatch,'BASE',root/'missing'), \
                 mock.patch.object(Path,'lstat',return_value=info),mock.patch.object(dispatch.subprocess,'run') as runner:
                dispatch.feedback_completion_tick()
                runner.assert_not_called()

    def test_feedback_drafts_never_enter_ordinary_delivery_or_consume_slots(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();base=root/'base';work=root/'work';(base/'runs').mkdir(parents=True);work.mkdir()
            for n in range(1,5):
                ident=f'ted-route-{n}-dm1';queued=base/'runs'/ident;queued.mkdir();run=work/ident;run.mkdir()
                receipt={'status':'needs_review','delivery_required':True}
                request={'request_id':ident,'permission_ceiling':'registered_prototype_revision' if n<4 else 'prepare_for_review'}
                (queued/'receipt.json').write_text(json.dumps(receipt));(run/'request.json').write_text(json.dumps(request))
            delivery=types.ModuleType('delivery');delivery.deliver=mock.Mock()
            ordinary={'request_id':'ted-route-4-dm1','permission_ceiling':'prepare_for_review'}
            with mock.patch.dict(sys.modules,{'delivery':delivery}),mock.patch.object(dispatch,'BASE',base), \
                 mock.patch.object(dispatch,'WORK',work),mock.patch.object(dispatch,'verified',return_value=ordinary) as verify:
                dispatch.delivery_tick()
                verify.assert_called_once_with('ted-route-4-dm1')
                delivery.deliver.assert_called_once()
                self.assertEqual(delivery.deliver.call_args.args[0],ordinary)


if __name__=='__main__':unittest.main()
