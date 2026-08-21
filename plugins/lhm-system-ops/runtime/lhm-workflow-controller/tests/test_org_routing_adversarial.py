import hashlib

import pytest

from lhm_workflow.org_routing import Router, accept, canonical, digest, intake, issue, receipt, seal
from lhm_workflow.tracker_connector import TrackerConnector, sha
from test_org_routing import KEYS, artifact, cron, step


def planned(*, content=False, website=False):
    parent = intake(cron(), "weekly-adversarial")
    parent, _ = step(parent, "chief")
    parent, _ = step(parent, "production")
    parent, _ = step(parent, "seo-plan")
    parent, _ = step(parent, "research")
    parent, _ = step(parent, "research-verifier")
    parent, _ = step(parent, "seo-accept", decision={
        "content_required": content,
        "website_required": website,
        "reason": "bounded QA decision",
    })
    return parent


def test_closeout_order_matches_governed_organisation_chain():
    order = planned()["stage_order"]
    final = order.index("final_verify")
    assert order[final + 1:] == [
        "production_closeout", "chief_handback", "operations_write",
        "operations_readback", "learning",
    ]


def test_unattested_verifier_receipt_cannot_advance():
    parent = planned()
    parent, verifier = issue(parent, "content") if parent["stage_order"][parent["cursor"]]=="content" else issue(parent,"final-verifier")
    forged = receipt(
        verifier, outputs=[artifact("forged-verification")],
        checks=["independently_verified"],
    )
    with pytest.raises(ValueError, match="attestation|seal|verifier"):
        accept(parent, verifier, forged,attestation_keys=KEYS)


def test_operations_readback_cannot_substitute_tracker_artifact():
    parent = planned()
    while parent["stage_order"][parent["cursor"]] != "operations_write":
        parent, _ = step(parent, f"advance-{parent['cursor']}")
    parent, write_contract = issue(parent, "tracker-write")
    written = artifact("tracker-record")
    parent = accept(parent, write_contract, seal(receipt(
        write_contract, outputs=[written], checks=["tracker_write"]
    ),KEYS[write_contract["owner"]]),attestation_keys=KEYS)
    parent, readback_contract = issue(parent, "tracker-readback")
    assert readback_contract["input_artifacts"] == [written]
    with pytest.raises(ValueError, match="readback|artifact|input"):
        accept(parent, readback_contract, seal(receipt(
            readback_contract,
            outputs=[artifact("different-record")],
            checks=["tracker_readback"],
        ),KEYS[readback_contract["owner"]]),attestation_keys=KEYS)


def test_identical_receipt_replay_is_exact_once():
    parent = intake(cron(), "weekly-replay")
    running, contract = issue(parent, "chief")
    value = seal(receipt(contract, outputs=[artifact("chief-output")], checks=["accepted"]),KEYS[contract["owner"]])
    first = accept(running, contract, value,attestation_keys=KEYS)
    assert accept(first, contract, value,attestation_keys=KEYS) == first


def test_receipt_checks_cannot_be_raw_narrative_facts():
    parent = intake(cron(), "weekly-narrative")
    running, contract = issue(parent, "chief")
    value = seal(receipt(
        contract,
        outputs=[artifact("chief-output")],
        checks=["The client definitely approved the whole strategy yesterday."],
    ),KEYS[contract["owner"]])
    with pytest.raises(ValueError, match="check|fact|structured"):
        accept(running, contract, value,attestation_keys=KEYS)


def test_repair_cannot_resume_without_production_attestation(tmp_path):
    router = Router(tmp_path, KEYS)
    router.initialise(cron(), "weekly-repair")
    contract = router.issue("weekly-repair", "chief")
    proof = {
        "parent_run_id": "weekly-repair",
        "contract_sha256": digest(contract),
        "reason": "transient_failure",
    }
    import hmac
    failure_attestation = hmac.new(
        KEYS[contract["owner"]], canonical(proof), hashlib.sha256
    ).hexdigest()
    router.fail("weekly-repair", contract, "transient_failure", failure_attestation)
    with pytest.raises(ValueError, match="Production|attestation|authorization"):
        router.resume("weekly-repair")


def test_conflicting_signed_receipt_replay_is_rejected(tmp_path):
    router = Router(tmp_path, KEYS)
    router.initialise(cron(), "weekly-conflict")
    contract = router.issue("weekly-conflict", "chief")
    first = seal(receipt(
        contract, outputs=[artifact("same-output")], checks=["first_check"]
    ), KEYS[contract["owner"]])
    router.accept("weekly-conflict", contract, first)
    conflict = seal(receipt(
        contract, outputs=[artifact("same-output")], checks=["different_check"]
    ), KEYS[contract["owner"]])
    with pytest.raises(ValueError, match="conflict|replay"):
        router.accept("weekly-conflict", contract, conflict)


