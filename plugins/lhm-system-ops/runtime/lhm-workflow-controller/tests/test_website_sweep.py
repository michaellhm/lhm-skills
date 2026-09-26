import json
from datetime import date

import pytest

from lhm_workflow.website_sweep import WebsiteSweepError, evaluate_board_snapshot, evaluate_project, parse_task_metadata


def setup_project(tmp_path, *, go_live="2026-09-18", cockpit_id="123"):
    vault = tmp_path / "vault"
    workflow = vault / "20 Clients/Example/project-management/Website Workflow.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
project_ref: example-website-rebuild
workflow_template: website-rebuild-v1
current_phase: development
active_gate: staging-review
immediate_owner: Aiya
go_live_date: 2026-09-18
---
# Workflow
- [x] `WEB-KICKOFF-010` Confirm kickoff
  - Owner: Kristalyn
  - Completion: Route recorded
- [ ] `WEB-BUILD-010` Build staging pages
  - Owner: Aiya
  - Depends on: `WEB-KICKOFF-010`
  - Completion: Staging URL verified
  - BasicOps: https://app.basicops.test/task/1
- [ ] `WEB-REVIEW-010` Review staging
  - Owner: Kristalyn
  - Depends on: `WEB-BUILD-010`
  - Completion: Review closed
  - BasicOps: Not yet ready
"""
    )
    record = vault / "_System/Hermes/clients/example/capabilities.json"
    record.parent.mkdir(parents=True)
    record.write_text(json.dumps({
        "schema_version": 1,
        "client": {"id": "example", "name": "Example", "type": "client"},
        "capabilities": {"website": {
            "projects": [{
                "project_ref": "example-website-rebuild",
                "workflow_template": "website-rebuild-v1",
                "obsidian_project": "20 Clients/Example/project-management/Website Workflow.md",
                "basicops_cockpit_id": cockpit_id,
                "basicops_cockpit_url": "https://app.basicops.test/project/123",
                "project_manager": "Kristalyn",
                "client_escalation_owner": "Kristalyn",
                "go_live_date": go_live,
                "morning_sweep": {"sweep_time": "08:00", "morning_hello_time": "09:00", "timezone": "Australia/Melbourne"},
            }]
        }}
    }))
    return vault


def test_read_only_sweep_selects_dependency_cleared_step(tmp_path):
    result = evaluate_project(setup_project(tmp_path), "example", "example-website-rebuild", today=date(2026, 8, 28))
    assert result["mode"] == "read_only" and result["mutations"] == []
    assert [item["workflow_step"] for item in result["ready_steps"]] == ["WEB-BUILD-010"]
    assert result["ready_steps_with_existing_task"] == ["WEB-BUILD-010"]
    assert result["morning_brief"]["consume_at"] == "09:00"


def test_missing_schedule_and_cockpit_alert_kristalyn(tmp_path):
    result = evaluate_project(setup_project(tmp_path, go_live="", cockpit_id=""), "example", "example-website-rebuild", today=date(2026, 8, 28))
    assert result["alerts"] == [
        {"type": "needs_scheduling", "recipient": "Kristalyn"},
        {"type": "missing_basicops_cockpit", "recipient": "Kristalyn"},
    ]


def test_registry_and_workflow_identity_must_match(tmp_path):
    vault = setup_project(tmp_path)
    workflow = vault / "20 Clients/Example/project-management/Website Workflow.md"
    workflow.write_text(workflow.read_text().replace("example-website-rebuild", "wrong-project"))
    with pytest.raises(WebsiteSweepError, match="identity"):
        evaluate_project(vault, "example", "example-website-rebuild", today=date(2026, 8, 28))


def test_task_metadata_requires_project_and_workflow_step():
    parsed = parse_task_metadata("LHM metadata: work_type=project-task; service=website; project_ref=example-website-rebuild; workflow_step=WEB-BUILD-010")
    assert parsed["project_ref"] == "example-website-rebuild"
    assert parsed["workflow_step"] == "WEB-BUILD-010"
    with pytest.raises(WebsiteSweepError, match="metadata"):
        parse_task_metadata("ordinary description")


def test_board_snapshot_finds_overdue_reconciliation_and_next_task_candidates(tmp_path):
    project = evaluate_project(setup_project(tmp_path), "example", "example-website-rebuild", today=date(2026, 8, 28))
    build_metadata = "LHM metadata: work_type=project-task; service=website; project_ref=example-website-rebuild; workflow_step=WEB-BUILD-010"
    board = evaluate_board_snapshot(project, [{
        "id": "task-1", "description": build_metadata, "status": "Complete",
        "assignee": "Aiya", "due_date": "2026-08-27",
    }], today=date(2026, 8, 28))
    assert board["obsidian_reconciliation"] == [{
        "workflow_step": "WEB-BUILD-010", "task_ids": ["task-1"],
        "action": "verify evidence then reconcile Obsidian",
    }]
    assert board["next_task_candidates"] == []
    assert board["mutations"] == []


def test_board_snapshot_alerts_owner_and_kristalyn_for_overdue_open_work(tmp_path):
    project = evaluate_project(setup_project(tmp_path), "example", "example-website-rebuild", today=date(2026, 8, 28))
    metadata = "LHM metadata: work_type=project-task; service=website; project_ref=example-website-rebuild; workflow_step=WEB-BUILD-010"
    board = evaluate_board_snapshot(project, [{
        "id": "task-2", "description": metadata, "status": "In Progress",
        "assignee": "Aiya", "due_date": "2026-08-27",
    }], today=date(2026, 8, 28))
    assert board["overdue"] == [{
        "workflow_step": "WEB-BUILD-010", "task_id": "task-2", "owner": "Aiya",
        "due_date": "2026-08-27", "alert_owner": True, "alert_kristalyn": True,
    }]
