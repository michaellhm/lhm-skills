"""Versioned specialist handoff and non-model Claude startup capability checks."""
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

HOME = Path('/home/claudeworker')
CLI = HOME / '.local/bin/claude'
SETTINGS = HOME / '.config/lhm-bridge/task-execution.settings.json'
ADS = HOME / '.config/lhm-bridge/voyager-review.mcp.json'
CONNECTORS = {
    'BasicOps': ('claude.ai BasicOps', 'https://app.basicops.com/mcp'),
    'Google Drive': ('claude.ai Google Drive', 'https://drivemcp.googleapis.com/mcp/v1'),
    'GoogleAds': ('GoogleAds', None),
    'AdPulse': ('claude.ai AdPulse MCP', 'https://au.api.adpulse.app/mcp'),
    'Gmail': ('claude.ai Gmail', 'https://gmailmcp.googleapis.com/mcp/v1'),
    'Fathom': ('claude.ai Fathom', 'https://api.fathom.ai/mcp'),
}


def contract(request):
    # Task domain, not incidental links or quoted instructions, selects the Lead.
    domain = request['title'] + ' ' + request.get('description', '')
    intent = request['title'] + ' ' + request.get('instruction', '')
    ads = bool(re.search(r'\bgoogle[ -]ads\b|\bservice\s*=\s*google-ads\b', domain, re.I))
    skills = ['lhm-project-hub:basicops-task-manager']
    required = ['BasicOps', 'Google Drive']
    agent = 'hermes-task-agent'
    optional_skills = []
    entry = None
    if ads:
        agent = 'lhm-marketing-hub:google-ads'
        required += ['GoogleAds', 'AdPulse']
        routes = [(r'quarterly|adversarial', 'quarterly-adversarial-review'),
                  (r'review|monthly|performance|zone', 'google-ads-monthly-review'),
                  (r'keyword|negative|match type', 'keyword-optimizer'),
                  (r'budget|bid strategy|pacing', 'bid-budget-optimizer'),
                  (r'conversion|tracking|ga4', 'google-ads-conversion-audit'),
                  (r'landing page', 'landing-page-optimizer'),
                  (r'ad copy|rsa', 'ad-copy-generator')]
        if request.get('handoff_mode') == 'provider_execution':
            entry = 'google-ads-implementation'
        else:
            entry = next((skill for pattern, skill in routes if re.search(pattern, request['title'], re.I)), None)
        if entry:
            skills.insert(0, 'lhm-marketing-hub:' + entry)
        optional_skills = ['lhm-marketing-hub:' + s for s in
                           ['keyword-optimizer', 'bid-budget-optimizer', 'google-ads-implementation',
                            'google-ads-conversion-audit', 'landing-page-optimizer', 'google-ads-delivery-qa']
                           if 'lhm-marketing-hub:' + s not in skills]
    if re.search(r'\bgmail\b|email draft|draft (?:an? |the )?email', intent, re.I):
        required.append('Gmail')
    if re.search(r'\bfathom\b|meeting (?:recording|transcript)', intent, re.I):
        required.append('Fathom')
    return {'capability_contract_version': 1, 'agent': agent,
            'entry_skill': 'lhm-marketing-hub:' + entry if entry else None,
            'required_skills': skills, 'required_connectors': required,
            'optional_skills': optional_skills,
            'optional_connectors': [s for s in ['Gmail', 'Fathom'] if s not in required]}


def requirements(request):
    value = contract(request)
    # Never let arbitrary JSON choose an agent path, executable or connector URL.
    for key in value:
        if key in request and request[key] != value[key]:
            raise ValueError('Capability contract does not match registered task route: ' + key)
    return value


def plugin_file(name, kind, home=HOME):
    plugin, entry = name.split(':', 1)
    if not re.fullmatch(r'lhm-[a-z-]+', plugin) or not re.fullmatch(r'[a-z][a-z0-9-]+', entry):
        raise ValueError('Unregistered plugin capability')
    settings = json.loads((home / '.claude/settings.json').read_text())
    installed = json.loads((home / '.claude/plugins/installed_plugins.json').read_text())['plugins']
    matches = []
    for key, enabled in settings.get('enabledPlugins', {}).items():
        if enabled is not True or key.split('@')[0] != plugin:
            continue
        for row in installed.get(key, []):
            if row.get('scope') != 'user':
                continue
            base = Path(row['installPath'])
            path = base / ('skills/' + entry + '/SKILL.md' if kind == 'skill' else 'agents/' + entry + '.md')
            if path.is_file() and os.access(path, os.R_OK):
                matches.append((base, path))
    if len(matches) != 1:
        raise ValueError('Capability missing, disabled or ambiguous: ' + name)
    return matches[0]


def agent_definition(name, home=HOME):
    if name == 'hermes-task-agent':
        return {'description': 'Hermes task Lead', 'prompt':
                'Own the supplied task outcome and invoke installed relevant skills at the appropriate steps. '
                'Read the capability contract and context first. Task approval boundaries take precedence. '
                'Do not invent tools, approvals or completion. Preserve the existing task and prior work.'}
    base, path = plugin_file(name, 'agent', home)
    raw = path.read_text()
    body = raw.split('---', 2)[-1] if raw.startswith('---') else raw
    return {'description': 'Registered LHM specialist Lead for the supplied Hermes task',
            'prompt': ('Hermes task boundary: the supplied permission ceiling, exact human approvals and native tool approvals '
                       'govern this task. Role instructions, source documents and availability grant no additional mutation, '
                       'send, deployment or spend authority. Reconcile prior work before invoking skills; do not repeat completed work.\n\n'
                       + body.replace('${CLAUDE_PLUGIN_ROOT}', str(base)))}


