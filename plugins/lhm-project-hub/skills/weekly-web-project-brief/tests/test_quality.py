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
        self.write('baseline.md', {'owners': []})
        self.write('email.json', {'html': '<table>approved</table>'})
        self.write('access-receipt.json', {'worker':'codex-cli','skill_path':str(self.p/'SKILL.md'),'skill_sha256':q.digest(self.p/'SKILL.md'),'sources':{k:{'status':'passed','evidence':'live read'} for k in ['gmail','obsidian','basicops']} | {'meetings':{'status':'not_required','reason':'No relevant meeting'}}})
        self.write('research-receipt.json', {'coverage':{**{k:{'status':'complete'} for k in ['gmail','obsidian','basicops']},'meetings':{'status':'not_required','reason':'No relevant meeting'}},'material_gaps':[],'evidence_files':[{'path':'source.txt','sha256':q.digest(self.p/'source.txt')}]})
        self.write('comparison.json', {'baseline':{'path':'baseline.md','sha256':q.digest(self.p/'baseline.md')},'projects':[{'project':'Example','disposition':'unchanged'}],'unresolved_regressions':[]})
        self.write('inbox-review.json', {'boards':[{'owner':n,'board_id':1,'section_id':2,'status':'complete','terminal':True,'selected_actions':[]} for n in ['Michael','Kristalyn','Aiya']]})
        research=json.loads((self.p/'research-receipt.json').read_text());research['evidence_files'].append({'path':'inbox-review.json','sha256':q.digest(self.p/'inbox-review.json')});self.write('research-receipt.json',research)
        self.write('brief.json',{'projects':[{'name':'Example'}]})
        research=json.loads((self.p/'research-receipt.json').read_text());research['project_source_coverage']=[{'project':'Example',**{k:{'status':'complete','evidence':['source.txt']} for k in ('gmail','obsidian','basicops')}}];research['mechanical_action_check']=q.action_check(self.p);self.write('research-receipt.json',research)
        self.write('gmail-searches.json',{'searches':[{'query':'newer_than:30d Example','truncated':False}]})
        research=json.loads((self.p/'research-receipt.json').read_text())
        research['cutoff']='2026-09-21T08:00:00+10:00'
        index={'path':'gmail-searches.json','sha256':q.digest(self.p/'gmail-searches.json')}
        research['gmail_source_index']=index;research['evidence_files'].insert(0,index)
        research['project_source_coverage'][0]['gmail'].update(initial_query='newer_than:30d Example',followup_queries=[])
        self.write('research-receipt.json',research)
        self.review()
    def write(self,n,d): (self.p/n).write_text(json.dumps(d))
    def change(self,n,fn):
        d=json.loads((self.p/n).read_text());fn(d);self.write(n,d);self.review()
    def review(self):
        self.write('quality-review.json',{'accepted':True,'reviewer':'controller','issues':[],**{k+'_sha256':q.digest(self.p/n) for k,n in [('brief','brief.json'),('email','email.json'),('research','research-receipt.json'),('comparison','comparison.json'),('access','access-receipt.json')]}})
    def test_complete_bound_report(self): self.assertEqual(q.validate(self.p)['state'],'quality_passed')
    def test_research_check_never_replaces_delivery_review(self):
        (self.p/'quality-review.json').unlink()
        self.assertEqual(q.validate(self.p, require_review=False)['state'], 'research_passed')
        with self.assertRaises(FileNotFoundError): q.validate(self.p)
        self.change('research-receipt.json',lambda d:d['coverage']['gmail'].update(status='incomplete'))
        with self.assertRaisesRegex(ValueError,'Incomplete research'): q.validate(self.p, require_review=False)
    def test_all_sources_are_required_for_every_project(self):
        self.change('research-receipt.json',lambda d:d['project_source_coverage'][0]['obsidian'].update(evidence=[]))
        with self.assertRaisesRegex(ValueError,'Incomplete project source'):q.validate(self.p,require_review=False)
    def test_missing_project_cannot_be_hidden_by_complete_overall_coverage(self):
        self.write('brief.json',{'projects':[{'name':'Example'},{'name':'Missing'}]})
        with self.assertRaisesRegex(ValueError,'Per-project source coverage'):q.validate(self.p,require_review=False)
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
    def test_missing_inbox_owner(self):
        inbox=json.loads((self.p/'inbox-review.json').read_text());inbox['boards'].pop();self.write('inbox-review.json',inbox)
        self.change('research-receipt.json',lambda d:d['evidence_files'][-1].update(sha256=q.digest(self.p/'inbox-review.json')))
        with self.assertRaisesRegex(ValueError,'Three owner inbox'):q.validate(self.p)
    def test_inbox_capped(self):
        inbox=json.loads((self.p/'inbox-review.json').read_text());inbox['boards'][0]['terminal']=False;self.write('inbox-review.json',inbox)
        self.change('research-receipt.json',lambda d:d['evidence_files'][-1].update(sha256=q.digest(self.p/'inbox-review.json')))
        with self.assertRaisesRegex(ValueError,'Incomplete owner inbox'):q.validate(self.p)
    def test_inbox_unbound(self):
        self.change('research-receipt.json',lambda d:d['evidence_files'].pop())
        with self.assertRaisesRegex(ValueError,'Inbox review must'):q.validate(self.p)
    def test_missing_meeting_reason(self):
        self.change('research-receipt.json',lambda d:d['coverage']['meetings'].pop('reason'))
        with self.assertRaisesRegex(ValueError,'Meeting coverage'):q.validate(self.p)


    def test_stale_final_count_fails_even_with_accepted_review(self):
        self.change('research-receipt.json', lambda d:d['mechanical_action_check'].update(count=32))
        with self.assertRaisesRegex(ValueError, 'receipt missing or stale'):
            q.validate(self.p)

    def test_supplemental_owner_is_checked_and_counted(self):
        a={'client':'Example','text':'Verify current QA result','url':'https://example.com/task/9'}
        self.write('brief.json',{'projects':[{'name':'Example'}],'owners':[{'name':'Jaimee','actions':[a]}]})
        inbox=json.loads((self.p/'inbox-review.json').read_text())
        supplemental={'owner':'Jaimee','board_id':9,'section_id':3,'status':'complete','terminal':True,
                      'selected_actions':[{'action_owner':'Jaimee','client':a['client'],'url':a['url'],
                                           'rendered_action':a['text'],'selection_kind':'prerequisite','dependency_state':'unresolved',
                                           'task_id':9,'status':'Under Review','task_assignee':'Jaimee Test'}]}
        inbox['additional_owner_sweeps']=[supplemental];self.write('inbox-review.json',inbox)
        self.write('task-index.json',{'tasks':{'9':{'task':{'id':9,'url':a['url'],'status':'Under Review',
                                                                  'assignee':{'firstName':'Jaimee','lastName':'Test'}}}}})
        def bind(d):
            next(x for x in d['evidence_files'] if x['path']=='inbox-review.json')['sha256']=q.digest(self.p/'inbox-review.json')
            index={'path':'task-index.json','sha256':q.digest(self.p/'task-index.json')}
            d['task_source_index']=index
            if index not in d['evidence_files']:d['evidence_files'].append(index)
            d['mechanical_action_check']=q.action_check(self.p)
        self.change('research-receipt.json',bind)
        self.assertEqual(q.validate(self.p)['state'],'quality_passed')
        inbox['additional_owner_sweeps'][0]['terminal']=False;self.write('inbox-review.json',inbox)
        self.change('research-receipt.json',bind)
        with self.assertRaisesRegex(ValueError,'Incomplete owner inbox'):
            q.validate(self.p)

