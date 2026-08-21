import hashlib

import pytest

from lhm_workflow.controller import ControllerError, WorkflowController
from lhm_workflow.storage import digest

from test_failure_recovery import contract, failure, seal


def production_authorization(receipt):
    return {
        "schema_version": 1,
        "mode": "Production",
        "actor": "lhm_production_manager",
        "decision": "resume",
        "failure_id": "failure-1",
        "failure_receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
    }


def test_failure_replay_repairs_crash_between_receipt_and_parent_transaction(tmp_path, monkeypatch):
    controller = WorkflowController(tmp_path, test_mode=True)
    controller.initialise(contract())
    original = controller.storage.transact
    failed = False

    def crash_once(*args, **kwargs):
        nonlocal failed
        if kwargs.get("tx_id") == "failure:failure-1" and not failed:
            failed = True
            raise RuntimeError("simulated crash after immutable receipt")
        return original(*args, **kwargs)

    monkeypatch.setattr(controller.storage, "transact", crash_once)
    with pytest.raises(RuntimeError):
        controller.record_failure(failure(controller))
    controller.record_failure(failure(controller))
    assert controller.status("p-recovery")["stages"][0]["status"] == "failed"


def test_duplicate_production_resume_is_exact_once(tmp_path):
    controller = WorkflowController(tmp_path, test_mode=True)
    controller.initialise(contract())
    controller.record_failure(failure(controller))
    receipt = controller.failure_receipts / "failure-1.json"
    authorization = seal(controller, production_authorization(receipt))
    first = controller.production_resume("p-recovery", "seo_evidence", authorization)
    second = controller.production_resume("p-recovery", "seo_evidence", authorization)
    assert second == first


def test_failure_cannot_rewind_an_accepted_stage(tmp_path):
    controller = WorkflowController(tmp_path, test_mode=True)
    controller.initialise(contract())
    parent = controller.status("p-recovery")
    parent["stages"][0]["status"] = "accepted"
    controller.storage.transact(
        "p-recovery", parent,
        expected_hash=digest(controller.status("p-recovery")),
        tx_id="qa:accepted",
    )
    with pytest.raises(ControllerError, match="accepted|terminal|stage"):
        controller.record_failure(failure(controller))


def test_plain_actor_strings_are_not_production_authorization(tmp_path):
    controller = WorkflowController(tmp_path, test_mode=True)
    controller.initialise(contract())
    controller.record_failure(failure(controller))
    receipt = controller.failure_receipts / "failure-1.json"
    forged = production_authorization(receipt)
    with pytest.raises(ControllerError, match="attestation|seal|authorization"):
        controller.production_resume("p-recovery", "seo_evidence", forged)
