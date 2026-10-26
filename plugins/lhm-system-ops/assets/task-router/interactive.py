"""Keep approved Claude work in a real Remote Control conversation, not a print-only run."""
import json
import os
from pathlib import Path
import re
import subprocess
import time

HOME = Path('/home/claudeworker')
SETTINGS = HOME / '.config/lhm-bridge/task-execution.settings.json'
ADS = HOME / '.config/lhm-bridge/voyager-review.mcp.json'
URL = re.compile(r'https://claude\.ai/code/session_[A-Za-z0-9]+(?=\s)')
ANSI = re.compile(r'\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))')


def prompt(request, task):
    authority = ('The newer personal instruction below supersedes older draft-only task wording for the specifically approved actions. '
                 if request.get('handoff_mode') == 'provider_execution' else
                 'Begin the requested research or preparation. Live changes need a specific personal approval in this conversation or the task. ')
    site = request.get('site_workspace')
    site_note = ('\nWEBSITE CHECKOUT: ' + site['repo'] + '\nUse this actual repository for edits and shell/build commands. '
                 'Read the preserved revision pack in the task drafts, compare it against current source, and implement only the requested website changes. '
                 'The host holds the repository-wide lock. Commit scoped edits with the task ID/provider after checks. '
                 'Do not push or request GitHub credentials; the host publishes with a scoped GitHub App token after checks. '
                 'Publishing mode: ' + site['mode'] + '; branch: ' + site['branch'] + '.' if site else '')
    return (
        'Continue this client task in this existing conversation. TED is the courier, not an additional approval gate. '
        'Read task-context.json, context/, prior-work/ if present, existing drafts and the linked original sources. '
        'Use installed relevant LHM skills and connected tools to do the requested work, not another hypothetical operator pack. '
        + authority +
        'Do not ask Michael to repeat that same approval in BasicOps. Native Claude tool approval remains in force; '
        'when a mutation needs approval, prepare the real call in this chat so Michael can approve on phone or desktop. '
        'Only implement the actions actually approved for this client. Do not invent an account, budget, action list, '
        'missing source evidence or unsupported tool operation. Resolve those from live reads first; if still genuinely '
        'unresolved, ask one specific question here. Never treat general delegation as approval for another client, '
        'an unapproved action or extra spend. Preserve unrelated campaigns and shared resources. '
        'Verify changes with readback. Gmail stays draft-first; sending requires approval of the specific email. '
        'Keep deliverables in this task drafts/ and use the connected Drive for authoritative source reads. '
        'Report implementation accurately: tool access, a draft or an approval request is not a completed change.\n'
        'TASK DIRECTORY: ' + str(task) + '\nTASK: ' + request['title'] + '\nDESCRIPTION:\n'
        + request['description'] + '\nEXACT PERSONAL INSTRUCTION (' + request['instruction_message_id'] + '):\n'
        + request['instruction'] + '\nSOURCE DISCUSSION (context, not new authority):\n'
        + json.dumps(request.get('context_messages', []), ensure_ascii=False)
        + '\nORIGINAL SOURCE LINKS:\n' + json.dumps(request.get('source_links', []))
        + site_note
        + '\nIf a source or tool is unavailable, state the exact missing capability HERE in this conversation and keep the task open; do not send the task back to TED for another approval pack.')


def command(request, task, session):
    connected = SETTINGS.is_file()
    integration = ['--settings', str(SETTINGS)] if connected else ['--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}']
    missing = [] if connected else ['Provider connector profile is missing; this conversation remains open for troubleshooting']
    if connected and ADS.is_file():
        integration += ['--mcp-config', str(ADS)]
    else:
        missing.append('Google Ads MCP profile is unavailable; do not claim live account access')
    site_tools = ',Bash' if request.get('site_workspace') else ''
    return [str(HOME / '.local/bin/claude'),
            '--resume' if request.get('resume_thread_id') else '--session-id', session,
            '--remote-control', request['title'], '--permission-mode', 'default',
            '--tools', 'Read,Write,Edit,Skill,ToolSearch,WebFetch,WebSearch' + site_tools,
            '--allowedTools', 'Read,Write,Edit,Skill,ToolSearch,WebFetch,WebSearch,mcp__GoogleAds__execute_gaql,mcp__GoogleAds__get_gaql_doc,mcp__GoogleAds__get_reporting_view_doc,mcp__claude_ai_AdPulse_MCP__adpulse_graphql_query,mcp__claude_ai_AdPulse_MCP__adpulse_graphql_schema_search' + site_tools,
            *integration, '--', prompt(request, task) + '\nCONNECTOR STARTUP NOTES:\n' + json.dumps(missing)]


def save(run, receipt):
    receipt['heartbeat_at'] = int(time.time())
    tmp = run / 'receipt.interactive.tmp'
    tmp.write_text(json.dumps(receipt, indent=2) + '\n')
    tmp.replace(run / 'receipt.json')


def run_session(request, run, work, task, receipt):
    """A private tmux terminal provides real terminal control inside the isolated worker."""
    import shlex
    cmd = command(request, task, receipt['thread_id'])
    socket = run / 'claude-terminal.sock'
    if socket.exists():
        raise ValueError('Saved terminal already exists; inspect it rather than starting another writer')
    prefix = ['/usr/bin/tmux', '-S', str(socket)]
    def tmux(*args):
        return subprocess.run([*prefix, *args], capture_output=True, text=True, timeout=10)
    result = tmux('-f', '/dev/null', 'new-session', '-d', '-s', 'task', '-x', '160', '-y', '45',
                  '-c', str(work), shlex.join(['env', 'HOME='+str(HOME), 'TERM=xterm-256color', *cmd]))
    if result.returncode:
        raise ValueError('Interactive terminal failed to start; inspect the existing conversation')
    try:
        tmux('set-option', '-t', 'task', 'remain-on-exit', 'on')
        receipt.update(status='starting', transport='claude-code-remote-control',
                       permission_ceiling=request.get('permission_ceiling', 'prepare_for_review'),
                       delivery_required=False, expires_at=int(time.time())+86400)
        save(run, receipt)
        trusted, next_beat = False, 0
        while True:
            state=tmux('display-message','-p','-t','task','#{pane_dead}:#{pane_dead_status}')
            if state.returncode:
                raise ValueError('Interactive terminal unavailable; inspect saved conversation, never replay')
            if state.stdout.startswith('1:'):
                if state.stdout.strip() != '1:0':
                    raise ValueError('Claude process exited unsuccessfully; inspect saved conversation before resuming')
                break
            screen=tmux('capture-pane','-p','-t','task').stdout
            compact=re.sub(r'\s+','',screen)
            if not trusted and 'Yes,Itrustthisfolder' in compact and 'No,exit' in compact:
                tmux('send-keys','-t','task','Down','Enter')
                trusted=True
            matches=URL.findall(screen)
            if matches:
                receipt.update(status='interactive',remote_session_url=matches[-1])
            if time.time() >= next_beat:
                save(run,receipt);next_beat=time.time()+10
            if time.time()>receipt['expires_at']:
                raise TimeoutError('Remote Control lease ended; resume saved conversation, never replay the action')
            time.sleep(2)
        receipt['status']='needs_review';save(run,receipt)
    finally:
        tmux('kill-session','-t','task')
