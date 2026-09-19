import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('knowledge',Path(__file__).parents[1]/'scripts/knowledge_drive.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
class KnowledgeTests(unittest.TestCase):
 def test_only_verified_shared_ancestry_is_exposed(self):
  rows=[{'id':'c','name':'20 Clients','parents':[k.DRIVE]},{'id':'a','name':'Alpha','parents':['c']},{'id':'n','name':'Current Projects.md','parents':['a']},{'id':'p','name':'Private','parents':[k.DRIVE]},{'id':'x','name':'Secret.md','parents':['p']},{'id':'e','name':'Escape.md','parents':['outside']}]
  paths=k.paths_from_files(rows);self.assertIn('20 Clients/Alpha/Current Projects.md',paths);self.assertEqual(len(paths),3)
  with self.assertRaises(ValueError):k.paths_from_files(rows+[{'id':'duplicate','name':'Current Projects.md','parents':['a']}])
if __name__=='__main__':unittest.main()
