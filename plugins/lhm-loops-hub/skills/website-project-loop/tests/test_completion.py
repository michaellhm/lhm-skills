import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('vault',Path(__file__).parents[1]/'scripts/shared_vault.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Vault:
    def __init__(self): self.text='- [ ] TEST-1 Produce homepage — Owner: Michael\n- [ ] TEST-2 Client approval — dependency: TEST-1\n- [ ] TEST-3 Build remaining pages — dependency: TEST-2\n';self.writes=0
    def read(self,path):return {'text':self.text}
    def write(self,path,before,after):
        if self.text!=before:raise ValueError('Changed')
        self.text=after;self.writes+=1;return 'verified-hash'

class CompletionTests(unittest.TestCase):
    def test_exact_item_preserves_approval_and_dependency(self):
        v=Vault();r=m.complete(v,'note','TEST-1','2026-10-10','https://evidence','https://discussion','Michael')
        self.assertEqual(r['state'],'verified');self.assertIn('- [x] TEST-1',v.text)
        self.assertIn('- [ ] TEST-2 Client approval',v.text);self.assertIn('- [ ] TEST-3 Build remaining pages',v.text)
        self.assertEqual(m.complete(v,'note','TEST-1','2026-10-10','https://evidence','https://discussion','Michael')['state'],'already_recorded')
        self.assertEqual(v.writes,1)
    def test_ambiguous_and_approval_are_blocked(self):
        for item in ['TEST','TEST-2','missing']:
            v=Vault()
            with self.assertRaises(ValueError):m.complete(v,'note',item,'2026-10-10','https://evidence','https://discussion','Michael')
            self.assertEqual(v.writes,0)
    def test_confirmed_next_action_replaces_stale_current_pointer(self):
        v=Vault();v.text='---\ntype: client-project\nupdated: 2026-10-01\n---\n'+v.text+'\nNext: Michael produces homepage\n'
        m.complete(v,'note','TEST-1','2026-10-10','https://evidence','https://discussion','Michael','Kristalyn reviews the homepage')
        self.assertIn('\nNext: Kristalyn reviews the homepage\n',v.text)
        self.assertNotIn('Next: Michael produces homepage',v.text)
        self.assertIn('updated: 2026-10-10',v.text)
        self.assertIn('- [ ] TEST-2 Client approval',v.text)

if __name__=='__main__':unittest.main()
