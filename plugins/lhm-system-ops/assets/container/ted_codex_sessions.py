#!/usr/bin/env python3
"""TED's bounded BasicOps-to-native-Codex pilot; no shell or credential tools."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re

PROFILE = Path('/opt/data/profiles/lhm_chief_of_staff')
QUEUE = Path('/opt/data/profiles/lhm_brain/dispatch/codex-pilot')
CONFIG = PROFILE / 'codex-session-pilot.json'
STATE = PROFILE / 'codex-session-state'
DELIVERIES = PROFILE / 'codex-session-deliveries'


def plain(value):
    return html.unescape(re.sub(r'<[^>]*>', ' ', str(value)))


def actor(value):
    user = value.get('user', value.get('userId', value.get('assignee')))
    return int(user.get('id', 0) if isinstance(user, dict) else user or 0)


def items(value):
    return value if isinstance(value, list) else value.get('data', [])


def atomic(path, value):
    temp = path.with_name('.' + path.name + '.' + str(os.getpid()) + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.chmod(0o640)
    os.replace(temp, path)


_proxy = None


def basicops(name, arguments):
    """Reuse TED's existing authenticated connector, never copying its tokens."""
    global _proxy
    if _proxy is None:
        spec = importlib.util.spec_from_file_location('ted_basicops_proxy', PROFILE / 'basicops_mcp_proxy.py')
        _proxy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_proxy)
    result = _proxy._rpc('tools/call', {'name': name, 'arguments': arguments})
    if result.get('isError'):
        raise ValueError('BasicOps ' + name + ' failed')
    _proxy._write_receipt(name, arguments, result)
    for block in result.get('content', []):
        if block.get('type') == 'text':
            try:
                return json.loads(block['text'])
            except json.JSONDecodeError:
                continue
    raise ValueError('BasicOps did not return a structured result')


