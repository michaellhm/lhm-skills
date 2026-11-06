#!/usr/bin/env python3
"""Verify the exact private-prototype deployment through the existing GitHub MCP.

Run as codexworker in its existing Workspace MCP Python environment. No new
credential is read by the publisher, and this client can call only two read APIs.
"""
import argparse
import asyncio
import json
import os
import re
from pathlib import Path

CONFIG = Path('/home/codexworker/.codex/config.toml')
COMMAND = '/usr/local/libexec/lhm-github-mcp-launch'
OWNER, REPO = 'michaellhm', 'lhm-prototype'
WORKFLOW_ID = 289562388
WORKFLOW_NAME = 'Deploy to lhmstaging'
WORKFLOW_PATH = '.github/workflows/deploy.yml'
MAX_PAGES = 10
MAX_ATTEMPTS = 30


def validate_commit(commit):
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('exact commit SHA required')


def tool_arguments(name, arguments):
    """Closed read-only scope, independent of tools offered by the MCP server."""
    if not isinstance(arguments, dict) or arguments.get('owner') != OWNER or arguments.get('repo') != REPO:
        raise ValueError('deployment reader is restricted to the prototype repository')
    if name == 'actions_list':
        expected = {'method', 'owner', 'repo', 'resource_id', 'page', 'perPage', 'workflow_runs_filter'}
        if (set(arguments) != expected or arguments['method'] != 'list_workflow_runs'
                or arguments['resource_id'] != str(WORKFLOW_ID) or arguments['perPage'] != 100
                or type(arguments['page']) is not int or not 1 <= arguments['page'] <= MAX_PAGES
                or arguments['workflow_runs_filter'] != {'branch': 'main'}):
            raise ValueError('unapproved deployment list operation')
    elif name == 'actions_get':
        if (set(arguments) != {'method', 'owner', 'repo', 'resource_id'}
                or arguments['method'] != 'get_workflow_run'
                or not isinstance(arguments['resource_id'], str)
                or not re.fullmatch(r'[1-9][0-9]*', arguments['resource_id'])):
            raise ValueError('unapproved deployment get operation')
    else:
        raise ValueError('only workflow list/get reads are allowed')
    return arguments


def decode_result(result):
    if getattr(result, 'is_error', False) or getattr(result, 'isError', False):
        raise RuntimeError('GitHub deployment read failed')
    structured = getattr(result, 'structured_content', None) or getattr(result, 'structuredContent', None)
    if isinstance(structured, dict):
        return structured
    blocks = [block.text for block in result.content if getattr(block, 'type', None) == 'text']
    if len(blocks) != 1:
        raise ValueError('GitHub returned ambiguous deployment evidence')
    value = json.loads(blocks[0])
    if not isinstance(value, dict):
        raise ValueError('GitHub deployment evidence must be an object')
    return value


def validate_run(run, commit, run_id=None):
    validate_commit(commit)
    if not isinstance(run, dict) or type(run.get('id')) is not int or run['id'] <= 0:
        raise ValueError('real workflow run identity required')
    if (run_id is not None and run['id'] != run_id) or run.get('head_sha') != commit:
        raise ValueError('workflow run differs from the exact commit')
    if (run.get('workflow_id') != WORKFLOW_ID or run.get('name') != WORKFLOW_NAME
            or run.get('path') != WORKFLOW_PATH or run.get('head_branch') != 'main'):
        raise ValueError('workflow identity or branch differs from the registered deployment')
    if run.get('status') != 'completed':
        return None
    if run.get('conclusion') != 'success':
        raise RuntimeError('exact deployment workflow completed unsuccessfully')
    return {'id': run['id'], 'workflow_id': WORKFLOW_ID, 'name': WORKFLOW_NAME,
            'path': WORKFLOW_PATH, 'head_sha': commit, 'head_branch': 'main',
            'status': 'completed', 'conclusion': 'success',
            'html_url': f'https://github.com/{OWNER}/{REPO}/actions/runs/{run["id"]}'}


