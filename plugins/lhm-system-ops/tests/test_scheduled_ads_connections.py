import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
WORKER = PLUGIN / 'assets/gateways/lhm-shared-claude-worker'


@pytest.mark.parametrize('profile,agent', [
    ('google_ads_readonly', 'lhm-marketing-hub:google-ads'),
    ('marketing_orchestrator_readonly', 'lhm-marketing-hub:start'),
    ('specialist_readonly', 'lhm-marketing-hub:seo'),
])
def test_only_scheduled_ads_gets_ga4_and_fathom(tmp_path, profile, agent):
    (tmp_path / 'prompt.json').write_text(json.dumps({'profile': profile, 'agent_id': agent}))
    response = SimpleNamespace(returncode=0, stdout='{}', stderr='')
    with patch.object(sys, 'argv', [str(WORKER), str(tmp_path), '30']), \
            patch('subprocess.run', return_value=response):
        state = runpy.run_path(str(WORKER))
    command = state['command']
    allowed = set(command[command.index('--allowedTools') + 1].split(','))
    if profile == 'google_ads_readonly':
        assert '--strict-mcp-config' not in command
        assert command[command.index('--setting-sources') + 1] == 'user'
        assert command[command.index('--settings') + 1].endswith('google-ads-scheduled-review.settings.json')
        assert any(arg.endswith('google-ads-scheduled-review.mcp.json') for arg in command)
        assert {'Skill', 'ToolSearch', 'mcp__analytics-mcp__run_report',
                'mcp__claude_ai_Fathom__list_meetings'} <= allowed
        assert state['provisioned_tools'] == 'Skill,ToolSearch'
        assert 'mcp__GoogleAds__mutate' not in allowed
        assert not any('*' in name or 'mcp__claude_ai_Gmail' in name for name in allowed)
        assert state['required_google_ads_skills'] == {
            'lhm-marketing-hub:google-ads-monthly-review',
            'lhm-marketing-hub:bid-budget-optimizer',
            'lhm-marketing-hub:google-ads-conversion-audit',
            'lhm-marketing-hub:google-ads-delivery-qa',
        }
        # Merely returning prose cannot satisfy the existing skill-execution gate.
        assert json.loads((tmp_path / 'final.json').read_text())['status'] == 'failed'
    else:
        assert '--strict-mcp-config' in command
        assert not any('Fathom' in name or 'analytics-mcp' in name for name in allowed)


def test_scheduled_connection_allowlist_excludes_unrelated_services():
    settings = json.loads((PLUGIN / 'assets/gateways/google-ads-scheduled-review.settings.json').read_text())
    assert settings == {'allowedMcpServers': [
        {'serverName': 'GoogleAds'}, {'serverName': 'analytics-mcp'},
        {'serverUrl': 'https://api.fathom.ai/mcp'},
    ]}
