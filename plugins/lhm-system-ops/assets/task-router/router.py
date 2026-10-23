"""Deterministic provider policy and human-bound, idempotent TED intake."""
import fcntl
import hashlib
import html
import json
from pathlib import Path
import re

POLICY_VERSION = 1
TERMINAL = {'needs_review', 'failed'}


def plain(value):
    return html.unescape(re.sub(r'<[^>]*>', ' ', str(value)))


def actor(value):
    user = value.get('user', value.get('userId', value.get('assignee')))
    return int(user.get('id', 0) if isinstance(user, dict) else user or 0)


def atomic(path, value):
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def choose(title, description, instruction):
    """Only the verified human instruction can override the provider."""
    overrides = re.findall(r'\b(?:use|send (?:this |it )?to|run (?:this |it )?(?:in|with))\s+(codex|claude)\b', instruction, re.I)
    if len(set(s.lower() for s in overrides)) > 1:
        raise ValueError('Conflicting provider instructions; one provider is required')
    if overrides:
        return overrides[-1].lower(), 'Explicit human provider selection'
    text = ' '.join([title, description, instruction]).lower()
    if re.search(r'\b(website|prototype|github|repository|repo|code|html|css|javascript|astro|wordpress|deploy|staging|google docs|google drive|g drive|workspace|gmail|spreadsheet)\b', text):
        return 'codex', 'Website/code or connected Workspace work; keep mixed deliverables together'
    return 'claude', 'Research, writing, analysis or planning; local draft for review'


def resolve_client(task, clients):
    # Prefer exact pre-existing task bindings. Never trust a model-supplied path/slug.
    exact = [key for key, value in clients.items() if str(task['id']) in [str(i) for i in value.get('basicops_task_ids', [])]]
    if len(exact) == 1:
        return exact[0]
    title = plain(task['title']).casefold()
    named = [key for key, value in clients.items()
             if re.search(r'(?<!\w)' + re.escape(value['name'].casefold()) + r'(?!\w)', title)]
    if re.search(r'(?<!\w)rtb(?!\w)', title) and 'raise-the-bar' in clients:
        named = list(set(named + ['raise-the-bar']))
    if len(exact) > 1:
        raise ValueError('Conflicting registered task bindings')
    if not named:
        description = plain(task.get('description', '')).casefold()
        named = [key for key, value in clients.items() if re.search(r'(?<!\w)' + re.escape(value['name'].casefold()) + r'(?!\w)', description)]
    if len(named) != 1:
        raise ValueError('Client is missing or ambiguous. Resolve the existing handback target before dispatch; do not guess a folder')
    return named[0]


