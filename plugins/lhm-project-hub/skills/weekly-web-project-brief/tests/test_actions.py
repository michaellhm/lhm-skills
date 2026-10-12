import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('quality_actions', Path(__file__).parents[1] / 'scripts/quality.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class ActionMappingTest(unittest.TestCase):
    def setUp(self):
        self.action = {'client': 'Example', 'text': 'Confirm the controlled test result', 'url': 'https://example.com/task/7'}
        self.brief = {'owners': [{'name': 'Michael', 'actions': [self.action]}]}
        self.selected = {'task_id': 7, 'client': 'Example', 'url': self.action['url'],
                         'action_owner': 'Michael', 'rendered_action': self.action['text'],
                         'selection_kind': 'prerequisite', 'dependency_state': 'unresolved'}
        self.boards = [{'owner': 'Michael', 'selected_actions': [self.selected]}]
        self.baseline = {'owners': [{'name': 'Michael', 'actions': [copy.deepcopy(self.action)]}]}
        self.disposition = {'owner': 'Michael', 'baseline_action': copy.deepcopy(self.action),
                            'disposition': 'prerequisite', 'reason': 'Launch remains gated on the controlled test',
                            'current_evidence_ids': ['evidence/current-task.json'],
                            'current_actions': [{'owner': 'Michael', 'action': copy.deepcopy(self.action)}]}
        self.comparison = {'action_dispositions': [self.disposition]}

    def check(self):
        q.validate_actions(self.brief, self.boards, self.baseline, self.comparison)

    def test_immediate_prerequisite_and_complete_ledger_pass(self):
        self.check()

    def test_selected_action_cannot_link_to_parent_instead(self):
        self.brief['owners'][0]['actions'][0]['url'] = 'https://example.com/parent/1'
        with self.assertRaisesRegex(ValueError, 'different task/owner'):
            self.check()

    def test_selected_action_cannot_move_to_another_owner(self):
        self.brief['owners'][0]['name'] = 'Aiya'
        with self.assertRaisesRegex(ValueError, 'different task/owner'):
            self.check()

    def test_selected_action_cannot_be_silently_shortened(self):
        self.brief['owners'][0]['actions'][0]['text'] = 'Review booking options'
        with self.assertRaisesRegex(ValueError, 'different task/owner'):
            self.check()

    def test_future_gated_execution_rejected(self):
        self.selected['selection_kind'] = 'execution'
        with self.assertRaisesRegex(ValueError, 'Future-gated'):
            self.check()

    def test_cleared_gate_allows_execution(self):
        self.selected.update(selection_kind='execution', dependency_state='clear')
        self.check()

    def test_all_baseline_actions_need_dispositions_including_one_off(self):
        self.baseline['owners'][0]['actions'].append('Verify the enquiry event due Friday')
        with self.assertRaisesRegex(ValueError, 'exactly one disposition'):
            self.check()
        self.comparison['action_dispositions'].append({**self.disposition,
            'baseline_action': 'Verify the enquiry event due Friday', 'disposition': 'completed'})
        self.check()

    def test_unsupported_completed_disposition_rejected(self):
        self.disposition.update(disposition='completed', current_evidence_ids=[])
        with self.assertRaisesRegex(ValueError, 'evidenced disposition'):
            self.check()

    def test_duplicate_or_invented_baseline_entries_rejected(self):
        self.comparison['action_dispositions'].append(copy.deepcopy(self.disposition))
        with self.assertRaisesRegex(ValueError, 'exactly one disposition'):
            self.check()
        self.comparison['action_dispositions'] = [{**self.disposition, 'owner': 'Aiya'}]
        with self.assertRaisesRegex(ValueError, 'exactly one disposition'):
            self.check()

    def test_coordination_uses_actual_action_owner(self):
        self.boards[0]['owner'] = 'Aiya'
        self.selected['task_assignee'] = 'Aiya'
        self.check()


    def test_unselected_rendered_action_rejected(self):
        self.brief['owners'][0]['actions'].append({'client': 'Other', 'text': 'Unexpected work', 'url': 'https://example.com/8'})
        with self.assertRaisesRegex(ValueError, 'Every rendered action'):
            self.check()

    def test_plain_text_cannot_hide_an_unverified_action(self):
        self.brief['owners'][0]['actions'].append('Publish the website now')
        with self.assertRaisesRegex(ValueError, 'unchecked prose'):
            self.check()
        self.brief['owners'][0]['actions'][-1] = 'No immediate action.'
        self.check()

    def test_completed_execution_rejected_but_review_followup_allowed(self):
        self.selected.update(status='Complete', selection_kind='execution', dependency_state='clear')
        with self.assertRaisesRegex(ValueError, 'Completed or cancelled'):
            self.check()
        self.selected.update(selection_kind='prerequisite')
        self.check()

    def test_retained_commitment_must_have_exact_visible_mapping(self):
        self.disposition.pop('current_actions')
        with self.assertRaisesRegex(ValueError, 'current_actions'):
            self.check()
        self.disposition['current_actions'] = [{'owner': 'Aiya', 'action': self.action}]
        with self.assertRaisesRegex(ValueError, 'absent or changed'):
            self.check()

    def test_archive_actions_and_composite_corrections_use_same_gate(self):
        for group in ('archive_action_dispositions', 'archive_correction_dispositions'):
            with self.subTest(group=group):
                self.comparison[group] = [{**self.disposition, 'current_actions': []}]
                with self.assertRaisesRegex(ValueError, 'current_actions'):
                    self.check()
                self.comparison.pop(group)

    def test_duplicate_rendered_and_selected_actions_rejected(self):
        self.brief['owners'][0]['actions'].append(copy.deepcopy(self.action))
        with self.assertRaisesRegex(ValueError, 'Duplicate rendered'):
            self.check()
        self.brief['owners'][0]['actions'].pop()
        self.boards[0]['selected_actions'].append(copy.deepcopy(self.selected))
        with self.assertRaisesRegex(ValueError, 'Duplicate selected'):
            self.check()

    def test_summary_computed_from_actual_final_actions(self):
        self.assertEqual(q.validate_actions(self.brief, self.boards, self.baseline, self.comparison),
                         {'count': 1, 'selected_count': 1, 'unique_task_urls': 1, 'unmatched': 0})


    def test_native_response_rejects_self_consistent_wrong_url_status_and_assignee(self):
        task={'id':7,'url':self.action['url'],'status':'Under Review',
              'assignee':{'firstName':'Aiya','lastName':'Test'}}
        self.selected.update(status='Under Review',task_assignee='Aiya Test',
                             ownership_basis='recommended coordination',source='Named review handoff')
        q.validate_task_bindings(self.boards,{'7':{'task':task}})
        for field,value in [('url','https://example.com/wrong'),('status','New'),('task_assignee','Michael')]:
            with self.subTest(field=field):
                original=self.selected[field];self.selected[field]=value
                with self.assertRaisesRegex(ValueError,'differs from native'):
                    q.validate_task_bindings(self.boards,{'7':{'task':task}})
                self.selected[field]=original
        self.selected.pop('ownership_basis')
        with self.assertRaisesRegex(ValueError,'recommended coordination'):
            q.validate_task_bindings(self.boards,{'7':{'task':task}})

    def test_actual_get_task_is_required_or_missing_card_disclosed(self):
        with self.assertRaisesRegex(ValueError,'actual worker get_task'):
            q.validate_task_bindings(self.boards,{})
        self.selected.update(missing_execution_task=True,gap_id='missing-card')
        with self.assertRaisesRegex(ValueError,'disclosed BasicOps'):
            q.validate_task_bindings(self.boards,{})
        q.validate_task_bindings(self.boards,{},[{'id':'missing-card','source':'basicops'}])

    def test_compound_given_name_and_native_orchestration_metadata(self):
        task={'id':7,'url':self.action['url'],'status':'Under Review',
              'assignee':{'firstName':'Michael Example','lastName':'Test'}}
        self.selected.update(status='Under Review',task_assignee='Michael Example Test')
        q.validate_task_bindings(self.boards,{'7':{'task':task}})
        task['assignee']={'firstName':'Aiya','lastName':'Test'}
        task['description']='<p>orchestration_owner=Michael; workflow_state=executing</p>'
        self.selected.update(task_assignee='Aiya Test',ownership_basis='Recorded orchestration owner',source='Native task metadata and named review handoff')
        q.validate_task_bindings(self.boards,{'7':{'task':task}})
        task['description']='<p>orchestration_owner=Michaelson;</p>'
        with self.assertRaisesRegex(ValueError,'recommended coordination'):
            q.validate_task_bindings(self.boards,{'7':{'task':task}})


if __name__ == '__main__':
    unittest.main()
