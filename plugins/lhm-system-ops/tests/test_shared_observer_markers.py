import ast
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]


def test_shared_worker_accepts_only_closed_decision_and_workflow_marker_prefixes():
    for relative in (
        'assets/gateways/lhm-shared-claude-worker',
        'runtime/lhm-workflow-controller/integration/lhm-claude-worker.live-reference',
    ):
        source = (PLUGIN / relative).read_text(encoding='utf-8')
        ast.parse(source)
        assert "startswith(('LHM decision:','LHM workflow event:'))" in source
        assert "startswith('LHM decision:')" not in source


def test_every_delegated_python_service_binds_current_controller_source():
    packaging = PLUGIN / 'runtime/lhm-workflow-controller/packaging'
    services = sorted(packaging.glob('lhm-delegated-*.service'))
    assert len(services) == 7
    for service in services:
        assert 'Environment=PYTHONPATH=/opt/lhm-workflow/current/src' in service.read_text(encoding='utf-8')


def test_projection_request_reads_root_registry_without_broad_workflow_user_access():
    service = (PLUGIN / 'runtime/lhm-workflow-controller/packaging/lhm-delegated-basicops-request.service').read_text(encoding='utf-8')
    assert 'User=root' in service and 'Group=root' in service
    assert 'ReadWritePaths=/var/lib/lhm-workflow/delegated-basicops-requests' in service
    assert 'ReadOnlyPaths=/var/lib/lhm-workflow/delegated-parents /home/hermes/.hermes/profiles/lhm_brain/config/client-handback-targets.json' in service


def test_delegated_dispatch_rejects_incomplete_connector_results():
    adapter = (PLUGIN / 'runtime/lhm-workflow-controller/integration/lhm-workflow-registered-adapter').read_text(encoding='utf-8')
    bridge = (PLUGIN / 'runtime/lhm-workflow-controller/integration/lhm-delegated-basicops-bridge').read_text(encoding='utf-8')
    assert 'result.get("status") != "completed"' in adapter
    assert 'not isinstance(result.get("verification"), dict)' in adapter
    assert 'registered BasicOps worker did not complete with verification' in bridge


def test_delegated_dispatch_coalesces_same_id_and_refuses_different_content():
    bridge = (PLUGIN / 'runtime/lhm-workflow-controller/integration/lhm-delegated-basicops-bridge').read_text(encoding='utf-8')
    installer = (PLUGIN / 'runtime/lhm-workflow-controller/packaging/install.sh').read_text(encoding='utf-8')
    assert 'duplicate delegated dispatch ID has different content' in bridge
    assert 'delegated-basicops-coalesced' in bridge
    assert 'delegated-basicops-coalesced' in installer
    assert '"delegated-basicops-dispatched", "delegated-basicops-observations"' in bridge
    assert 'same delegated queue ID has different terminal content' in bridge
    assert 'delegated-basicops-observations-failed" / "payloads"' in bridge
    assert 'except RuntimeError:\n            raise' in bridge