class Router:
    def __init__(self, profile, queue, api):
        self.profile, self.queue, self.api = Path(profile), Path(queue), api
        self.config = json.loads((self.profile / 'task-router.json').read_text())
        self.state = self.profile / 'task-router-state'
        self.state.mkdir(exist_ok=True)

    def contract(self, task_id, instruction_message_id):
        if type(task_id) is not int or task_id <= 0 or not re.fullmatch(r'dm[1-9][0-9]*', instruction_message_id):
            raise ValueError('Exact task and durable human instruction IDs are required')
        if self.api('get_current_user', {}).get('id') != self.config['agent_user_id']:
            raise ValueError('TED connector identity mismatch')
        task = self.api('get_task', {'taskId': task_id})
        if task.get('id') != task_id or not task.get('url', '').startswith('https://app.basicops.com/'):
            raise ValueError('Task identity or URL mismatch')
        response = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
        messages = response if isinstance(response, list) else response.get('data', [])
        msg = next((m for m in messages if m.get('id') == instruction_message_id), None)
        instruction = plain(msg.get('message', '')) if msg else ''
        if (not msg or actor(msg) != self.config['reviewer_id']
                or re.search(r'AI authorship\s*:', instruction, re.I)
                or not re.search(r'\b(work on|run|execute|prepare|write|draft|research|investigate|update|revise|implement|go ahead|proceed|approve)\b', instruction, re.I)
                or re.search(r"\b(do not|don't|never|stop|cancel|hold|pause)\b", instruction, re.I)):
            raise ValueError('A direct personal work request is required; assignment, relay or a stop is not permission')
        if task.get('status') in {'Complete', 'Cancelled', 'Decline'}:
            raise ValueError('Task is closed')
        if any(actor(m) == self.config['reviewer_id'] and m.get('created', 0) > msg.get('created', 0)
               and re.search(r'\b(stop|cancel|hold|pause)\b', plain(m.get('message', '')), re.I) for m in messages):
            raise ValueError('A later human stop/hold supersedes this instruction')
        client = resolve_client(task, self.config['clients'])
        provider, reason = choose(plain(task['title']), plain(task.get('description', '')), instruction)
        existing = self.state / f'{task_id}.json'
        resume = None
        if existing.exists():
            old = json.loads(existing.read_text())['request']
            if old['instruction_message_id'] == instruction_message_id:
                resume = old.get('resume_thread_id')
            else:
                status = self.status(task_id)
                if status['status'] not in TERMINAL or not status.get('thread_id'):
                    raise ValueError('Existing session is active or unavailable; inspect its status before adding feedback')
                if int(instruction_message_id[2:]) <= int(old['instruction_message_id'][2:]):
                    raise ValueError('Feedback must be a newer personal instruction')
                resume = status['thread_id']
            # Keep follow-ups with their provider unless a human explicitly asks otherwise.
            explicit = re.search(r'\b(?:use|send (?:this |it )?to|run (?:this |it )?(?:in|with))\s+(codex|claude)\b', instruction, re.I)
            if explicit and provider != old['provider']:
                raise ValueError('Changing provider requires a new task; do not split an existing conversation')
            provider = old['provider']
            reason = old['reason'] if old['instruction_message_id'] == instruction_message_id else 'Continue the existing ' + provider + ' session'
        if not self.config['providers'].get(provider, False):
            raise ValueError(provider + ' is unavailable; no silent provider substitution')
        target = self.config['clients'][client]
        request = {'schema_version': 1, 'policy_version': POLICY_VERSION,
                   'request_id': f'ted-route-{task_id}-{instruction_message_id}',
                   'task_id': task_id, 'task_url': task['url'], 'title': plain(task['title'])[:160],
                   'description': plain(task.get('description', ''))[:16000],
                   'instruction': instruction, 'instruction_message_id': instruction_message_id,
                   'instruction_sha256': hashlib.sha256(msg['message'].encode()).hexdigest(),
                   'client_id': client, 'client': target, 'provider': provider, 'reason': reason,
                   'reviewer_id': self.config['reviewer_id'],
                   'permission_ceiling': 'prepare_for_review'}
        if resume:
            request['resume_thread_id'] = resume
        if len(json.dumps(request).encode()) > 28000:
            raise ValueError('Task context too large; supply a bounded brief')
        return task, request

    def preview(self, task_id, instruction_message_id):
        _, request = self.contract(task_id, instruction_message_id)
        return {k: request[k] for k in ['task_id', 'task_url', 'client_id', 'provider', 'reason', 'permission_ceiling']}

    def submit(self, task_id, instruction_message_id):
        task, request = self.contract(task_id, instruction_message_id)
        # Existing pilot chats are deliberately preserved instead of starting duplicate production.
        legacy = self.profile / 'codex-session-state' / f'{task_id}.json'
        if legacy.exists():
            raise ValueError('This task already has a pilot Codex session. Continue that chat; use a new task for the central route')
        if actor(task) != self.config['agent_user_id'] or task.get('status') != 'In Progress':
            raise ValueError('Claim the task for TED in In Progress before submitting')
        with (self.state / 'submit.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            path = self.state / f'{task_id}.json'
            if path.exists():
                old = json.loads(path.read_text())
                if old['request'] == request:
                    return self.status(task_id)
                if old['request']['instruction_message_id'] == instruction_message_id or not request.get('resume_thread_id'):
                    raise ValueError('Existing instruction changed; do not duplicate or replace work')
                if old['request']['client_id'] != request['client_id']:
                    raise ValueError('Follow-up cannot change the client')
                atomic(self.state / ('history-' + old['request']['request_id'] + '.json'), old)
            previous = path.read_text() if path.exists() else None
            atomic(path, {'request': request, 'notification': None})
            try:
                atomic(self.queue / 'incoming' / (request['request_id'] + '.json'), request)
            except Exception:
                if previous is None:
                    path.unlink()
                else:
                    path.write_text(previous)
                raise
        return self.status(task_id)

    def status(self, task_id):
        if type(task_id) is not int or task_id <= 0:
            raise ValueError('Numeric task ID required')
        path = self.state / f'{task_id}.json'
        if not path.exists():
            return {'task_id': task_id, 'status': 'not_submitted'}
        saved = json.loads(path.read_text())
        request = saved['request']
        run = self.queue / 'runs' / request['request_id']
        receipt = json.loads((run / 'receipt.json').read_text()) if (run / 'receipt.json').exists() else {'status': 'queued'}
        result = {k: request[k] for k in ['task_id', 'task_url', 'request_id', 'provider', 'reason', 'client_id', 'title']}
        result.update(receipt)
        result['notification'] = saved.get('notification')
        if (run / 'result.md').exists():
            result['result'] = (run / 'result.md').read_text()[:12000]
        return result

    def reconcile(self, task_id):
        with (self.state / 'handback.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = self.status(task_id)
            if state['status'] not in TERMINAL or state['notification']:
                return state
            path = self.state / f'{task_id}.json'
            saved = json.loads(path.read_text())
            request = saved['request']
            # Re-read authority and task, including stop messages since admission.
            task, current = self.contract(task_id, request['instruction_message_id'])
            if current != request or actor(task) not in {self.config['agent_user_id'], self.config['reviewer_id']}:
                raise ValueError('Task changed or ownership moved; retain result without overwriting a human handoff')
            marker = 'TED central route: ' + request['request_id']
            messages = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
            messages = messages if isinstance(messages, list) else messages.get('data', [])
            if not any(marker in plain(m.get('message', '')) and actor(m) == self.config['agent_user_id'] for m in messages):
                location = ('Open hermes-vps in Codex and find “' + request['title'] + '”.'
                            if request['provider'] == 'codex' else
                            'Claude session saved on the VPS. It does not appear automatically in the Claude app. Resume command: ' + str(state.get('resume_command', 'unavailable')))
                body = ('<p><strong>' + request['provider'].title() + ' — ' + state['status'] + '</strong></p><p>'
                        + html.escape(state.get('result') or state.get('error') or 'Inspect the saved run.')
                        + '</p><p>' + html.escape(location) + '</p><p>Prepared for review. No publication, main push or client send is authorised by this route.</p><p>'
                        + html.escape(marker) + ' | AI authorship: TED central router.</p>')
                self.api('create_message_in_task', {'taskId': task_id, 'message': body})
                check = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
                check = check if isinstance(check, list) else check.get('data', [])
                if not any(marker in plain(m.get('message', '')) and actor(m) == self.config['agent_user_id'] for m in check):
                    raise ValueError('Handback readback failed')
            # Result delivery is separate from business completion. Keep task open for feedback.
            saved['notification'] = {'verified': True, 'status': state['status']}
            atomic(path, saved)
            return self.status(task_id)
