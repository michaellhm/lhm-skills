"""Deterministic provider policy and human-bound, idempotent TED intake."""
import fcntl
import hashlib
import html
import json
from pathlib import Path
import re
import time
import uuid
from urllib.parse import quote, urlparse
from html.parser import HTMLParser

POLICY_VERSION = 4
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


def session_link(provider, thread_id, config, receipt):
    if provider == 'codex':
        try:
            thread_id = str(uuid.UUID(thread_id or ''))
        except (ValueError, AttributeError):
            return None
        host = config.get('codex_host_id')
        if not isinstance(host, str) or not re.fullmatch(r'[A-Za-z0-9:_-]{1,160}', host):
            return None
        return 'codex://threads/' + thread_id + '?hostId=' + quote(host, safe='')
    # A Claude Code local UUID is NOT a Remote Control session URL. Never fabricate that mapping.
    remote = receipt.get('remote_session_url', '')
    if not isinstance(remote, str):
        return None
    parsed = urlparse(remote)
    if (parsed.scheme == 'https' and parsed.netloc == 'claude.ai'
            and re.fullmatch(r'/code/session_[A-Za-z0-9]+', parsed.path)
            and not parsed.query and not parsed.fragment):
        return remote
    return None


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.urls.extend(v for k, v in attrs if k == 'href')


def contains_link(message, url):
    links = Links()
    links.feed(message)
    return url in links.urls


def explicit_provider(instruction):
    """Provider changes require a positive, personal routing instruction."""
    pattern = (r'\b(?:use|(?:send|push|switch|move|reroute)\s+(?:(?:this|it|the task)\s+)?to|'
               r'run\s+(?:(?:this|it)\s+)?(?:in|with))\s+(codex|claude)\b')
    overrides = re.findall(pattern, instruction, re.I)
    if overrides and re.search(r"\b(do not|don't|never|not)\s+(?:use|send|push|switch|move|reroute|run)\b", instruction, re.I):
        raise ValueError('Negated provider instructions require clarification')
    if len(set(value.lower() for value in overrides)) > 1:
        raise ValueError('Conflicting provider instructions; one provider is required')
    return overrides[-1].lower() if overrides else None


def choose(title, description, instruction):
    """Domain policy precedes incidental tools; personal override has highest priority."""
    override = explicit_provider(instruction)
    if override:
        return override, 'Explicit human provider selection'
    if (re.search(r'\bgoogle[ -]ads\b', title, re.I)
            or re.search(r'\bservice\s*=\s*google-ads\b', description, re.I)):
        return 'claude', 'Google Ads domain policy; incidental website/Workspace references do not change provider'
    text = ' '.join([title, description, instruction]).lower()
    if re.search(r'\b(website|prototype|github|repository|repo|code|html|css|javascript|astro|wordpress|deploy|staging|google docs|google drive|g drive|workspace|gmail|spreadsheet)\b', text):
        return 'codex', 'Website/code or connected Workspace work; keep mixed deliverables together'
    return 'claude', 'Research, writing, analysis or planning; local draft for review'


def execution_handoff(provider, instruction):
    """Forward personal execution/approval intent, without TED interpreting action details."""
    return provider == 'claude' and bool(re.search(r'\b(approve|approved|implement|execute|publish)\b', instruction, re.I))


def resolve_client(task, clients, discussion=''):
    exact = [key for key, value in clients.items() if str(task['id']) in [str(i) for i in value.get('basicops_task_ids', [])]]
    if len(exact) > 1:
        raise ValueError('Conflicting registered task bindings')
    if len(exact) == 1:
        return exact[0]

    def names(text, prefix_only=False):
        text = plain(text).casefold()
        found = set()
        for key, value in clients.items():
            aliases = [value['name'], *value.get('aliases', [])]
            if key == 'raise-the-bar':
                aliases.append('RTB')  # Preserve the original pilot abbreviation.
            for alias in aliases:
                pattern = re.escape(alias.casefold())
                if prefix_only or len(alias) <= 5:
                    matched = re.match(r'^\s*' + pattern + r'\s*:', text)
                else:
                    matched = re.search(r'(?<!\w)' + pattern + r'(?!\w)', text)
                if matched:
                    found.add(key)
        return found

    for text, prefix_only in [(task['title'], True), (task['title'], False),
                              (task.get('description', ''), False), (discussion, False)]:
        found = names(text, prefix_only)
        if len(found) == 1:
            return next(iter(found))
        if len(found) > 1:
            raise ValueError('Several canonical clients match this task; do not guess a folder')
    raise ValueError('Client not identified in task or brief. Check task_client_lookup and the canonical shared client index')


