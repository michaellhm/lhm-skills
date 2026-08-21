import hashlib,json,os
from pathlib import Path
import pytest

from lhm_workflow.client_preflight import ClientOnboardingRequired,require_capability

OPS=["list_sites","batch_url_inspection","search_analytics","list_sitemaps"]
PROP="sc-domain:example.test"

def fixture(tmp_path):
    evidence=tmp_path/"evidence.json"
    evidence.write_text(json.dumps({"requests":{"research.json":{"value":{"profile":"seo_gsc_readonly","required_capabilities":["google_search_console.property_read"],"site_property":PROP}}}})); evidence.chmod(0o600)
    vault=tmp_path/"vault"; record=vault/"_System/Hermes/clients/example/capabilities.json"; record.parent.mkdir(parents=True)
    value={"client":{"id":"example"},"capabilities":{"google_search_console":{"status":"verified","route":"seo_gsc_readonly","identifiers":{"property":PROP},"allowed_operations":OPS,"last_test":{"result":"passed","evidence_ref":str(evidence),"evidence_sha256":hashlib.sha256(evidence.read_bytes()).hexdigest(),"binding":{"client_id":"example","property":PROP,"capability":"google_search_console.property_read","allowed_operations":OPS}}}}}
    record.write_text(json.dumps(value)); record.chmod(0o600)
    return vault,record,evidence

def test_verified_evidence_is_exact_and_bound(tmp_path):
    vault,_,_=fixture(tmp_path)
    assert require_capability(vault,"example","google_search_console",test_mode=True)["identifiers"]["property"]==PROP

@pytest.mark.parametrize("target",["record","evidence"])
def test_group_readable_or_writable_files_are_rejected(tmp_path,target):
    vault,record,evidence=fixture(tmp_path); (record if target=="record" else evidence).chmod(0o640)
    with pytest.raises(ClientOnboardingRequired,match="owner or mode"):
        require_capability(vault,"example","google_search_console",test_mode=True)

def test_symlinked_evidence_is_rejected(tmp_path):
    vault,record,evidence=fixture(tmp_path); real=tmp_path/"real.json"; evidence.rename(real); evidence.symlink_to(real)
    with pytest.raises(ClientOnboardingRequired,match="evidence.*(?:type|link)"):
        require_capability(vault,"example","google_search_console",test_mode=True)

def test_wrong_property_or_capability_binding_is_rejected(tmp_path):
    vault,record,evidence=fixture(tmp_path)
    evidence.write_text(json.dumps({"requests":{"research.json":{"value":{"profile":"other","required_capabilities":[],"site_property":"sc-domain:wrong.test"}}}})); evidence.chmod(0o600)
    value=json.loads(record.read_text()); value["capabilities"]["google_search_console"]["last_test"]["evidence_sha256"]=hashlib.sha256(evidence.read_bytes()).hexdigest(); record.write_text(json.dumps(value)); record.chmod(0o600)
    with pytest.raises(ClientOnboardingRequired,match="binding mismatch"):
        require_capability(vault,"example","google_search_console",test_mode=True)
