import importlib.util,tempfile,unittest,json
from datetime import datetime
from pathlib import Path
spec=importlib.util.spec_from_file_location('runtime',Path(__file__).parents[1]/'scripts/weekly_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class RuntimeTests(unittest.TestCase):
 def test_same_release_continuation_preserves_failed_run_and_stable_schedule(self):
  with tempfile.TemporaryDirectory() as d:
   cfg={'state':d,'commit':'a'*40};week='2026-11-16';base=week+'-catch-up-aaaaaaaa'
   p=Path(d)/'runtime'/base/'status.json';p.parent.mkdir(parents=True);p.write_text('{"state":"failed","error":"retain"}')
   key=r.run_key(cfg,week,'catch-up',base)
   self.assertNotEqual(key,base);self.assertRegex(key,r'^2026-11-16-catch-up-[0-9a-f]{8}$')
   self.assertEqual(json.loads(p.read_text())['error'],'retain')
   self.assertEqual(r.run_key(cfg,week,'scheduled',base),week)
   self.assertEqual(r.run_key(cfg,week,'catch-up'),base)
   p.write_text('{"state":"running"}')
   self.assertEqual(r.run_key(cfg,week,'catch-up',base),base)
 def test_only_failed_same_week_catch_up_can_continue(self):
  r.validate_continuation('catch-up','2026-11-16','2026-11-16-catch-up-1234abcd',{'state':'failed'})
  for mode,key,state in [('catch-up','2026-11-09-catch-up-1234abcd','failed'),('catch-up','2026-11-16-catch-up-1234abcd','delivered'),('scheduled','2026-11-16-catch-up-1234abcd','failed')]:
   with self.assertRaises(ValueError):r.validate_continuation(mode,'2026-11-16',key,{'state':state})
 def test_catch_up_authority_and_week_validation(self):
  at=datetime.fromisoformat('2026-11-21T10:00:00+11:00')
  self.assertEqual(r.validate_catch_up('2026-11-16',True,at),'2026-11-16')
  for week,authority in [('2026-11-16',False),('2026-11-17',True),('2026-11-23',True)]:
   with self.assertRaises(ValueError):r.validate_catch_up(week,authority,at)
  with self.assertRaises(ValueError):r.validate_request({'week':'2026-11-16','mode':'catch-up'},at)
 def test_existing_send_intent_blocks_catch_up_before_research(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'receipts').mkdir();(root/'receipts/2026-09-21-brief.json').write_text('{"state":"delivery_uncertain"}')
   with self.assertRaisesRegex(ValueError,'Existing production receipt'):
    r.run({'state':d},'2026-09-21','catch-up',authorised_catch_up=True)
 def test_completion_prompt_can_be_constructed(self):
  prompt=r.repair_prompt(Path('/skill'),Path('/output'))
  self.assertIn('{project: exact displayed name',prompt)
  self.assertIn('/output',prompt)
 def test_schedule_and_dst(self):
  for week,stamp in [('2026-09-21','2026-09-20T21:00:00+00:00'),('2026-10-05','2026-10-04T20:00:00+00:00')]:
   self.assertEqual(r.validate_request({'week':week,'mode':'scheduled'},datetime.fromisoformat(stamp)),week)
  for v in [{'week':'2026-09-21','mode':'test'},{'week':'2026-09-21','mode':'scheduled','command':'anything'}]:
   with self.assertRaises(ValueError):r.validate_request(v)
  with self.assertRaises(ValueError):r.validate_request({'week':'2026-09-21','mode':'scheduled'},datetime.fromisoformat('2026-09-21T03:00:00+00:00'))
 def test_no_source_mutation_or_shell(self):
  for action in ['gmail-send','vault-write','exec']:
   with self.assertRaises(ValueError):r.source_read({}, {'action':action,'value':'x'})
  with self.assertRaises(ValueError):r.source_read({}, {'action':'gmail-get','value':'x;cat /etc/passwd'})
  with self.assertRaises(ValueError):r.source_read({}, {'action':'gmail-search','value':'x','max':999})
  self.assertTrue(all(t.startswith(('get_','list_')) for t in r.READ_TOOLS))
 def test_retains_actual_source_results_and_binds_them(self):
  with tempfile.TemporaryDirectory() as d:
   work=Path(d);out=work/'output';out.mkdir()
   (out/'research-receipt.json').write_text(json.dumps({'evidence_files':[]}))
   records=[{'type':'item.completed','item':{'type':'mcp_tool_call','tool':'get_task','result':{'assignee':'Aiya','discussion':'Completed current work'}}},{'type':'item.completed','item':{'type':'command_execution','command':'python source_read.py gmail-get abc','aggregated_output':'Full email body'}},{'type':'item.completed','item':{'type':'command_execution','command':'cat SKILL.md','aggregated_output':'not source evidence'}}]
   (work/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in records))
   paths=r.retain_raw_reads(work,out);self.assertEqual(len(paths),1)
   self.assertEqual(len(json.loads(paths[0].read_text())['records']),2)
   receipt=json.loads((out/'research-receipt.json').read_text());self.assertEqual(receipt['evidence_files'][0]['sha256'],r.digest(paths[0]))
   r.retain_raw_reads(work,out);self.assertEqual(len(json.loads((out/'research-receipt.json').read_text())['evidence_files']),1)
   before=paths[0].read_bytes();records.append({'type':'item.completed','item':{'type':'mcp_tool_call','tool':'get_task','result':'New evidence'}})
   (work/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in records));r.retain_raw_reads(work,out)
   self.assertEqual(paths[0].read_bytes(),before)
   self.assertEqual(len(json.loads((out/'research-receipt.json').read_text())['evidence_files']),2)
 def test_vault_and_output_confinement(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'20 Clients').mkdir();(root/'20 Clients/test.md').write_text('source')
   self.assertEqual(r.source_read({'vault':d},{'action':'vault-read','value':'20 Clients/test.md'})['text'],'source')
   for name in ['../auth.json','/etc/passwd','config.yaml']:
    with self.assertRaises(ValueError):r.vault_path(root,name)
   (root/'20 Clients/escape.md').symlink_to('/etc/passwd')
   with self.assertRaises(ValueError):r.vault_path(root,'20 Clients/escape.md')
   with self.assertRaises(ValueError):list(r.safe_files(root))
if __name__=='__main__':unittest.main()
