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
                            'current_evidence_ids': ['evidence/current-task.json']}
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


if __name__ == '__main__':
    unittest.main()