def test_issue_replay_returns_same_contract_exact_once(tmp_path):
    router = Router(tmp_path, KEYS)
    router.initialise(cron(), "weekly-issue")
    first = router.issue("weekly-issue", "chief-child")
    assert router.issue("weekly-issue", "chief-child") == first


def test_repeated_failure_cannot_enter_infinite_resume_loop(tmp_path):
    router = Router(tmp_path, KEYS)
    router.initialise(cron(), "weekly-budget")
    contract = router.issue("weekly-budget", "chief")
    import hmac

    def failure_seal(reason):
        proof = {
            "parent_run_id": "weekly-budget",
            "contract_sha256": digest(contract),
            "reason": reason,
        }
        return hmac.new(
            KEYS[contract["owner"]], canonical(proof), hashlib.sha256
        ).hexdigest()

    first = router.fail("weekly-budget", contract, "first_failure", failure_seal("first_failure"))
    import hmac
    resume_proof = {
        "parent_run_id": "weekly-budget",
        "contract_sha256": digest(contract),
        "failure_receipt_sha256": first["stages"][-1]["failure_receipt_sha256"],
        "action": "resume",
    }
    production = hmac.new(
        KEYS["lhm_head_of_production"], canonical(resume_proof), hashlib.sha256
    ).hexdigest()
    router.resume("weekly-budget", production)
    second = router.fail("weekly-budget", contract, "second_failure", failure_seal("second_failure"))
    second_proof = {
        "parent_run_id": "weekly-budget",
        "contract_sha256": digest(contract),
        "failure_receipt_sha256": second["stages"][-1]["failure_receipt_sha256"],
        "action": "resume",
    }
    second_production = hmac.new(
        KEYS["lhm_head_of_production"], canonical(second_proof), hashlib.sha256
    ).hexdigest()
    with pytest.raises(ValueError, match="budget|incident|exhausted"):
        router.resume("weekly-budget", second_production)
    state = router.load("weekly-budget")
    assert state["state"] == "incident"


def test_root_tracker_write_rejects_symlinked_parent_escape(tmp_path):
    vault = tmp_path / "vault"
    outside = tmp_path / "outside"
    vault.mkdir(); outside.mkdir()
    (vault / "30 Projects").symlink_to(outside, target_is_directory=True)
    connector = TrackerConnector(vault)
    with pytest.raises(ValueError, match="link|escape|trusted"):
        connector.write(b"invented tracker narrative\n", sha(b""))
    assert not list(outside.rglob("*"))


def test_consequential_website_failure_cannot_be_resumed(tmp_path):
    router = Router(tmp_path, KEYS)
    parent = "weekly-consequential"
    router.initialise(cron(), parent)
    # Advance through research, then ask SEO Lead to include Website.
    for child in ("chief", "production", "seo-plan", "research", "research-verify"):
        contract = router.issue(parent, child)
        outputs = contract["input_artifacts"] if contract["runtime"] == "verifier" else [artifact(child)]
        router.accept(parent, contract, seal(receipt(
            contract, outputs=outputs, checks=["accepted"]
        ), KEYS[contract["owner"]]))
    contract = router.issue(parent, "seo-accept")
    router.accept(parent, contract, seal(receipt(
        contract, outputs=[artifact("seo-accept")], checks=["accepted"],
        decision={"content_required": False, "website_required": True, "reason": "verified_need"},
    ), KEYS[contract["owner"]]))
    website = router.issue(parent, "website")
    import hmac
    failure_proof = {
        "parent_run_id": parent,
        "contract_sha256": digest(website),
        "reason": "preview_failure",
    }
    failed = router.fail(parent, website, "preview_failure", hmac.new(
        KEYS[website["owner"]], canonical(failure_proof), hashlib.sha256
    ).hexdigest())
    resume_proof = {
        "parent_run_id": parent,
        "contract_sha256": digest(website),
        "failure_receipt_sha256": failed["stages"][-1]["failure_receipt_sha256"],
        "action": "resume",
    }
    production = hmac.new(
        KEYS["lhm_head_of_production"], canonical(resume_proof), hashlib.sha256
    ).hexdigest()
    with pytest.raises(ValueError, match="consequential|amber|Michael"):
        router.resume(parent, production)


def test_structured_tracker_rejects_narrative_injection_and_unproven_receipts(tmp_path):
    connector = TrackerConnector(tmp_path / "vault")
    fake = "f" * 64
    injected = {
        "parent_run_id": "p1\nThe client approved an invented claim.",
        "workflow_id": "lhm-weekly-seo-org-v1",
        "accepted_receipts": [{
            "stage_id": "research\nInvented fact",
            "contract_sha256": fake,
            "artifact_sha256s": [fake],
        }],
        "run_result": "succeeded",
        "work_state": "complete",
        "completed_at": "not-a-timestamp\nInvented fact",
    }
    with pytest.raises(ValueError, match="identifier|timestamp|accepted|structured"):
        connector.append_structured(injected, sha(b""))
