import json
import tempfile
import unittest
from pathlib import Path
from lhm_workflow.storage import Storage, StorageConfig

class Crash(RuntimeError): pass

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(); self.storage=Storage(StorageConfig.for_test(Path(self.temporary.name)/"state"))
    def tearDown(self): self.temporary.cleanup()
    def phases(self): return [json.loads(line)["phase"] for line in (self.storage.wal/"wf-1.jsonl").read_text().splitlines()]
    def test_fixed_production_paths(self):
        StorageConfig().validate()
        with self.assertRaises(ValueError): StorageConfig(Path("/tmp/not-production"),Path("/usr/local/libexec/lhm-workflow")).validate()
    def test_safe_id_rejects_traversal(self):
        with self.assertRaises(ValueError): self.storage.read_parent("../escape")
    def test_atomic_transaction_and_hash_binding(self):
        parent={"state":"intake","sequence":1}; self.storage.transact("wf-1",parent,expected_hash=None,tx_id="tx-1")
        self.assertEqual(self.storage.read_parent("wf-1"),parent); self.assertEqual(self.phases(),["prepared","applied","committed"])
        with self.assertRaises(ValueError): self.storage.transact("wf-1",{"state":"bad"},expected_hash=None,tx_id="tx-2")
    def test_reconcile_each_crash_boundary(self):
        for boundary in ("after_prepared","after_parent","after_applied"):
            with self.subTest(boundary=boundary):
                self.tearDown(); self.setUp(); target={"state":"testing","sequence":1}
                def fault(point):
                    if point==boundary: raise Crash(point)
                with self.assertRaises(Crash): self.storage.transact("wf-1",target,expected_hash=None,tx_id="tx-1",fault=fault)
                self.storage.reconcile("wf-1"); self.assertEqual(self.storage.read_parent("wf-1"),target); self.assertEqual(self.phases().count("committed"),1)
                self.storage.reconcile("wf-1"); self.assertEqual(self.phases().count("committed"),1)
    def test_reconcile_detects_conflicting_parent(self):
        def fault(point):
            if point=="after_prepared": raise Crash()
        with self.assertRaises(Crash): self.storage.transact("wf-1",{"state":"a"},expected_hash=None,tx_id="tx-1",fault=fault)
        self.storage.atomic_json(self.storage.parents/"wf-1.json",{"state":"foreign"})
        with self.assertRaisesRegex(RuntimeError,"hash conflict"): self.storage.reconcile("wf-1")
    def test_files_are_not_group_or_world_writable(self):
        self.storage.transact("wf-1",{"state":"ok"},expected_hash=None,tx_id="tx-1")
        self.assertEqual(self.storage.parents.joinpath("wf-1.json").stat().st_mode & 0o022,0); self.assertEqual(self.storage.wal.joinpath("wf-1.jsonl").stat().st_mode & 0o022,0)

if __name__=="__main__": unittest.main()
