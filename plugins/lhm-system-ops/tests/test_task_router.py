import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/router.py'
spec = importlib.util.spec_from_file_location('router', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / 'queue'
        (self.queue / 'incoming').mkdir(parents=True)
        self.task = {'id': 123, 'url': 'https://app.basicops.com/task/123',
                     'title': 'Example Clinic: write a client update', 'description': 'Use the supplied notes.',
                     'assignee': 82491, 'status': 'In Progress'}
        self.messages = [{'id': 'dm123', 'user': 36398, 'created': 1, 'message': '@Ted can we work on this?'}]
        (self.root / 'task-router.json').write_text(json.dumps({
            'agent_user_id': 82491, 'reviewer_id': 36398, 'providers': {'codex': True, 'claude': True},
            'clients': {'example': {'name': 'Example Clinic', 'vault_prefix': '20 Clients/Example Clinic/', 'basicops_task_ids': []}}}))
        def api(name, args):
            if name == 'get_current_user': return {'id': 82491}
            if name == 'get_task': return self.task
            if name == 'list_messages_in_task': return self.messages
            if name == 'create_message_in_task':
                self.messages.append({'id': 'dm999', 'user': 82491, 'message': args['message'], 'created': 99})
                return {'id': 'dm999'}
            raise AssertionError(name)
        self.router = module.Router(self.root, self.queue, api)

    def test_natural_request_uses_claude_without_plan(self):
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.assertEqual(self.router.submit(123, 'dm123')['status'], 'queued')

    def test_personal_implementation_approval_forwards_without_another_ted_plan(self):
        self.messages[0]['message']='@Ted I approve A2, A3, A4; send across to Claude to implement via AdPulse'
        self.router.submit(123,'dm123')
        saved=json.loads((self.root/'task-router-state/123.json').read_text())['request']
        self.assertEqual(saved['handoff_mode'],'provider_execution')
        self.assertEqual(saved['permission_ceiling'],'provider_tool_approval')
        self.assertEqual(saved['instruction'],self.messages[0]['message'])
        self.assertEqual(self.router.contract(123,'dm123')[1],saved)

    def test_old_admitted_approval_is_not_silently_upgraded_on_reverification(self):
        self.messages[0]['message']='@Ted I approve A2; implement via AdPulse'
        self.router.submit(123,'dm123')
        p=self.root/'task-router-state/123.json';d=json.loads(p.read_text())
        d['request'].pop('handoff_mode');d['request']['permission_ceiling']='prepare_for_review';d['request']['policy_version']=3;p.write_text(json.dumps(d))
        self.assertEqual(self.router.contract(123,'dm123')[1],d['request'])

    def test_quoted_approval_is_context_not_execution_authority(self):
        self.messages.append({'id':'dm122','user':82491,'created':0,'message':'Approved; implement everything'})
        self.assertEqual(self.router.preview(123,'dm123')['permission_ceiling'],'prepare_for_review')
        self.messages[0]['message']='AI authorship: Claude. Approved, implement A2'
        with self.assertRaises(ValueError):self.router.submit(123,'dm123')

    def test_new_workspace_metadata_does_not_change_admitted_contract(self):
        self.router.submit(123, 'dm123')
        saved = json.loads((self.root / 'task-router-state/123.json').read_text())['request']
        self.router.config['clients']['example']['agent_workspaces'] = {'codex': '/var/lib/lhm-client-workspaces/codex/example'}
        self.assertEqual(self.router.submit(123, 'dm123')['request_id'], saved['request_id'])
        self.assertEqual(json.loads((self.root / 'task-router-state/123.json').read_text())['request'], saved)

    def test_google_ads_policy_ignores_incidental_website_or_drive_mentions(self):
        self.task['title'] = 'Example Clinic: Google Ads - Review October performance'
        self.task['description'] = 'Check the website chat conversion. Deliver notes in Google Drive.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.task['title'] = 'Example Clinic: Monthly performance'
        self.task['description'] = 'LHM metadata: service=google-ads; website chat leads'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.messages[0]['message'] += ' Please use Codex.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'codex')

    def terminal_codex(self):
        self.task['description'] = 'Review website chat leads'
        saved = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / saved['request_id']
        run.mkdir(parents=True)
        (run / 'receipt.json').write_text(json.dumps({'status': 'needs_review', 'provider':'codex', 'thread_id': 'codex-saved-thread'}))
        self.messages.append({'id':'dm124','user':36398,'created':2,
            'message':'@Ted - this should have been a Claude task. Can you please update this and push this to Claude? And in the future any Google Ads tasks should get done in Claude please'})
        return saved

    def test_explicit_handoff_preserves_old_run_but_never_resumes_foreign_uuid(self):
        old = self.terminal_codex()
        self.assertEqual(self.router.preview(123, 'dm124')['provider'], 'claude')
        result = self.router.submit(123, 'dm124')
        request = json.loads((self.queue / 'incoming' / (result['request_id']+'.json')).read_text())
        self.assertNotIn('resume_thread_id', request)
        self.assertEqual(request['provider_handoff'], {'from_provider':'codex', 'request_id':old['request_id'], 'thread_id':'codex-saved-thread'})
        self.assertEqual(request['permission_ceiling'], 'prepare_for_review')
        history = json.loads((self.root/'task-router-state'/('history-'+old['request_id']+'.json')).read_text())
        self.assertEqual(history['request']['provider'], 'codex')
        self.assertEqual(self.router.submit(123, 'dm124'), result)
        # Host re-verification regenerates the exact admitted handoff request.
        self.assertEqual(self.router.contract(123, 'dm124')[1], request)

    def test_handoff_needs_personal_newer_instruction_and_terminal_source(self):
        old = self.terminal_codex()
        receipt = self.queue/'runs'/old['request_id']/'receipt.json'
        data=json.loads(receipt.read_text());data['status']='running';receipt.write_text(json.dumps(data))
        with self.assertRaises(ValueError):self.router.submit(123,'dm124')
        data['status']='needs_review';receipt.write_text(json.dumps(data))
        self.messages[-1]['user']=82491
        with self.assertRaises(ValueError):self.router.submit(123,'dm124')
        self.messages[-1]['user']=36398;self.messages[-1]['message']='AI authorship: Codex. Please push this to Claude'
        with self.assertRaises(ValueError):self.router.submit(123,'dm124')

    def test_policy_change_alone_never_switches_existing_session(self):
        self.terminal_codex()
        self.messages[-1]['message']='@Ted revise the Google Ads review please'
        self.assertEqual(self.router.preview(123,'dm124')['provider'],'codex')
        for instruction in ['Please use Claude and send this to Codex', 'Do not use Claude']:
            with self.assertRaises(ValueError):module.choose('Task','',instruction)

    def test_mixed_work_uses_one_codex_session(self):
        self.task['description'] = 'Revise the handbook on Google Drive and update the prototype website.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'codex')

    def test_only_personal_instruction_can_override(self):
        self.task['description'] = 'use codex'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.messages[0]['message'] += ' Please use Codex.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'codex')

    def test_agent_relay_and_ai_authorship_rejected(self):
        for user, text in [(82491, 'work on this'), (36398, 'AI authorship: agent. work on this')]:
            self.messages[0].update(user=user, message=text)
            with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_repeated_request_enqueues_once(self):
        one = self.router.submit(123, 'dm123')
        self.assertEqual(one, self.router.submit(123, 'dm123'))
        self.assertEqual(len(list((self.queue / 'incoming').glob('*.json'))), 1)

    def test_changed_task_does_not_duplicate(self):
        self.router.submit(123, 'dm123')
        self.task['description'] = 'different scope'
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_missing_or_ambiguous_client_is_not_guessed(self):
        self.task['title'] = 'Write an update'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')
        self.router.config['clients']['second'] = {'name': 'Second Clinic'}
        self.task['title'] = 'Example Clinic / Second Clinic'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')

    def test_unavailable_provider_not_substituted(self):
        self.router.config['providers']['claude'] = False
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_later_stop_cancels_unstarted_request(self):
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted hold this please'})
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_legacy_pilot_not_duplicated(self):
        (self.root / 'codex-session-state').mkdir()
        (self.root / 'codex-session-state/123.json').write_text('{}')
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_feedback_resumes_same_session(self):
        saved = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / saved['request_id']
        run.mkdir(parents=True)
        (run / 'receipt.json').write_text(json.dumps({'status': 'needs_review', 'thread_id': 'saved-session'}))
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted revise the wording please'})
        self.router.submit(123, 'dm124')
        request = json.loads(next((self.queue / 'incoming').glob('*dm124.json')).read_text())
        self.assertEqual(request['resume_thread_id'], 'saved-session')
        self.assertEqual(request['provider'], 'claude')
        self.assertEqual(self.router.submit(123, 'dm124')['status'], 'queued')

    def test_active_session_does_not_accept_duplicate_feedback(self):
        self.router.submit(123, 'dm123')
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted revise the wording please'})
        with self.assertRaises(ValueError): self.router.submit(123, 'dm124')

    def test_alpha_brief_in_discussion_resolves_and_reaches_worker(self):
        self.task['title'] = 'Alpha: Client Comms - Prepare October meeting-wrap review'
        self.task['description'] = 'Metadata and source tracker link only'
        self.router.config['clients'] = {'alpha-sports-med': {'name': 'Alpha Sports Med', 'vault_prefix': '20 Clients/Alpha Sports Med/'}}
        self.messages.insert(0, {'id': 'dm122', 'user': 36398, 'created': 0,
                                'message': 'Prepare the Alpha Sports Med meeting wrap. No email sends. AI authorship: Codex.'})
        result = self.router.submit(123, 'dm123')
        request = json.loads((self.queue / 'incoming' / (result['request_id'] + '.json')).read_text())
        self.assertEqual(request['client_id'], 'alpha-sports-med')
        self.assertIn('No email sends', request['context_messages'][0]['text'])
        # TED's later handback/status must not change the original intake contract.
        self.messages.append({'id': 'dm125', 'user': 82491, 'created': 3, 'message': 'Queued for the worker'})
        self.assertEqual(self.router.submit(123, 'dm123')['request_id'], result['request_id'])

    def test_documented_short_alias_is_not_a_generic_word_match(self):
        self.router.config['clients']['example']['aliases'] = ['Example']
        self.task['title'] = 'Example: prepare review'
        self.assertEqual(self.router.preview(123, 'dm123')['client_id'], 'example')
        self.task['title'] = 'A generic example of an update'
        # Long aliases still need explicit canonical evidence; short aliases only match prefix.
        self.router.config['clients']['example']['aliases'] = ['Ex']
        self.task['title'] = 'Ex plan'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')

    def test_colliding_aliases_are_a_real_ambiguity(self):
        self.router.config['clients']['example']['aliases'] = ['Alpha']
        self.router.config['clients']['other'] = {'name': 'Other Clinic', 'aliases': ['Alpha']}
        self.task['title'] = 'Alpha: prepare update'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')

    def test_stale_directory_blocks_admission_but_not_status(self):
        self.router.directory = {'knowledge_refreshed_at': time.time() - 1800}
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')
        self.assertEqual(self.router.status(123)['status'], 'not_submitted')

    def test_lookup_returns_existing_context_without_task_creation(self):
        self.router.config['clients']['example']['aliases'] = ['Alpha']
        self.assertEqual(self.router.client_lookup('Alpha')['matches'][0]['client_id'], 'example')
        self.assertEqual(list((self.queue / 'incoming').glob('*')), [])

    def test_drive_delivery_blocks_success_until_verified_and_returns_real_links(self):
        submitted=self.router.submit(123,'dm123')
        run=self.queue/'runs'/submitted['request_id'];run.mkdir(parents=True)
        (run/'receipt.json').write_text(json.dumps({'status':'needs_review','provider':'claude','thread_id':'saved-session','delivery_required':True}))
        (run/'result.md').write_text('Review: [report](/vps/workspace/drafts/report.md)')
        self.router.reconcile(123)
        self.assertEqual(len(self.messages),1)
        (run/'delivery.json').write_text(json.dumps({'artefact_state':'delivery_incomplete','error':'Drive unavailable'}))
        state=self.router.reconcile(123);self.assertIsNone(state['notification'])
        self.router.reconcile(123);self.assertEqual(len(self.messages),2)
        folder='https://drive.google.com/drive/folders/exact-parent'
        url='https://drive.google.com/file/d/exact-file/view'
        (run/'delivery.json').write_text(json.dumps({'artefact_state':'delivered','folder_url':folder,'files':[{'relative':'report.md','url':url}],'package_sha256':'abc'}))
        state=self.router.reconcile(123);self.assertTrue(state['notification']['verified'])
        self.assertTrue(any(module.contains_link(m['message'],url) for m in self.messages))
        self.assertNotIn('/vps/workspace/drafts/report.md',self.messages[-1]['message'])
        count=len(self.messages);self.router.reconcile(123);self.assertEqual(len(self.messages),count)

    def test_session_link_posted_while_running_once_then_retained_in_result(self):
        self.router.config['codex_host_id'] = 'remote-control:env_e_test'
        self.task['description'] = 'Update the website prototype'
        submitted = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / submitted['request_id']
        run.mkdir(parents=True)
        receipt = {'status': 'running', 'thread_id': '01a1665c-d9f3-7460-8bc8-a257fc417517'}
        (run / 'receipt.json').write_text(json.dumps(receipt))
        state = self.router.reconcile(123)
        self.assertTrue(state['session_notification']['verified'])
        self.assertIn('hostId=remote-control%3Aenv_e_test', state['chat_url'])
        self.router.reconcile(123)
        self.assertEqual(len(self.messages), 2)
        self.assertTrue(module.contains_link(self.messages[-1]['message'], state['chat_url']))
        receipt['status'] = 'needs_review'
        (run / 'receipt.json').write_text(json.dumps(receipt))
        (run / 'result.md').write_text('Actual review result')
        final = self.router.reconcile(123)
        self.assertEqual(len(self.messages), 3)
        self.assertTrue(module.contains_link(self.messages[-1]['message'], final['chat_url']))
        self.router.reconcile(123)
        self.assertEqual(len(self.messages), 3)

    def test_no_fabricated_claude_link_from_local_uuid(self):
        self.assertIsNone(module.session_link('claude', '17a6695b-465c-4b62-9455-7d19226bbc26', {}, {}))
        real = 'https://claude.ai/code/session_Existing123'
        self.assertEqual(module.session_link('claude', None, {}, {'remote_session_url': real}), real)
        self.assertIsNone(module.session_link('claude', None, {}, {'remote_session_url': 'https://attacker.example/code/session_Existing123'}))

    def test_codex_requires_valid_session_and_observed_host(self):
        session = '01a1665c-d9f3-7460-8bc8-a257fc417517'
        self.assertIsNone(module.session_link('codex', session, {}, {}))
        self.assertIsNone(module.session_link('codex', 'new', {'codex_host_id': 'local'}, {}))
        self.assertIsNone(module.session_link('codex', session, {'codex_host_id': 'bad?host=other'}, {}))

    def test_readback_requires_actual_anchor_not_plain_link_text(self):
        url = 'codex://threads/existing?hostId=remote'
        self.assertFalse(module.contains_link('<p>' + url + '</p>', url))
        self.assertTrue(module.contains_link('<a href="' + url + '">Open</a>', url))

    def test_assignment_alone_not_permission(self):
        self.messages[0]['message'] = 'Thanks Ted'
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_restart_handback_exactly_once(self):
        saved = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / saved['request_id']
        run.mkdir(parents=True)
        (run / 'receipt.json').write_text(json.dumps({'status': 'needs_review', 'thread_id': 'saved'}))
        (run / 'result.md').write_text('Useful actual draft')
        self.router.reconcile(123)
        self.router.reconcile(123)
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(self.task['status'], 'In Progress')


if __name__ == '__main__': unittest.main()