async def find_run(call, commit):
    validate_commit(commit)
    for page in range(1, MAX_PAGES + 1):
        arguments = {'method': 'list_workflow_runs', 'owner': OWNER, 'repo': REPO,
                     'resource_id': str(WORKFLOW_ID), 'page': page, 'perPage': 100,
                     'workflow_runs_filter': {'branch': 'main'}}
        result = await call('actions_list', tool_arguments('actions_list', arguments))
        rows = result.get('workflow_runs')
        if not isinstance(rows, list):
            raise ValueError('GitHub workflow list is incomplete')
        candidates = [row for row in rows if row.get('head_sha') == commit]
        if candidates:
            # A fresh authoritative read resolves rerun status, never list-summary inference.
            candidate = max(candidates, key=lambda row: (row.get('run_attempt', 0), row.get('id', 0)))
            identity = candidate.get('id')
            if type(identity) is not int or identity <= 0:
                raise ValueError('workflow list has invalid identity')
            arguments = {'method': 'get_workflow_run', 'owner': OWNER, 'repo': REPO,
                         'resource_id': str(identity)}
            actual = await call('actions_get', tool_arguments('actions_get', arguments))
            return validate_run(actual, commit, identity)
        if len(rows) < 100:
            return None
    raise ValueError('workflow pagination limit reached before exact deployment was found')


async def wait_for_deployment(call, commit, *, attempts=MAX_ATTEMPTS, delay=10, sleep=asyncio.sleep):
    validate_commit(commit)
    if type(attempts) is not int or not 1 <= attempts <= MAX_ATTEMPTS:
        raise ValueError('bounded deployment wait required')
    for attempt in range(attempts):
        result = await find_run(call, commit)
        if result is not None:
            return result
        if attempt + 1 < attempts:
            await sleep(delay)
    raise RuntimeError('exact deployment workflow is not yet verified')


class GithubDeployment:
    def __init__(self, config=CONFIG):
        self.config = Path(config)

    def parameters(self):
        import tomllib
        value = tomllib.loads(self.config.read_text())['mcp_servers']['github']
        if value.get('command') != COMMAND or value.get('args', []) != []:
            raise ValueError('GitHub connector launch differs from the existing approved route')
        environment = value.get('env', {})
        if not isinstance(environment, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in environment.items()):
            raise ValueError('invalid GitHub MCP environment')
        return {'command': COMMAND, 'args': [], 'env': {**os.environ, **environment}}

    async def _connected(self, operation):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        with open(os.devnull, 'w') as errors:
            async with stdio_client(StdioServerParameters(**self.parameters()), errlog=errors) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    catalog = await session.list_tools()
                    if not {'actions_list', 'actions_get'} <= {tool.name for tool in catalog.tools}:
                        raise ValueError('GitHub workflow read tools are not available')
                    async def call(name, arguments):
                        result = await session.call_tool(name, tool_arguments(name, arguments))
                        return decode_result(result)
                    return await operation(call)

    async def verify(self, commit):
        validate_commit(commit)
        return await self._connected(lambda call: wait_for_deployment(call, commit))

    async def preflight(self):
        async def operation(call):
            arguments = {'method': 'list_workflow_runs', 'owner': OWNER, 'repo': REPO,
                         'resource_id': str(WORKFLOW_ID), 'page': 1, 'perPage': 100,
                         'workflow_runs_filter': {'branch': 'main'}}
            result = await call('actions_list', tool_arguments('actions_list', arguments))
            if not isinstance(result.get('workflow_runs'), list):
                raise ValueError('GitHub deployment read preflight returned incomplete evidence')
            return {'status': 'ready', 'repository': OWNER + '/' + REPO, 'workflow_id': WORKFLOW_ID}
        return await self._connected(operation)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--commit')
    mode.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    client = GithubDeployment()
    result = asyncio.run(client.preflight() if args.preflight else client.verify(args.commit))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
