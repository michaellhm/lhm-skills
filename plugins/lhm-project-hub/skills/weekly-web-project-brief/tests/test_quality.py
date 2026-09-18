import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('quality', Path(__file__).parents[1] / 'scripts/quality.py')
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)

class QualityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.p = Path(self.tmp.name)
        for n in ('source.txt', 'baseline.md', 'SKILL.md'): (self.p/n).write_text(n)
        self.write('email.json', {'html': '<table>approved</table>'})
        self.write('access-receipt.json', {'worker':'codex-cli','skill_path':str(self.p/'SKILL.md'),'skill_sha256':q.digest(self.p/'SKILL.md'),'sources':{k:{'status':'passed','evidence':'live read'} for k in ['gmail','obsidian','basicops']} | {'meetings':{'status':'not_required','reason':'No relevant meeting'}}})
        self.write('research-receipt.json', {'coverage':{**{k:{'status':'complete'} for k in ['gmail','obsidian','basicops']},'meetings':{'status':'not_required','reason':'No relevant meeting'}},'material_gaps':[],'evidence_files':[{'path':'source.txt','sha256':q.digest(self.p/'source.txt')}]})
        self.write('comparison.json', {'baseline':{'path':'baseline.md','sha256':q.digest(self.p/'baseline.md')},'projects':[{'project':'Example','disposition':'unchanged'}],'unresolved_regressions':[]})
        self.review()
    def write(self,n,d): (self.p/n).write_text(json.dumps(d))
    def change(self,n,fn):
        d=json.loads((self.p/n).read_text());fn(d);self.write(n,d);self.review()
    def review(self):
        self.write('quality-review.json',{'accepted':True,'reviewer':'controller','issues':[],**{k+'_sha256':q.digest(self.p/n) for k,n in [('email','email.json'),('research','research-receipt.json'),('comparison','comparison.json'),('access','access-receipt.json')]}})
    def test_complete_bound_report(self): self.assertEqual(q.validate(self.p)['state'],'quality_passed')
    def test_missing_live_email(self):
        self.change('access-receipt.json',lambda d:d['sources'].pop('gmail'))
        with self.assertRaisesRegex(ValueError,'Live worker read'):q.validate(self.p)
    def test_capped_board(self):
        self.change('research-receipt.json',lambda d:d['coverage']['basicops'].update(status='incomplete'))
        with self.assertRaisesRegex(ValueError,'Incomplete research'):q.validate(self.p)
    def test_missing_original_evidence(self):
        (self.p/'source.txt').unlink()
        with self.assertRaisesRegex(ValueError,'Evidence/baseline'):q.validate(self.p)
    def test_changed_payload_after_review(self):
        self.write('email.json',{'html':'changed'})
        with self.assertRaisesRegex(ValueError,'Review invalidated'):q.validate(self.p)
    def test_backward_stage_unresolved(self):
        self.change('comparison.json',lambda d:d.update(unresolved_regressions=['Old interview replaces newer approval']))
        with self.assertRaisesRegex(ValueError,'factual regression'):q.validate(self.p)
    def test_required_meeting_not_read(self):
        self.change('research-receipt.json',lambda d:d['coverage']['meetings'].update(status='complete'))
        with self.assertRaisesRegex(ValueError,'Live meeting read'):q.validate(self.p)
    def test_missing_meeting_reason(self):
        self.change('research-receipt.json',lambda d:d['coverage']['meetings'].pop('reason'))
        with self.assertRaisesRegex(ValueError,'Meeting coverage'):q.validate(self.p)

if __name__=='__main__':unittest.main()
