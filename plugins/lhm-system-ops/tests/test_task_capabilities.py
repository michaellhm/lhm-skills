import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router'
sys.path.insert(0, str(SOURCE))
import capabilities as module
import interactive
import worker


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.settings = self.home / 'launch.json'
        self.ads = self.home / 'ads.json'
        self.ads.write_text('{"mcpServers":{"GoogleAds":{}}}')
        self.settings.write_text((SOURCE / 'task-execution.settings.json').read_text())
        self.request = {'request_id':'ted-route-123-dm123', 'title':'Example: Google Ads - Review October performance',
                        'description':'service=google-ads', 'instruction':'Send to Claude', 'handoff_mode':'provider_conversation'}
        self.spec = module.contract(self.request)
        self.plugin = self.home / 'plugins'
        (self.home / '.claude/plugins').mkdir(parents=True)
        enabled = {}; installed = {}
        for name in [self.spec['agent'], *self.spec['required_skills'], *self.spec['optional_skills']]:
            plugin, entry = name.split(':'); key = plugin + '@lhm-marketing-skills'
            enabled[key] = True
            installed[key] = [{'scope':'user', 'installPath':str(self.plugin / plugin)}]
            path = self.plugin / plugin / ('agents/'+entry+'.md' if name == self.spec['agent'] else 'skills/'+entry+'/SKILL.md')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('---\nname: '+entry+'\n---\nRead ${CLAUDE_PLUGIN_ROOT}/references/contract.md')
        (self.home / '.claude/settings.json').write_text(json.dumps({'enabledPlugins':enabled}))
        (self.home / '.claude/plugins/installed_plugins.json').write_text(json.dumps({'plugins':installed}))
        self.health = '\n'.join(v[0]+': https://example.test - ✔ Connected' for v in module.CONNECTORS.values())

    def check(self, health=None):
        with patch.object(module.subprocess, 'run', return_value=SimpleNamespace(stdout=self.health if health is None else health, returncode=0)), patch.object(module, 'google_ads_probe', return_value=True):
            return module.preflight(self.request, self.home, self.home, self.settings, self.ads)

    def test_ads_lead_gets_explicit_skills_and_only_relevant_dependencies(self):
        self.assertEqual(self.spec['agent'], 'lhm-marketing-hub:google-ads')
        self.assertIn('lhm-marketing-hub:google-ads-monthly-review', self.spec['required_skills'])
        self.assertIn('BasicOps', self.spec['required_connectors'])
        self.assertNotIn('Fathom', self.spec['required_connectors'])
        self.assertNotIn('Gmail', self.spec['required_connectors'])
        keywords=module.contract({**self.request,'title':'Example: Google Ads keywords'})
        self.assertEqual(keywords['entry_skill'],'lhm-marketing-hub:keyword-optimizer')
        execution=module.contract({**self.request,'handoff_mode':'provider_execution'})
        self.assertIn('lhm-marketing-hub:google-ads-implementation',execution['required_skills'])
        other = module.contract({**self.request, 'title':'Example: review Fathom meeting transcript and Gmail draft', 'description':''})
        self.assertIn('Fathom', other['required_connectors']); self.assertIn('Gmail', other['required_connectors'])
        self.assertEqual(other['agent'], 'hermes-task-agent')

    def test_missing_required_skill_and_disabled_plugin_block(self):
        self.assertEqual(self.check()['status'], 'ready')
        (self.plugin / 'lhm-marketing-hub/skills/google-ads-monthly-review/SKILL.md').unlink()
        self.assertEqual(self.check()['status'], 'blocked_on_capability')
        (self.home / '.claude/settings.json').write_text('{"enabledPlugins":{}}')
        self.assertEqual(self.check()['agent']['status'], 'unavailable')

    def test_non_invocable_entry_skill_blocks_even_if_installed(self):
        path = self.plugin/'lhm-marketing-hub/skills/google-ads-monthly-review/SKILL.md'
        path.write_text('---\nname: google-ads-monthly-review\ndisable-model-invocation: true\n---\nManual only')
        self.assertEqual(self.check()['status'], 'blocked_on_capability')

    def test_failed_google_ads_protocol_blocks_no_false_ready_from_account_list(self):
        with patch.object(module.subprocess,'run',return_value=SimpleNamespace(stdout=self.health,returncode=0)), patch.object(module,'google_ads_probe',return_value=False):
            report=module.preflight(self.request,self.home,self.home,self.settings,self.ads)
        self.assertEqual(report['status'],'blocked_on_capability')
        self.assertEqual(report['connectors']['GoogleAds']['status'],'unavailable_or_unauthenticated')

    def test_healthy_account_connector_cannot_bypass_launch_allowlist(self):
        d=json.loads(self.settings.read_text())
        d['allowedMcpServers']=[r for r in d['allowedMcpServers'] if r.get('serverUrl') != module.CONNECTORS['BasicOps'][1]]
        self.settings.write_text(json.dumps(d))
        report=self.check()
        self.assertEqual(report['connectors']['BasicOps']['status'], 'not_allowed')
        self.assertEqual(report['status'], 'blocked_on_capability')

    def test_missing_auth_blocks_but_optional_fathom_does_not(self):
        healthy=self.health.replace('claude.ai Fathom: https://example.test - ✔ Connected','claude.ai Fathom: https://example.test - ! Needs authentication')
        self.assertEqual(self.check(healthy)['status'], 'ready')
        healthy=healthy.replace('claude.ai BasicOps: https://example.test - ✔ Connected','claude.ai BasicOps: https://example.test - ! Needs authentication')
        self.assertEqual(self.check(healthy)['status'], 'blocked_on_capability')

    def test_request_cannot_select_arbitrary_agent_or_change_requirements(self):
        with self.assertRaises(ValueError):module.requirements({**self.request,'agent':'/tmp/injected'})
        with self.assertRaises(ValueError):module.requirements({**self.request,'required_connectors':[]})

    def test_probe_uses_same_cwd_settings_and_no_model_call(self):
        with patch.object(module.subprocess,'run',return_value=SimpleNamespace(stdout=self.health,returncode=0)) as run, patch.object(module,'google_ads_probe',return_value=True):
            report=module.preflight(self.request,self.home,self.home,self.settings,self.ads)
        args=run.call_args.args[0]
        self.assertEqual(args[-2:],['mcp','list'])
        self.assertIn('--mcp-config='+str(self.ads), args)
        self.assertEqual(run.call_args.kwargs['cwd'],self.home)
        self.assertNotIn('https://example.test',json.dumps(report))

    def test_main_agent_definition_resolves_installed_plugin_root(self):
        definition=module.agent_definition(self.spec['agent'],self.home)
        self.assertNotIn('${CLAUDE_PLUGIN_ROOT}', definition['prompt'])
        self.assertIn(str(self.plugin/'lhm-marketing-hub'), definition['prompt'])
        request={**self.request,'instruction_message_id':'dm123'}
        with patch('capabilities.agent_definition',return_value=definition), patch.object(interactive.Path,'is_file',return_value=True):
            cmd=interactive.command(request,Path('/task'),'session')
        self.assertEqual(cmd[cmd.index('--agent')+1], self.spec['agent'])
        self.assertIn('required_connectors',cmd[-1])
        self.assertNotIn('--dangerously-skip-permissions',cmd)

    def test_missing_capability_writes_block_receipt_without_starting_claude(self):
        run=self.home/'run';run.mkdir();work=run/'workspace';(work/'drafts').mkdir(parents=True)
        (run/'request.json').write_text(json.dumps({**self.request,'provider':'claude'}))
        blocked={'status':'blocked_on_capability','errors':['Required connector BasicOps: not_allowed']}
        with patch('capabilities.preflight',return_value=blocked), patch('interactive.run_session') as start:
            worker.execute(run,'claude')
        start.assert_not_called()
        receipt=json.loads((run/'receipt.json').read_text())
        self.assertEqual(receipt['failure_kind'],'blocked_on_capability')
        self.assertFalse(receipt['delivery_required'])
        self.assertNotIn('thread_id',receipt)
        self.assertTrue((work/'capability-preflight.json').is_file())

    def test_google_ads_stdio_handshake_checks_tool_inventory_without_gaql(self):
        server=self.home/'server.py'
        server.write_text('import json,sys\nfor line in sys.stdin:\n d=json.loads(line)\n if d.get("id")==1: print(json.dumps({"jsonrpc":"2.0","id":1,"result":{"serverInfo":{"name":"test"}}}),flush=True)\n if d.get("id")==2: print(json.dumps({"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"execute_gaql"}]}}),flush=True)\n')
        self.ads.write_text(json.dumps({'mcpServers':{'GoogleAds':{'command':sys.executable,'args':[str(server)]}}}))
        self.assertTrue(module.google_ads_probe(self.ads))

if __name__ == '__main__': unittest.main()