class Bridge:
    def __init__(self, config=CONFIG, queue=QUEUE, state=STATE, api=basicops):
        self.config = json.loads(Path(config).read_text())
        self.queue, self.state, self.api = Path(queue), Path(state), api
        self.state.mkdir(exist_ok=True)

    def registration(self, task_id):
        if type(task_id) is not int or task_id <= 0:
            raise ValueError('A numeric BasicOps task ID is required')
        registration = self.config['tasks'].get(str(task_id))
        if not registration or not registration.get('enabled'):
            raise ValueError('Task is not registered for the Codex session pilot; retain the current route')
        if registration['client_id'] not in {'wellness-chiropractic', 'raise-the-bar'}:
            raise ValueError('Client is not enabled')
        if registration['client_id'] == 'raise-the-bar' and task_id != 2212824:
            raise ValueError('RTB editing is pinned to task 2212824')
        return registration

    def identity(self):
        current = self.api('get_current_user', {})
        if current.get('id') != self.config['agent_user_id']:
            raise ValueError('Connector identity is not verified TED')

    def messages(self, task_id):
        response = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
        if not isinstance(items(response), list):
            raise ValueError('Malformed BasicOps discussion')
        return items(response)

    def approved_contract(self, task_id, plan_message_id, approval_message_id):
        registration = self.registration(task_id)
        if not registration.get('ready', True):
            raise ValueError('The registered editing route is not ready; retain the task and report its dependencies')
        self.identity()
        task = self.api('get_task', {'taskId': task_id})
        project = task.get('project', {})
        project_id = project.get('id') if isinstance(project, dict) else project
        if task.get('id') != task_id or project_id != registration['project_id']:
            raise ValueError('BasicOps task or project binding mismatch')
        if actor(task) != self.config['agent_user_id'] or task.get('status') != 'In Progress':
            raise ValueError('TED must own the approved task in In Progress before dispatch')
        messages = self.messages(task_id)
        # Explicit human task instructions can be the contract themselves. No TED-authored
        # plan is required when this registered route has opted into direct intake.
        if plan_message_id == approval_message_id and registration.get('direct_task_intake'):
            instruction = next((m for m in messages if m.get('id') == approval_message_id), None)
            text = plain(instruction.get('message', '')) if instruction else ''
            if (not instruction or actor(instruction) != registration['reviewer_id']
                    or re.search(r'AI authorship\s*:', text, re.I)
                    or not re.search(r'\b(run|execute|update|revise|prepare|implement|work on|go ahead)\b', text, re.I)
                    or re.search(r"\b(do not|don't|never)\s+(run|execute|update|proceed)\b", text, re.I)):
                raise ValueError('Direct intake requires the registered human task instruction, not an agent relay')
            if not re.fullmatch(r'dm[1-9][0-9]*', instruction['id']):
                raise ValueError('Direct intake requires a durable BasicOps message ID')
            if registration['client_id'] != 'raise-the-bar':
                raise ValueError('Direct intake is not enabled for this client mode')
            objective = ('Human-directed RTB draft-edit task; interpret the requested work yourself.\n'
                         'Task: ' + task['title'] + '\nTask description: ' + plain(task.get('description', ''))
                         + '\nHuman instruction: ' + text
                         + '\nDeliver actual document/prototype review artifacts under the registered route. '
                         'Publishing, main pushes, deployment and client sends require explicit scoped permission; '
                         'this draft-edit route does not execute those actions.')
            if len(objective) > 8000:
                raise ValueError('Direct task exceeds the bounded context limit')
            return registration, task, instruction, instruction, int(instruction['id'][2:]), objective
        plans = [m for m in messages if actor(m) == self.config['agent_user_id']
                 and re.search(r'TED PLAN v\d+\s*[—-]\s*AWAITING APPROVAL', plain(m.get('message', '')))]
        if not plans:
            raise ValueError('No TED plan is recorded on this task')
        latest = max(plans, key=lambda m: m.get('created', 0))
        if latest.get('id') != plan_message_id:
            raise ValueError('Approval must bind the latest visible TED plan')
        approval = next((m for m in messages if m.get('id') == approval_message_id), None)
        if approval is None:
            replies = self.api('list_replies_in_message', {'messageId': plan_message_id})
            approval = next((m for m in items(replies) if m.get('id') == approval_message_id), None)
        text = plain(approval.get('message', '')) if approval else ''
        if (not approval or actor(approval) != registration['reviewer_id']
                or approval.get('created', 0) < latest.get('created', 0)
                or not re.search(r'\b(approve|approved|proceed|execute|go ahead)\b', text, re.I)
                or re.search(r"\b(do not|don't|never)\s+(approve|proceed|execute)\b", text, re.I)
                or re.search(r'AI authorship\s*:', text, re.I)):
            raise ValueError('A current approval by the registered human reviewer is required')
        version = int(re.search(r'TED PLAN v(\d+)', plain(latest['message'])).group(1))
        named_versions = re.findall(r'TED PLAN v(\d+)', text)
        if named_versions and any(int(v) != version for v in named_versions):
            raise ValueError('Approval refers to a different plan version')
        if not task.get('url'):
            raise ValueError('BasicOps task URL is missing')
        plan = plain(latest['message']).strip()
        if registration['client_id'] == 'wellness-chiropractic':
            if not re.search(r'saved.context', plan, re.I) or not re.search(r'review.only|read.only', plan, re.I):
                raise ValueError('Wellness accepts only saved-context, review-only plans')
        elif not re.search(r'draft.edit', plan, re.I) or not re.search(r'prototype', plan, re.I):
            raise ValueError('RTB requires an explicit draft-edit plan with prototype work, not a summary-only substitute')
        if len(plan) > 8000:
            raise ValueError('Pilot plan exceeds the bounded context limit')
        return registration, task, latest, approval, version, plan

    def submit_direct(self, task_id, instruction_message_id):
        return self.submit(task_id, instruction_message_id, instruction_message_id)

    def submit(self, task_id, plan_message_id, approval_message_id):
        registration, task, plan_message, approval, version, plan = self.approved_contract(
            task_id, plan_message_id, approval_message_id)
        request_id = f'ted-codex-{task_id}-v{version}'
        binding = {'task_id': task_id, 'task_url': task['url'], 'plan_version': version,
                   'plan_message_id': plan_message_id, 'approval_message_id': approval_message_id,
                   'plan_sha256': hashlib.sha256(plan_message['message'].encode()).hexdigest(),
                   'objective_sha256': hashlib.sha256(plan.encode()).hexdigest(),
                   'approval_sha256': hashlib.sha256(approval['message'].encode()).hexdigest(),
                   'reviewer_id': registration['reviewer_id'], 'project_id': registration['project_id']}
        request = {'schema_version': 1, 'request_id': request_id,
                   'client_id': registration['client_id'], 'task_type': 'ted_task',
                   'title': task['title'], 'objective': plan, 'basicops': binding}
        with (self.state / 'submit.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            mapping = self.state / f'{task_id}.json'
            if mapping.exists():
                prior = json.loads(mapping.read_text())
                if prior['request'] != request:
                    raise ValueError('Task already has a different registered plan; do not duplicate or replace it')
                return self.status(task_id)
            atomic(mapping, {'request': request, 'notification': None})
            try:
                atomic(self.queue / 'incoming' / (request_id + '.json'), request)
            except Exception:
                mapping.unlink()
                raise
        return self.status(task_id)

    def status(self, task_id):
        registration = self.registration(task_id)
        path = self.state / f'{task_id}.json'
        if not path.exists():
            return {'task_id': task_id, 'status': 'not_submitted', 'client_id': registration['client_id'],
                    'mode': registration.get('mode', 'saved_context_review'), 'ready': registration.get('ready', True)}
        mapping = json.loads(path.read_text())
        request = mapping['request']
        run = self.queue / 'runs' / request['request_id']
        receipt_path = run / 'receipt.json'
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {'status': 'queued'}
        rejection = self.queue / 'failed' / (request['request_id'] + '.json.error.json')
        if not receipt_path.exists() and rejection.exists():
            receipt = {'status': 'failed', 'error': json.loads(rejection.read_text()).get('reason', 'Worker rejected request')}
        if receipt_path.exists() and receipt.get('basicops') != request['basicops']:
            raise ValueError('Worker receipt does not match the approved BasicOps contract')
        result = {'task_id': task_id, 'task_url': request['basicops']['task_url'],
                  'request_id': request['request_id'], 'status': receipt['status'],
                  'chat_title': request['title'], 'host': 'hermes-vps',
                  'thread_id': receipt.get('thread_id'), 'error': receipt.get('error'),
                  'notification': mapping.get('notification')}
        session = run / 'session.json'
        if not result['thread_id'] and session.exists():
            result['thread_id'] = json.loads(session.read_text())['thread_id']
        if registration['client_id'] == 'raise-the-bar' and receipt['status'] == 'needs_review':
            delivery_path = DELIVERIES / (request['request_id'] + '.json')
            if not delivery_path.exists():
                result['status'] = 'awaiting_delivery'
            else:
                delivery = json.loads(delivery_path.read_text())
                if delivery.get('basicops') != request['basicops'] or delivery.get('artifacts') != receipt.get('artifacts'):
                    raise ValueError('RTB delivery does not match the approved run and artifacts')
                if delivery.get('verification') != 'passed':
                    result.update(status='failed', error=delivery.get('error', 'RTB delivery verification failed'))
                else:
                    result['deliverables'] = delivery['deliverables']
        if receipt['status'] == 'needs_review':
            result['result'] = (run / 'result.md').read_text()
        return result

    def reconcile_one(self, task_id):
        registration = self.registration(task_id)
        with (self.state / 'handback.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = self.status(task_id)
            if state['status'] not in {'needs_review', 'failed'} or (state.get('notification') or {}).get('work_state') == state['status']:
                return state
            self.identity()
            task = self.api('get_task', {'taskId': task_id})
            if task.get('status') in {'Complete', 'Cancelled', 'Decline'}:
                return {'task_id': task_id, 'status': 'human_closed_task_no_mutation'}
            if actor(task) not in {self.config['agent_user_id'], registration['reviewer_id']}:
                raise ValueError('Next owner changed; do not overwrite another handoff')
            marker = 'Codex session handback: ' + state['request_id']
            existing = next((m for m in self.messages(task_id)
                             if marker in plain(m.get('message', ''))
                             and actor(m) == self.config['agent_user_id']
                             and (state['status'] != 'needs_review' or 'Codex draft ready for review' in plain(m.get('message', '')))), None)
            if existing is None:
                summary = state.get('result', state.get('error') or 'Worker did not complete.')[:3000]
                heading = 'Codex draft ready for review' if state['status'] == 'needs_review' else 'Codex worker needs attention'
                boundary = ('This pilot used saved context only. No live account changes, client sends or Drive delivery were performed.'
                            if registration['client_id'] == 'wellness-chiropractic' else
                            ('RTB draft files and prototype source were prepared for review. No shared-site publication or client email was performed.'
                             if state['status'] == 'needs_review' else 'The run stopped before verified delivery. Inspect its receipt; no completed draft or publication is claimed.'))
                links = ''.join('<li><a href="' + html.escape(item['url'], quote=True) + '">'
                                + html.escape(item['name']) + '</a></li>' for item in state.get('deliverables', []))
                message = ('<p><strong>' + heading + '</strong></p><p>' + html.escape(summary) + '</p>'
                           '<p>Open the paired hermes-vps device in Codex. Chat: <strong>'
                           + html.escape(state['chat_title']) + '</strong>.</p>'
                           '<p>' + boundary + '</p><ul>' + links + '</ul>'
                           '<p>Next handoff: review the draft and continue in the same Codex conversation.</p>'
                           '<p><small>' + marker + ' | Session: ' + html.escape(state.get('thread_id') or 'unavailable')
                           + ' | AI authorship: Ted via the governed Codex session bridge.</small></p>')
                self.api('create_message_in_task', {'taskId': task_id, 'message': message})
                existing = next((m for m in self.messages(task_id)
                                 if marker in plain(m.get('message', ''))
                                 and actor(m) == self.config['agent_user_id']), None)
                if existing is None:
                    raise ValueError('BasicOps handback message readback failed')
            if state['status'] == 'needs_review':
                path = self.state / f'{task_id}.json'
                checkpoint = json.loads(path.read_text())
                if checkpoint.get('review_request') == 'attempting':
                    raise ValueError('Review request outcome is uncertain; inspect BasicOps before retrying')
                if not checkpoint.get('review_request'):
                    self.api('update_task', {'taskId': task_id, 'assignee': registration['reviewer_id']})
                    checkpoint['review_request'] = 'attempting'
                    atomic(path, checkpoint)
                    response = self.api('request_review', {'taskId': task_id,
                        'reviewers': [registration['reviewer_id']],
                        'message': '<p>Please review the Codex draft and any linked files in the task discussion.</p>'})
                    if response.get('success') is False:
                        raise ValueError('BasicOps review request failed; inspect before retrying')
                    checkpoint['review_request'] = 'requested'
                    atomic(path, checkpoint)
            next_status = 'Under Review' if state['status'] == 'needs_review' else 'Blocked'
            if next_status == 'Blocked':
                self.api('update_task', {'taskId': task_id, 'status': next_status,
                                         'assignee': registration['reviewer_id']})
            checked = self.api('get_task', {'taskId': task_id})
            if checked.get('status') != next_status or actor(checked) != registration['reviewer_id']:
                raise ValueError('BasicOps reviewer/status readback failed')
            path = self.state / f'{task_id}.json'
            mapping = json.loads(path.read_text())
            mapping['notification'] = {'message_id': existing['id'], 'verified': True,
                                       'work_state': state['status']}
            atomic(path, mapping)
            return self.status(task_id)


def run_mcp():
    import anyio
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    async def list_tools(_context, _params):
        schemas = [
            {'name': 'codex_task_submit', 'description': 'Send a registered human-directed task to Codex to interpret and execute within its configured scope, without a TED plan approval round trip.',
             'inputSchema': {'type': 'object', 'additionalProperties': False, 'required': ['task_id', 'instruction_message_id'],
                             'properties': {'task_id': {'type': 'integer'}, 'instruction_message_id': {'type': 'string'}}}},
            {'name': 'codex_session_submit', 'description': 'Send the latest human-approved, registered pilot plan to a persistent Codex chat. Never submits unapproved work.',
             'inputSchema': {'type': 'object', 'additionalProperties': False,
                             'required': ['task_id', 'plan_message_id', 'approval_message_id'],
                             'properties': {'task_id': {'type': 'integer'}, 'plan_message_id': {'type': 'string'},
                                            'approval_message_id': {'type': 'string'}}}},
            {'name': 'codex_session_status', 'description': 'Read the submitted task, conversation ID and checked worker result. A notifier returns terminal results to BasicOps.',
             'inputSchema': {'type': 'object', 'additionalProperties': False, 'required': ['task_id'],
                             'properties': {'task_id': {'type': 'integer'}}}},
        ]
        return types.ListToolsResult(tools=[types.Tool.model_validate(s) for s in schemas])

    async def call_tool(_context, params):
        try:
            bridge = Bridge()
            action = {'codex_task_submit': bridge.submit_direct, 'codex_session_submit': bridge.submit, 'codex_session_status': bridge.status}.get(params.name)
            if action is None:
                raise ValueError('Unknown Codex session tool')
            result = await anyio.to_thread.run_sync(lambda: action(**(params.arguments or {})))
            return types.CallToolResult(content=[types.TextContent(type='text', text=json.dumps(result))])
        except Exception as exc:
            return types.CallToolResult(isError=True, content=[types.TextContent(type='text', text=str(exc))])

    async def main():
        server = Server('ted-codex-sessions', on_list_tools=list_tools, on_call_tool=call_tool)
        async with stdio_server() as streams:
            await server.run(*streams, server.create_initialization_options())

    anyio.run(main)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reconcile', action='store_true')
    args = parser.parse_args()
    if args.reconcile:
        bridge = Bridge()
        for task_id, registration in bridge.config['tasks'].items():
            if registration.get('enabled'):
                result = bridge.reconcile_one(int(task_id))
                print(json.dumps({k: result.get(k) for k in ['task_id', 'status', 'notification']}))
    else:
        run_mcp()