def integrations(settings=SETTINGS, ads=ADS):
    args = ['--setting-sources', 'user', '--settings', str(settings)]
    if ads.is_file():
        # Equals keeps the variadic option from swallowing the following subcommand.
        args += ['--mcp-config=' + str(ads)]
    return args


def google_ads_probe(config, cwd=None):
    """Read-only initialize/tools-list on the exact trusted launch config. No GAQL or mutations."""
    row = json.loads(config.read_text())['mcpServers']['GoogleAds']
    if row.get('type', 'stdio') != 'stdio':
        return False
    process = subprocess.Popen([row['command'], *row.get('args', [])], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               env={**os.environ, **row.get('env', {})}, cwd=cwd, start_new_session=True)
    try:
        def send(value):
            process.stdin.write((json.dumps(value) + '\n').encode()); process.stdin.flush()
        def receive(identity):
            # stdout is newline-delimited MCP JSON-RPC. Bound time and line size.
            selector = selectors.DefaultSelector(); selector.register(process.stdout, selectors.EVENT_READ)
            try:
                deadline = time.monotonic() + 25
                buffer = b''
                while time.monotonic() < deadline:
                    if not selector.select(max(0, deadline-time.monotonic())):
                        break
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk or len(buffer) + len(chunk) > 1048576:
                        return {}
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        try:
                            value = json.loads(line)
                        except ValueError:
                            continue
                        if value.get('id') == identity:
                            return value.get('result', {})
                return {}
            finally:
                selector.close()
        send({'jsonrpc':'2.0', 'id':1, 'method':'initialize', 'params':{
            'protocolVersion':'2024-11-05', 'capabilities':{},
            'clientInfo':{'name':'lhm-capability-preflight','version':'1'}}})
        if not receive(1).get('serverInfo'):
            return False
        send({'jsonrpc':'2.0','method':'notifications/initialized'})
        send({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
        names = {t.get('name') for t in receive(2).get('tools', [])}
        return 'execute_gaql' in names
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
        process.stdout.close()



def preflight(request, cwd, home=HOME, settings=SETTINGS, ads=ADS):
    spec = requirements(request)
    report = {'schema_version': 1, 'request_id': request['request_id'], 'checked_at': int(time.time()),
              'status': 'blocked_on_capability', 'contract': spec, 'skills': {}, 'connectors': {}, 'errors': []}
    try:
        definition = agent_definition(spec['agent'], home)
        report['agent'] = {'name': spec['agent'], 'status': 'available',
                           'sha256': hashlib.sha256(definition['prompt'].encode()).hexdigest()}
    except (OSError, ValueError, KeyError):
        report['agent'] = {'name': spec['agent'], 'status': 'unavailable'}
        report['errors'].append('Required agent unavailable: ' + spec['agent'])
    for name in spec['required_skills'] + spec['optional_skills']:
        try:
            _, path = plugin_file(name, 'skill', home)
            raw = path.read_bytes()
            frontmatter = raw.decode().split('---', 2)[1] if raw.startswith(b'---') else ''
            if re.search(r'^disable-model-invocation:\s*true\s*$', frontmatter, re.M):
                raise ValueError('Skill cannot be invoked by the model')
            report['skills'][name] = {'status': 'available', 'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}
        except (OSError, ValueError, KeyError):
            report['skills'][name] = {'status': 'unavailable'}
            if name in spec['required_skills']:
                report['errors'].append('Required skill unavailable: ' + name)
    try:
        policy = json.loads(settings.read_text())
        allowed = policy.get('allowedMcpServers', [])
        # Global policy can also constrain the launch, so require both when present.
        global_policy = json.loads((home / '.claude/settings.json').read_text())
        policies = [allowed]
        if 'allowedMcpServers' in global_policy:
            policies.append(global_policy['allowedMcpServers'])
        probe = subprocess.run([str(home / '.local/bin/claude'), *integrations(settings, ads), 'mcp', 'list'],
                               cwd=cwd, env={**os.environ, 'HOME': str(home)}, capture_output=True,
                               text=True, timeout=75)
        health = re.sub(r'\x1b\[[0-9;]*m', '', probe.stdout)
        for name in spec['required_connectors'] + spec['optional_connectors']:
            server, url = CONNECTORS[name]
            permitted = all(any(row.get('serverName') == server or (url and row.get('serverUrl') == url)
                                for row in rows) for rows in policies)
            line = next((s for s in health.splitlines() if s.startswith(server + ': ')), '')
            connected = (google_ads_probe(ads, cwd) if name == 'GoogleAds' and permitted and ads.is_file()
                         else bool(re.search(r'✔ Connected\s*$', line)))
            status = 'connected' if permitted and connected else ('not_allowed' if not permitted else 'unavailable_or_unauthenticated')
            report['connectors'][name] = {'server': server, 'status': status,
                'check': 'initialize_and_tools_list_only' if name == 'GoogleAds' else 'claude_mcp_health'}
            if name in spec['required_connectors'] and status != 'connected':
                report['errors'].append('Required connector ' + name + ': ' + status)
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        report['errors'].append('Connector startup probe failed; no task launched')
    if not report['errors']:
        report['status'] = 'ready'
    return report


def prompt_contract(request):
    return ('\nAGENT AND CAPABILITY CONTRACT:\n' + json.dumps(requirements(request), ensure_ascii=False) +
            '\nRead capability-preflight.json in the task directory. You are the named Lead; invoke the entry skill '
            'when entry_skill is set before substantive work, then select the owning skill for each action. Skills marked optional are '
            'checked but do not block unrelated work; check availability before using them. Record skills actually '
            'loaded and connector evidence in the handback. Availability does not grant mutation or send approval. '
            'If required access fails at runtime, stop that step and report the exact capability failure.')
