import importlib.util,tempfile,unittest,json
from datetime import datetime
from pathlib import Path
spec=importlib.util.spec_from_file_location('runtime',Path(__file__).parents[1]/'scripts/weekly_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class RuntimeTests(unittest.TestCase):
 def test_schedule_and_dst(self):
  for week,stamp in [('2026-09-21','2026-09-21T02:00:00+00:00'),('2026-10-05','2026-10-05T01:00:00+00:00')]:
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