def delivery_key(delivery):
    return hashlib.sha256(json.dumps({k: delivery.get(k) for k in ['artefact_state','package_sha256','error']}, sort_keys=True).encode()).hexdigest()[:12]


def result_with_drive_links(result, delivery):
    if delivery.get('artefact_state') != 'delivered':
        return result
    files = delivery.get('files', [])
    def replace(match):
        path = match.group(2)
        found = [f for f in files if path == 'drafts/' + f['relative'] or path.endswith('/drafts/' + f['relative'])]
        return '[' + match.group(1) + '](' + found[0]['url'] + ')' if len(found) == 1 else match.group(0)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace, result)


class Router:
    def __init__(self, profile, queue, api):
        self.profile, self.queue, self.api = Path(profile), Path(queue), api
        self.config = json.loads((self.profile / 'task-router.json').read_text())
        self.state = self.profile / 'task-router-state'
        self.state.mkdir(exist_ok=True)
        self.directory = None
        catalog = self.profile / 'task-router-client-directory.json'
        if catalog.exists():
            self.directory = json.loads(catalog.read_text())
            self.config['clients'] = self.directory['clients']

    def client_lookup(self, query):
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 120:
            raise ValueError('Supply a client name or known alias, 2–120 characters')
        if self.api('get_current_user', {}).get('id') != self.config['agent_user_id']:
            raise ValueError('TED connector identity mismatch')
        self.check_freshness()
        matches = [{'client_id': key, **value} for key, value in self.config['clients'].items()
                   if any(query.strip().casefold() in name.casefold() for name in [value['name'], *value.get('aliases', [])])]
        return {'source': 'shared Obsidian client index and canonical overviews',
                'matches': matches[:20], 'count': len(matches),
                'write_authority': 'none; recorded Drive/GitHub links require normal access and destination verification'}

    def check_freshness(self):
        if self.config.get('require_client_directory') and self.directory is None:
            raise ValueError('Canonical shared client directory is not ready; refresh shared knowledge before intake')
        if self.directory and not 0 <= time.time() - self.directory.get('knowledge_refreshed_at', 0) <= 900:
            raise ValueError('Canonical shared client knowledge cache is stale; refresh or use live evidence, not a guessed client')

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
                or not (re.search(r'\b(work on|run|execute|prepare|write|draft|research|investigate|update|revise|implement|go ahead|proceed|approve)\b', instruction, re.I) or explicit_provider(instruction))
                or re.search(r"\b(do not|don't|never|stop|cancel|hold|pause)\b", instruction, re.I)):
            raise ValueError('A direct personal work request is required; assignment, relay or a stop is not permission')
        if task.get('status') in {'Complete', 'Cancelled', 'Decline'}:
            raise ValueError('Task is closed')
        if any(actor(m) == self.config['reviewer_id'] and m.get('created', 0) > msg.get('created', 0)
               and re.search(r'\b(stop|cancel|hold|pause)\b', plain(m.get('message', '')), re.I) for m in messages):
            raise ValueError('A later human stop/hold supersedes this instruction')
        self.check_freshness()
        context_messages = [{'id': m['id'], 'author': actor(m), 'text': plain(m.get('message', ''))}
                            for m in messages if m.get('id') != instruction_message_id
                            and m.get('created', 0) <= msg.get('created', 0) and m.get('message')]
        context_messages.sort(key=lambda m: m['id'])
        if sum(len(m['text']) for m in context_messages) > 16000:
            raise ValueError('Task discussion brief exceeds bounded context; identify a smaller authoritative brief')
        discussion = '\n'.join(m['text'] for m in context_messages)
        client = resolve_client(task, self.config['clients'], discussion)
        provider, reason = choose(plain(task['title']), plain(task.get('description', '')) + '\n' + discussion, instruction)
        existing = self.state / f'{task_id}.json'
        resume = None
        handoff = None
        if existing.exists():
            old = json.loads(existing.read_text())['request']
            if old['instruction_message_id'] == instruction_message_id:
                resume = old.get('resume_thread_id')
                handoff = old.get('provider_handoff')
            else:
                status = self.status(task_id)
                if status['status'] not in TERMINAL or not status.get('thread_id'):
                    raise ValueError('Existing session is active or unavailable; inspect its status before adding feedback')
                if int(instruction_message_id[2:]) <= int(old['instruction_message_id'][2:]):
                    raise ValueError('Feedback must be a newer personal instruction')
                resume = status['thread_id']
            explicit = explicit_provider(instruction)
            if old['instruction_message_id'] != instruction_message_id and explicit and explicit != old['provider']:
                handoff = {'from_provider': old['provider'], 'request_id': old['request_id'],
                           'thread_id': status['thread_id']}
                resume = None  # Provider IDs are never interchangeable.
                provider, reason = explicit, 'Explicit human handoff from ' + old['provider'] + '; preserve prior draft and audit trail'
            else:
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
                   'permission_ceiling': 'prepare_for_review', 'context_messages': context_messages}
        if provider == 'claude':
            request['handoff_mode'] = 'provider_conversation'
        links = Links()
        links.feed(task.get('description', ''))
        for message in messages:
            if message.get('created', 0) <= msg.get('created', 0):
                links.feed(message.get('message', ''))
        request['source_links'] = sorted(set(u for u in links.urls if u.startswith('https://')))[:40]
        if execution_handoff(provider, instruction):
            request.update(handoff_mode='provider_execution', permission_ceiling='provider_tool_approval')
        if existing.exists():
            prior = json.loads(existing.read_text())['request']
            if prior['instruction_message_id'] == instruction_message_id:
                if prior['client_id'] != client:
                    raise ValueError('Canonical lookup conflicts with the admitted client')
                request['client'] = prior['client']
                request['policy_version'] = prior.get('policy_version', 1)
                # Reverification never upgrades an immutable, already-admitted request.
                request['permission_ceiling'] = prior['permission_ceiling']
                if 'handoff_mode' in prior:
                    request['handoff_mode'] = prior['handoff_mode']
                else:
                    request.pop('handoff_mode', None)
                if 'source_links' in prior:
                    request['source_links'] = prior['source_links']
                else:
                    request.pop('source_links', None)
                if prior.get('policy_version') == 1:
                    request['policy_version'] = 1
                    request.pop('context_messages', None)
        if resume:
            request['resume_thread_id'] = resume
        if handoff:
            request['provider_handoff'] = handoff
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
                if old['request']['instruction_message_id'] == instruction_message_id or not (request.get('resume_thread_id') or request.get('provider_handoff')):
                    raise ValueError('Existing instruction changed; do not duplicate or replace work')
                if old['request']['client_id'] != request['client_id']:
                    raise ValueError('Follow-up cannot change the client')
                handoff = request.get('provider_handoff')
                if handoff and (handoff['request_id'] != old['request']['request_id'] or handoff['from_provider'] != old['request']['provider']):
                    raise ValueError('Handoff source changed; preview again')
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
        delivery_path = run / 'delivery.json'
        result['delivery_required'] = bool(receipt.get('delivery_required') or (run / 'delivery-request.json').exists())
        result['delivery'] = json.loads(delivery_path.read_text()) if delivery_path.exists() else {'artefact_state': 'pending' if result['delivery_required'] else 'not_configured'}
        result['delivery_notification'] = saved.get('delivery_notification')
        result['notification'] = saved.get('notification')
        result['session_notification'] = saved.get('session_notification')
        result['chat_url'] = session_link(request['provider'], receipt.get('thread_id'), self.config, receipt)
        if (run / 'result.md').exists():
            result['result'] = (run / 'result.md').read_text()[:12000]
        return result

    def reconcile(self, task_id):
        with (self.state / 'handback.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = self.status(task_id)
            needs_link = bool(state.get('chat_url')) and not state.get('session_notification')
            delivery = state.get('delivery', {})
            delivery_state = delivery.get('artefact_state')
            needs_delivery = delivery_state in {'delivered', 'delivery_incomplete', 'no_files_produced'} and state.get('delivery_notification') != delivery_key(delivery)
            needs_result = state['status'] in TERMINAL and not state['notification'] and not (state.get('delivery_required') and delivery_state in {'pending', 'delivery_incomplete'})
            if not needs_link and not needs_result and not needs_delivery:
                return state
            path = self.state / f'{task_id}.json'
            saved = json.loads(path.read_text())
            request = saved['request']
            # Re-read authority and task, including stop messages since admission.
            task, current = self.contract(task_id, request['instruction_message_id'])
            if current != request or actor(task) not in {self.config['agent_user_id'], self.config['reviewer_id']}:
                raise ValueError('Task changed or ownership moved; retain result without overwriting a human handoff')
            if needs_link:
                marker = 'TED session link: ' + request['request_id']
                messages = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
                messages = messages if isinstance(messages, list) else messages.get('data', [])
                existing = next((m for m in messages if marker in plain(m.get('message', ''))
                                 and actor(m) == self.config['agent_user_id']), None)
                url = state['chat_url']
                if existing is None:
                    label = 'Open existing ' + request['provider'].title() + ' chat'
                    message = ('<p><strong>' + html.escape(request['provider'].title() + ' session available')
                               + '</strong></p><p><a href="' + html.escape(url, quote=True) + '">'
                               + html.escape(label) + '</a></p><p>Chat: ' + html.escape(request['title'])
                               + '. Worker status: ' + html.escape(state['status']) + '.</p>'
                               + '<p>This opens the existing conversation, preserving its context. '
                               + ('Use the desktop app paired with hermes-vps. ' if request['provider'] == 'codex' else '')
                               + 'A running worker is not a completed delivery; check its status before taking over.</p>'
                               + '<p><small>' + html.escape(marker) + ' | AI authorship: TED central router.</small></p>')
                    self.api('create_message_in_task', {'taskId': task_id, 'message': message})
                    check = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
                    check = check if isinstance(check, list) else check.get('data', [])
                    existing = next((m for m in check if marker in plain(m.get('message', ''))
                                     and actor(m) == self.config['agent_user_id']), None)
                if existing is None:
                    raise ValueError('Session-link message readback failed')
                saved['session_notification'] = {'message_id': existing['id'],
                    'url': url, 'verified': contains_link(existing.get('message', ''), url),
                    'verification_scope': 'BasicOps anchor readback; desktop opening requires the paired client'}
                atomic(path, saved)
                if not saved['session_notification']['verified']:
                    raise ValueError('BasicOps did not preserve the chat-link anchor; do not claim a clickable link')
            if needs_delivery:
                marker = 'TED Drive delivery: ' + request['request_id'] + ':' + delivery_key(delivery)
                messages = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
                messages = messages if isinstance(messages, list) else messages.get('data', [])
                if not any(marker in plain(m.get('message','')) and actor(m) == self.config['agent_user_id'] for m in messages):
                    if delivery_state == 'delivered':
                        body = '<p><strong>Files delivered to Google Drive</strong></p><p><a href="' + html.escape(delivery['folder_url'], quote=True) + '">Open the task files in Drive</a></p><ul>'
                        body += ''.join('<li><a href="' + html.escape(f['url'], quote=True) + '">' + html.escape(f['relative']) + '</a></li>' for f in delivery['files'])
                        body += '</ul><p>Every file was read back and its name, folder, byte count and SHA-256 verified. These are internal review drafts; no email send, live account change or website publication is implied.</p>'
                    else:
                        body = '<p><strong>' + ('Drive delivery incomplete' if delivery_state == 'delivery_incomplete' else 'No files produced') + '</strong></p><p>' + html.escape(delivery.get('error') or delivery.get('reason','')) + '</p><p>Local preparation is not a verified Drive delivery.</p>'
                    body += '<p>' + html.escape(marker) + ' | AI authorship: TED central router.</p>'
                    self.api('create_message_in_task', {'taskId':task_id,'message':body})
                    checked = self.api('list_messages_in_task', {'taskId':task_id,'limit':50})
                    checked = checked if isinstance(checked,list) else checked.get('data',[])
                    if not any(marker in plain(m.get('message','')) and actor(m) == self.config['agent_user_id'] for m in checked):
                        raise ValueError('Drive-link handback readback failed')
                saved['delivery_notification'] = delivery_key(delivery)
                atomic(path,saved)
            if not needs_result:
                return self.status(task_id)
            marker = 'TED central route: ' + request['request_id']
            messages = self.api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
            messages = messages if isinstance(messages, list) else messages.get('data', [])
            if not any(marker in plain(m.get('message', '')) and actor(m) == self.config['agent_user_id'] for m in messages):
                location = ('Open hermes-vps in Codex and find “' + request['title'] + '”.'
                            if request['provider'] == 'codex' else
                            'Claude session saved on the VPS. It does not appear automatically in the Claude app. Resume command: ' + str(state.get('resume_command', 'unavailable')))
                if state.get('chat_url'):
                    location_html = '<a href="' + html.escape(state['chat_url'], quote=True) + '">Open existing ' + html.escape(request['provider'].title()) + ' chat</a>'
                else:
                    location_html = html.escape(location)
                body = ('<p><strong>' + request['provider'].title() + ' — ' + state['status'] + '</strong></p><p>'
                        + html.escape(result_with_drive_links(state.get('result') or state.get('error') or 'Inspect the saved run.', delivery))
                        + '</p><p>' + location_html + '</p><p>Prepared for review. No publication, main push or client send is authorised by this route.</p><p>'
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
