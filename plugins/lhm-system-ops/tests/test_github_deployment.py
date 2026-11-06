import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / 'assets/task-router/github_deployment.py'
spec = importlib.util.spec_from_file_location('github_deployment', PATH)
github = importlib.util.module_from_spec(spec)
spec.loader.exec_module(github)
SHA = 'a' * 40


def run(**updates):
    value = {'id': 123, 'head_sha': SHA, 'workflow_id': github.WORKFLOW_ID,
             'name': github.WORKFLOW_NAME, 'path': github.WORKFLOW_PATH,
             'head_branch': 'main', 'status': 'completed', 'conclusion': 'success'}
    value.update(updates)
    return value


class DeploymentTests(unittest.TestCase):
    def test_exact_success(self):
        result = github.validate_run(run(), SHA, 123)
        self.assertEqual(result['id'], 123)
        self.assertEqual(result['head_sha'], SHA)
        self.assertEqual(result['html_url'], 'https://github.com/michaellhm/lhm-prototype/actions/runs/123')

    def test_wrong_commit_run_workflow_path_name_or_branch(self):
        for updates in ({'head_sha': 'b'*40}, {'id': 124}, {'workflow_id': 1},
                        {'path': '.github/workflows/other.yml'}, {'name': 'Other'},
                        {'head_branch': 'feature'}, {'id': 0}, {'id': True}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                github.validate_run(run(**updates), SHA, 123)

    def test_commit_is_closed_sha(self):
        for value in ('main', 'A'*40, '../escape', '', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                github.validate_commit(value)

    def test_pending_is_not_success_and_failure_fails(self):
        self.assertIsNone(github.validate_run(run(status='in_progress', conclusion=None), SHA))
        for conclusion in ('failure', 'cancelled', 'timed_out', 'neutral', 'skipped', None):
            with self.subTest(conclusion=conclusion), self.assertRaises(RuntimeError):
                github.validate_run(run(conclusion=conclusion), SHA)

    def test_list_then_authoritative_get(self):
        calls = []
        async def call(name, args):
            calls.append((name, args))
            return {'workflow_runs': [run(status='queued', conclusion=None)]} if name == 'actions_list' else run()
        result = asyncio.run(github.find_run(call, SHA))
        self.assertEqual(result['id'], 123)
        self.assertEqual([c[0] for c in calls], ['actions_list', 'actions_get'])
        self.assertEqual(calls[0][1]['workflow_runs_filter'], {'branch': 'main'})

    def test_get_mismatch_cannot_inherit_list_success(self):
        async def call(name, args):
            return {'workflow_runs': [run()]} if name == 'actions_list' else run(head_sha='b'*40)
        with self.assertRaises(ValueError): asyncio.run(github.find_run(call, SHA))

    def test_pagination_finds_exact_commit(self):
        pages = []
        async def call(name, args):
            if name == 'actions_get': return run()
            pages.append(args['page'])
            return {'workflow_runs': [run(head_sha='b'*40)] * 100} if args['page'] == 1 else {'workflow_runs': [run()]}
        self.assertEqual(asyncio.run(github.find_run(call, SHA))['id'], 123)
        self.assertEqual(pages, [1, 2])

    def test_missing_or_truncated_list_not_success(self):
        async def missing(name, args): return {'workflow_runs': []}
        self.assertIsNone(asyncio.run(github.find_run(missing, SHA)))
        async def bad(name, args): return {'message': 'truncated'}
        with self.assertRaises(ValueError): asyncio.run(github.find_run(bad, SHA))

    def test_bounded_pagination_never_guesses(self):
        async def call(name, args): return {'workflow_runs': [run(head_sha='b'*40)] * 100}
        with self.assertRaisesRegex(ValueError, 'pagination'): asyncio.run(github.find_run(call, SHA))

    def test_pending_poll_retries_and_exhaustion_stays_unverified(self):
        counts = {'gets': 0}
        async def call(name, args):
            if name == 'actions_list': return {'workflow_runs': [run()]}
            counts['gets'] += 1
            return run(status='queued', conclusion=None) if counts['gets'] == 1 else run()
        sleeps = []
        async def sleep(delay): sleeps.append(delay)
        self.assertEqual(asyncio.run(github.wait_for_deployment(call, SHA, attempts=2, sleep=sleep))['id'], 123)
        self.assertEqual(sleeps, [10])
        async def none(name, args): return {'workflow_runs': []}
        with self.assertRaisesRegex(RuntimeError, 'not yet verified'):
            asyncio.run(github.wait_for_deployment(none, SHA, attempts=2, sleep=sleep))

    def test_only_two_fixed_repository_reads(self):
        valid = {'method': 'get_workflow_run', 'owner': github.OWNER, 'repo': github.REPO, 'resource_id': '123'}
        self.assertEqual(github.tool_arguments('actions_get', valid), valid)
        for name, args in [('actions_run_trigger', valid), ('actions_get', {**valid, 'method': 'get_workflow'}),
                           ('actions_get', {**valid, 'owner': 'other'}), ('actions_get', {**valid, 'repo': 'other'}),
                           ('actions_get', {**valid, 'resource_id': '../x'}), ('actions_get', {**valid, 'extra': True})]:
            with self.subTest(name=name, args=args), self.assertRaises(ValueError):
                github.tool_arguments(name, args)

    def test_closed_list_fields(self):
        valid = {'method': 'list_workflow_runs', 'owner': github.OWNER, 'repo': github.REPO,
                 'resource_id': str(github.WORKFLOW_ID), 'page': 1, 'perPage': 100,
                 'workflow_runs_filter': {'branch': 'main'}}
        self.assertEqual(github.tool_arguments('actions_list', valid), valid)
        for change in ({'resource_id': '1'}, {'page': 0}, {'page': 11}, {'page': True},
                       {'workflow_runs_filter': {'branch': 'other'}}, {'perPage': 101}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                github.tool_arguments('actions_list', {**valid, **change})

    def test_existing_config_without_secret_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'config.toml'
            path.write_text('[mcp_servers.github]\ncommand="'+github.COMMAND+'"\n[mcp_servers.github.env]\nEXISTING_ROUTE="preserved"\n')
            params = github.GithubDeployment(path).parameters()
            self.assertEqual(params['command'], github.COMMAND)
            self.assertEqual(params['args'], [])
            self.assertEqual(params['env']['EXISTING_ROUTE'], 'preserved')
            path.write_text('[mcp_servers.github]\ncommand="unapproved"\n')
            with self.assertRaises(ValueError): github.GithubDeployment(path).parameters()

    def test_preflight_reads_registered_workflow_without_inventing_success(self):
        client = github.GithubDeployment()
        seen = []
        async def connected(operation):
            async def call(name, arguments):
                seen.append((name, arguments));return {'workflow_runs': []}
            return await operation(call)
        with mock.patch.object(client, '_connected', side_effect=connected):
            result = asyncio.run(client.preflight())
        self.assertEqual(result, {'status':'ready','repository':'michaellhm/lhm-prototype','workflow_id':github.WORKFLOW_ID})
        self.assertEqual(seen[0][0], 'actions_list')
        self.assertNotIn('conclusion', result)
        async def malformed(operation):
            async def call(name, arguments): return {'error':'not permitted'}
            return await operation(call)
        with mock.patch.object(client, '_connected', side_effect=malformed), self.assertRaises(ValueError):
            asyncio.run(client.preflight())

    def test_sdk_snakecase_error_and_text_decode(self):
        with self.assertRaises(RuntimeError):
            github.decode_result(types.SimpleNamespace(is_error=True))
        value = types.SimpleNamespace(is_error=False, content=[types.SimpleNamespace(type='text', text=json.dumps(run()))])
        self.assertEqual(github.decode_result(value), run())
        value.content.append(types.SimpleNamespace(type='text', text='{}'))
        with self.assertRaises(ValueError): github.decode_result(value)


if __name__ == '__main__': unittest.main()
