import unittest
from lhm_workflow.workflow import STAGES,accept_receipt,issue_current,new_workflow

def artifact(name,n): return {"artifact_id":name,"sha256":str(n)*64,"media_type":"application/json"}
def receipt(parent,contract,outputs,inputs=None,worker=None):
 return {"schema_version":1,"receipt_id":"receipt-"+contract["stage_id"],"workflow_id":contract["workflow_id"],"parent_run_id":contract["parent_run_id"],"stage_id":contract["stage_id"],"child_run_id":contract["child_run_id"],"idempotency_key":contract["idempotency_key"],"worker":worker or contract["worker"],"input_artifacts":contract["input_artifacts"] if inputs is None else inputs,"output_artifacts":outputs,"disposition":"verified"}

class WorkflowTests(unittest.TestCase):
 def test_complete_fixed_sequence_and_hash_dependencies(self):
  parent=new_workflow("parent-1","Improve LHM SEO")
  outputs=[artifact("seo-pack",1),artifact("content",2),artifact("site-receipt",3)]
  for index,spec in enumerate(STAGES):
   parent,contract=issue_current(parent,f"child-{index}"); self.assertEqual(contract["stage_id"],spec["id"]); self.assertEqual(contract["worker"],spec["worker"])
   if index: self.assertEqual(contract["input_artifacts"],[outputs[index-1]])
   parent=accept_receipt(parent,receipt(parent,contract,[outputs[index]]))
  self.assertEqual(parent["state"],"review_ready"); self.assertIsNone(parent["current_stage"])
 def test_cannot_issue_downstream_early(self):
  parent=new_workflow("parent-1","SEO")
  with self.assertRaises(ValueError): issue_current({**parent,"current_stage":"content"},"child-x")
 def test_rejects_changed_dependency_hash(self):
  parent=new_workflow("parent-1","SEO"); parent,c=issue_current(parent,"seo-child"); parent=accept_receipt(parent,receipt(parent,c,[artifact("seo-pack",1)])); parent,c=issue_current(parent,"content-child")
  with self.assertRaisesRegex(ValueError,"dependency"): accept_receipt(parent,receipt(parent,c,[artifact("content",2)],inputs=[artifact("seo-pack",9)]))
 def test_rejects_wrong_worker(self):
  parent=new_workflow("parent-1","SEO"); parent,c=issue_current(parent,"seo-child")
  with self.assertRaisesRegex(ValueError,"worker"): accept_receipt(parent,receipt(parent,c,[artifact("seo-pack",1)],worker={"runtime":"claude","identity":"wrong"}))
 def test_contract_is_deterministic(self):
  parent=new_workflow("parent-1","SEO"); _,a=issue_current(parent,"child-1"); _,b=issue_current(parent,"child-1"); self.assertEqual(a,b)

if __name__=="__main__": unittest.main()
