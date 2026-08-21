import json
from pathlib import Path

import pytest

from integration import reconcile_site_launch as recovery


def setup(tmp_path, events):
    dispatch=tmp_path/"dispatch"; workflow=tmp_path/"workflow"
    for name in ("site-runs","site-snapshots","site-drafts","site-artifacts","site-processed","site-incoming"):
        (dispatch/name).mkdir(parents=True)
    child="child-1"; run=dispatch/"site-runs"/child; run.mkdir(); (run/"final.json").write_text(json.dumps({"status":"failed"}))
    (dispatch/"site-snapshots"/child).mkdir(); (dispatch/"site-drafts"/child).mkdir()
    (dispatch/"site-processed"/f"{child}.json").write_text("{}")
    (workflow/"host-events").mkdir(parents=True)
    (workflow/"host-events"/f"{child}.jsonl").write_text("\n".join(json.dumps(x) for x in events)+"\n")
    (workflow/"host-events"/f"{child}.lock").write_text("")
    (dispatch/"site-reconciliation").mkdir()
    return dispatch,workflow,child


def test_admission_only_failed_launch_is_requeued_with_archive(tmp_path,monkeypatch):
    dispatch,workflow,child=setup(tmp_path,[{"event":"dispatch_admitted"}])
    monkeypatch.setattr(recovery.os,"geteuid",lambda:0); monkeypatch.setattr(recovery,"inactive",lambda unit:True)
    monkeypatch.setattr(recovery,"ROOT_UID",recovery.os.getuid()); monkeypatch.setattr(recovery,"WORKER_UID",recovery.os.getuid())
    archive=recovery.reconcile(child,dispatch=dispatch,workflow=workflow)
    assert (dispatch/"site-incoming"/f"{child}.json").is_file()
    assert (archive/"run"/"final.json").is_file()
    assert (workflow/"host-events"/f"{child}.jsonl").is_file()


def test_failure_after_skill_observation_requires_new_child(tmp_path,monkeypatch):
    dispatch,workflow,child=setup(tmp_path,[{"event":"dispatch_admitted"},{"event":"skill_invoked"}])
    monkeypatch.setattr(recovery.os,"geteuid",lambda:0); monkeypatch.setattr(recovery,"inactive",lambda unit:True)
    monkeypatch.setattr(recovery,"ROOT_UID",recovery.os.getuid()); monkeypatch.setattr(recovery,"WORKER_UID",recovery.os.getuid())
    with pytest.raises(SystemExit,match="new child id"):
        recovery.reconcile(child,dispatch=dispatch,workflow=workflow)
    assert (dispatch/"site-runs"/child).is_dir()
    assert not (dispatch/"site-incoming"/f"{child}.json").exists()

def test_symlinked_recovery_input_fails_before_any_move(tmp_path,monkeypatch):
    dispatch,workflow,child=setup(tmp_path,[{"event":"dispatch_admitted"}])
    processed=dispatch/"site-processed"/f"{child}.json"; real=tmp_path/"real.json"; real.write_text("{}")
    processed.unlink(); processed.symlink_to(real)
    monkeypatch.setattr(recovery.os,"geteuid",lambda:0); monkeypatch.setattr(recovery,"inactive",lambda unit:True)
    monkeypatch.setattr(recovery,"ROOT_UID",recovery.os.getuid()); monkeypatch.setattr(recovery,"WORKER_UID",recovery.os.getuid())
    with pytest.raises(SystemExit,match="unsafe recovery input"):
        recovery.reconcile(child,dispatch=dispatch,workflow=workflow)
    assert (dispatch/"site-runs"/child).is_dir()
