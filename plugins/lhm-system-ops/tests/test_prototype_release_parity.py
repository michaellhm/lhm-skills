import importlib.util
import json
import zipfile
from importlib.machinery import SourceFileLoader
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
ASSET = PLUGIN / 'assets/host/lhm-prototype-publisher'
FIXTURE = PLUGIN / 'tests/fixtures/asp-sitemap-v2-publication.request.json'


def load_asset(path):
    spec = importlib.util.spec_from_loader('packaged_prototype_publisher', SourceFileLoader('packaged_prototype_publisher', str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_asset_accepts_exact_asp_v2_contract(tmp_path):
    archive = tmp_path / 'lhm-system-ops.zip'
    member = 'lhm-system-ops/assets/host/lhm-prototype-publisher'
    with zipfile.ZipFile(archive, 'w') as package:
        package.write(ASSET, member)
    with zipfile.ZipFile(archive) as package:
        package.extract(member, tmp_path / 'installed')
    installed = tmp_path / 'installed' / member
    publisher = load_asset(installed)
    request = json.loads(FIXTURE.read_text(encoding='utf-8'))
    assert publisher.validate_contract(request) == request
    assert publisher.FIELDS == set(request)
    assert publisher.package_digest(request['file_manifest']) == request['source_package_sha256']


def test_packaged_schema_drift_breaks_asp_fixture(tmp_path):
    drifted = tmp_path / 'lhm-prototype-publisher'
    drifted.write_text(ASSET.read_text(encoding='utf-8').replace("r.get('schema_version')!=2", "r.get('schema_version')!=1"), encoding='utf-8')
    publisher = load_asset(drifted)
    request = json.loads(FIXTURE.read_text(encoding='utf-8'))
    try:
        publisher.validate_contract(request)
    except ValueError as exc:
        assert 'schema' in str(exc)
    else:
        raise AssertionError('schema drift unexpectedly accepted the approved ASP v2 fixture')