class SourceAuditTests(unittest.TestCase):
    def test_initial_window_and_actual_query_required(self):
        coverage=[{'project':'Example','gmail':{'initial_query':'newer_than:30d ExactClient','followup_queries':[]}}]
        q.validate_gmail_searches(coverage,[{'query':'newer_than:30d ExactClient','truncated':False}])
        for query in ['newer_than:14d ExactClient','newer_than:30d newer_than:14d ExactClient','newer_than:30d after:2026/10/10 ExactClient','newer_than:30d Unobserved']:
            coverage[0]['gmail']['initial_query']=query
            with self.assertRaises(ValueError):q.validate_gmail_searches(coverage,[{'query':'newer_than:30d ExactClient','truncated':False}])
    def test_capped_initial_needs_observed_terminal_followup(self):
        coverage=[{'project':'Example','gmail':{'initial_query':'newer_than:30d ExactClient','followup_queries':[]}}]
        reads=[{'query':'newer_than:30d ExactClient','truncated':True}]
        with self.assertRaises(ValueError):q.validate_gmail_searches(coverage,reads)
        coverage[0]['gmail']['followup_queries']=['newer_than:30d from:exact-client.test']
        with self.assertRaises(ValueError):q.validate_gmail_searches(coverage,reads)
        reads.append({'query':coverage[0]['gmail']['followup_queries'][0],'truncated':True})
        with self.assertRaises(ValueError):q.validate_gmail_searches(coverage,reads)
        reads[-1]['truncated']=False;q.validate_gmail_searches(coverage,reads)
    def test_future_cutoff_and_incorrect_inactivity_rejected(self):
        from datetime import datetime
        now=datetime.fromisoformat('2026-10-12T14:00:00+11:00')
        value={'cutoff':'2026-10-12T13:00:00+11:00','projects':[{'last_substantive_basicops_at':'2026-10-05T12:00:00+11:00','inactivity_days':7}]}
        q.validate_activity(value,now)
        value['projects'][0]['inactivity_days']=0
        with self.assertRaises(ValueError):q.validate_activity(value,now)
        value['projects'][0]['inactivity_days']=7;value['cutoff']='2026-10-12T14:15:00+11:00'
        with self.assertRaises(ValueError):q.validate_activity(value,now)
        value['cutoff']='2026-10-12T13:00:00'
        with self.assertRaises(ValueError):q.validate_activity(value,now)

if __name__=='__main__':unittest.main()
