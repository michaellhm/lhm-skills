import hashlib, importlib.util, json, tempfile
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

import pytest


PLUGIN = Path(__file__).resolve().parents[1]
ASSET = PLUGIN / 'assets/host/lhm-prototype-publication-runtime'
spec = importlib.util.spec_from_loader('prototype_publication_runtime', SourceFileLoader('prototype_publication_runtime', str(ASSET)))
runtime = importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)


def configure(root):
    runtime.BASE = root / 'dispatch'
    runtime.INCOMING, runtime.SEALED, runtime.CLAIMS, runtime.PROCESSED, runtime.FAILED = (
        runtime.BASE / name for name in ('incoming', 'sealed', 'claims', 'processed', 'failed'))
    runtime.STAGING = root / 'root-staging'
    runtime.LOCK = runtime.BASE / '.consumer.lock'
    for directory in (runtime.INCOMING, runtime.SEALED, runtime.CLAIMS, runtime.PROCESSED, runtime.FAILED, runtime.STAGING):
        directory.mkdir(parents=True)


def request(root, request_id='rtb-sitemap-fresh-2188809-20260821-c01'):
    content = b'<html>approved</html>'
    relative = 'raise-the-bar/sitemap/index.html'
    source = runtime.SEALED / request_id / relative
    source.parent.mkdir(parents=True); source.write_bytes(content)
    manifest = [{'path': relative, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}]
    package = hashlib.sha256((json.dumps(manifest, sort_keys=True, separators=(',', ':')) + '\n').encode()).hexdigest()
    value = {'schema_version': 3, 'request_id': request_id, 'source_basicops_task': 'task-1',
             'governed_parent': 'RTB-SITEMAP-FRESH-2188809-20260821', 'destination_profile_id': 'prototype-main-v1',
             'operation': 'publish_sitemap', 'credential_reference': 'LHM_PROTOTYPE_MAIN_DEPLOY_KEY',
             'client_slug': 'raise-the-bar', 'project_slug': 'sitemap', 'prototype_kind': 'sitemap',
             'repository': 'michaellhm/lhm-prototype', 'branch': 'main', 'expected_base_commit': '0a4650e35839efbc6582abd4ad067a194280b47c',
             'source_directory': str(runtime.SEALED / request_id), 'source_package_sha256': package,
             'file_manifest': manifest, 'qa_evidence_reference': 'qa-approved', 'idempotency_key': request_id,
             'standing_authority_reference': 'MICHAEL-PROTOTYPE-PUBLISH-STANDING-20260820',
             'commit_message': 'prototype: raise-the-bar/sitemap approved static package'}
    path = runtime.INCOMING / f'{request_id}.json'; path.write_text(json.dumps(value))
    return path, value


def result(value, commit='b' * 40):
    return {'schema_version': 3, 'status': 'published_and_verified', 'request_id': value['request_id'],
            'destination_profile_id': value['destination_profile_id'], 'repository': value['repository'],
            'branch': value['branch'], 'base_commit': value['expected_base_commit'], 'commit': commit,
            'source_package_sha256': value['source_package_sha256'], 'idempotency_key': value['idempotency_key'],
            'standing_authority_reference': value['standing_authority_reference'],
            'workflow': {'conclusion': 'success'}, 'public_verifications': [{'commit': commit, 'status': 200}]}


def test_consumes_shared_request_stages_exact_package_and_returns_verified_receipt():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary)); expected = result(value)
        completed = mock.Mock(returncode=0, stdout=json.dumps(expected), stderr='')
        assert runtime.process(path, runner=mock.Mock(return_value=completed)) == 'processed'
        staged_request = json.loads((runtime.STAGING / f'{value["request_id"]}.request.json').read_text())
        assert staged_request['source_directory'] == str(runtime.STAGING / value['request_id'])
        assert (runtime.STAGING / value['request_id'] / value['file_manifest'][0]['path']).read_bytes() == b'<html>approved</html>'
        assert json.loads((runtime.PROCESSED / path.name).read_text())['commit'] == 'b' * 40
        assert not path.exists()


def test_tamper_fails_before_publisher_and_preserves_failed_request():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary))
        (runtime.SEALED / value['request_id'] / value['file_manifest'][0]['path']).write_bytes(b'tampered')
        runner = mock.Mock()
        assert runtime.process(path, runner=runner) == 'failed'
        runner.assert_not_called()
        assert (runtime.FAILED / path.name).is_file()
        assert 'does not match manifest' in (runtime.FAILED / f'{path.stem}.error').read_text()


def test_extra_file_symlink_and_traversal_fail_closed():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary))
        extra = runtime.SEALED / value['request_id'] / 'extra.html'; extra.write_text('extra')
        with pytest.raises(ValueError, match='files do not match'):
            runtime.stage(value['request_id'], value['file_manifest'])
        value['file_manifest'][0]['path'] = '../escape.html'
        with pytest.raises(ValueError, match='unsafe'):
            runtime.validate_transport(value, path)


def test_mismatched_publisher_receipt_is_not_exposed_to_hermes_processed():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary)); wrong = result(value)
        wrong['base_commit'] = 'c' * 40
        completed = mock.Mock(returncode=0, stdout=json.dumps(wrong), stderr='')
        assert runtime.process(path, runner=mock.Mock(return_value=completed)) == 'failed'
        assert not (runtime.PROCESSED / path.name).exists()


def test_existing_identical_staging_supports_interrupted_run_retry():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary))
        first = runtime.stage(value['request_id'], value['file_manifest'])
        second = runtime.stage(value['request_id'], value['file_manifest'])
        assert first == second


def test_restart_replays_an_interrupted_claim_through_idempotent_publisher():
    with tempfile.TemporaryDirectory() as temporary:
        configure(Path(temporary)); path, value = request(Path(temporary)); expected = result(value)
        claim = runtime.CLAIMS / path.name; path.replace(claim)
        completed = mock.Mock(returncode=0, stdout=json.dumps(expected), stderr='')
        assert runtime.process(claim, runner=mock.Mock(return_value=completed)) == 'processed'
        assert not claim.exists()
        assert json.loads((runtime.PROCESSED / path.name).read_text())['commit'] == expected['commit']
