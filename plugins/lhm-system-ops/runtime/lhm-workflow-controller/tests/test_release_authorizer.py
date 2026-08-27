import hashlib,hmac,importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1];source=ROOT/"packaging/lhm-controller-release-authorizer";loader=SourceFileLoader("release_authorizer",str(source));spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module)

def signed(key,**changes):
    body={"schema_version":1,"action":"install","nonce":"a"*32,"issued_at":100,"expires_at":200,"git_commit":"b"*40,"controller_archive_sha256":"c"*64,"source_tree_release_id":"d"*64,"enablement":{"workflow":False,"barney":False,"delegated":False},"rollback_target":None};body.update(changes);body["hmac_sha256"]=hmac.new(key,module.canonical(body),hashlib.sha256).hexdigest();return body

def valid(approval,key,action="install"):
    return module.validate(approval,key,action=action,archive_sha256="c"*64,source_tree_release_id="d"*64,git_commit="b"*40,now=150)

def test_exact_binding_expiry_and_flags():
    key=b"k"*32;approval=signed(key);assert valid(approval,key)==approval
    for field,value in (("git_commit","e"*40),("controller_archive_sha256","e"*64),("source_tree_release_id","e"*64),("action","rollback")):
        with pytest.raises(ValueError):valid(approval,key,**({"action":value} if field=="action" else {})) if field=="action" else module.validate(approval,key,action="install",archive_sha256=value if field=="controller_archive_sha256" else "c"*64,source_tree_release_id=value if field=="source_tree_release_id" else "d"*64,git_commit=value if field=="git_commit" else "b"*40,now=150)
    with pytest.raises(ValueError,match="expired"):module.validate(approval,key,action="install",archive_sha256="c"*64,source_tree_release_id="d"*64,git_commit="b"*40,now=201)
    tampered={**approval,"enablement":{"workflow":True,"barney":True,"delegated":True}}
    with pytest.raises(ValueError,match="HMAC"):valid(tampered,key)

def test_one_use_claim_is_atomic(tmp_path):
    approval=signed(b"k"*32);claims=tmp_path/"claims";module.claim_once(tmp_path/"ledger",claims,approval)
    assert (claims/f"{approval['nonce']}.json").is_file()
    with pytest.raises(FileExistsError):module.claim_once(tmp_path/"ledger",claims,approval)

def test_rollback_requires_separate_bound_approval():
    key=b"k"*32;approval=signed(key,action="rollback",nonce="f"*32,rollback_target="e"*64);assert valid(approval,key,"rollback")==approval
    with pytest.raises(ValueError,match="action"):valid(approval,key,"install")
