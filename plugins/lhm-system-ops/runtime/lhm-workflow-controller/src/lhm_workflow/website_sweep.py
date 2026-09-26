"""Read-only website project sweep for Lily's morning operating rhythm."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STEP = re.compile(r"^- \[(?P<state>[ xX])\] `(?P<id>WEB-[A-Z]+-[0-9]{3})` (?P<title>.+)$")
FIELD = re.compile(r"^  - (?P<name>[A-Za-z][A-Za-z ]+): (?P<value>.*)$")
METADATA = re.compile(r"(?:^|;)\s*(?P<key>[a-z_]+)=(?P<value>[^;]*)")


class WebsiteSweepError(ValueError):
    """Raised when a project cannot be evaluated safely."""


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    title: str
    complete: bool
    owner: str | None
    depends_on: tuple[str, ...]
    completion: str | None
    basicops: str | None


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise WebsiteSweepError("workflow file has no YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise WebsiteSweepError("workflow frontmatter is not closed")
    result: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if ":" not in raw or raw.startswith((" ", "\t")):
            continue
        key, value = raw.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def parse_workflow(path: Path) -> tuple[dict[str, str], list[WorkflowStep]]:
    text = path.read_text(encoding="utf-8")
    meta = _frontmatter(text)
    steps: list[WorkflowStep] = []
    current: dict | None = None
    for line in text.splitlines():
        match = STEP.match(line)
        if match:
            if current:
                steps.append(_step(current))
            current = {
                "step_id": match["id"],
                "title": match["title"].strip(),
                "complete": match["state"].lower() == "x",
                "fields": {},
            }
            continue
        field = FIELD.match(line)
        if current and field:
            current["fields"][field["name"].lower().replace(" ", "_")] = field["value"].strip()
    if current:
        steps.append(_step(current))
    if not steps:
        raise WebsiteSweepError("workflow file has no stable WEB step IDs")
    ids = [step.step_id for step in steps]
    if len(ids) != len(set(ids)):
        raise WebsiteSweepError("workflow file contains duplicate step IDs")
    return meta, steps


def _step(value: dict) -> WorkflowStep:
    fields = value["fields"]
    raw_dependencies = fields.get("depends_on", "none")
    dependencies = tuple(re.findall(r"WEB-[A-Z]+-[0-9]{3}", raw_dependencies))
    return WorkflowStep(
        step_id=value["step_id"],
        title=value["title"],
        complete=value["complete"],
        owner=fields.get("owner"),
        depends_on=dependencies,
        completion=fields.get("completion"),
        basicops=fields.get("basicops"),
    )


def parse_task_metadata(line: str) -> dict[str, str]:
    prefix = "LHM metadata:"
    if not line.startswith(prefix):
        raise WebsiteSweepError("task is missing governed LHM metadata")
    return {match["key"]: match["value"].strip() for match in METADATA.finditer(line[len(prefix):])}


def load_website_project(vault: Path, client_id: str, project_ref: str) -> dict:
    if not SAFE_ID.fullmatch(client_id) or not SAFE_ID.fullmatch(project_ref):
        raise WebsiteSweepError("unsafe client or project reference")
    record = vault / "_System/Hermes/clients" / client_id / "capabilities.json"
    data = json.loads(record.read_text(encoding="utf-8"))
    if data.get("client", {}).get("id") != client_id:
        raise WebsiteSweepError("client registry identity mismatch")
    website = data.get("capabilities", {}).get("website", {})
    projects = website.get("projects", [])
    matches = [item for item in projects if item.get("project_ref") == project_ref]
    if len(matches) != 1:
        raise WebsiteSweepError("website project mapping is missing or ambiguous")
    project = matches[0]
    required = {
        "project_ref", "workflow_template", "obsidian_project", "basicops_cockpit_id",
        "basicops_cockpit_url", "project_manager", "client_escalation_owner",
        "go_live_date", "morning_sweep",
    }
    if set(project) != required:
        raise WebsiteSweepError("website project mapping has an invalid field set")
    relative = Path(project["obsidian_project"])
    if relative.is_absolute() or ".." in relative.parts:
        raise WebsiteSweepError("website project path escapes the vault")
    project["_path"] = str((vault / relative).resolve())
    if not Path(project["_path"]).is_relative_to(vault.resolve()):
        raise WebsiteSweepError("website project path escapes the vault")
    return project


def evaluate_project(vault: Path, client_id: str, project_ref: str, *, today: date) -> dict:
    project = load_website_project(vault, client_id, project_ref)
    meta, steps = parse_workflow(Path(project["_path"]))
    if meta.get("project_ref") != project_ref or meta.get("workflow_template") != project["workflow_template"]:
        raise WebsiteSweepError("registry and workflow identity do not match")
    complete = {step.step_id for step in steps if step.complete}
    known = {step.step_id for step in steps}
    invalid = sorted({dependency for step in steps for dependency in step.depends_on if dependency not in known})
    if invalid:
        raise WebsiteSweepError(f"unknown workflow dependencies: {', '.join(invalid)}")
    ready = [step for step in steps if not step.complete and set(step.depends_on).issubset(complete)]
    mapped = [step for step in ready if step.basicops and not step.basicops.lower().startswith(("not linked", "not yet", "create only"))]
    # The registry is the machine scheduling contract. The Markdown value is
    # human-readable project state and must not silently fill a missing or
    # stale registry date during an unattended sweep.
    go_live = project["go_live_date"] or None
    days_to_go_live = None
    if go_live:
        try:
            days_to_go_live = (date.fromisoformat(go_live) - today).days
        except ValueError as exc:
            raise WebsiteSweepError("go_live_date must be ISO YYYY-MM-DD") from exc
    alerts: list[dict] = []
    if not go_live:
        alerts.append({"type": "needs_scheduling", "recipient": project["client_escalation_owner"]})
    elif days_to_go_live is not None and days_to_go_live < 0:
        alerts.append({"type": "go_live_overdue", "recipient": project["client_escalation_owner"]})
    elif days_to_go_live is not None and days_to_go_live <= 21:
        alerts.append({"type": "go_live_watch", "recipient": project["client_escalation_owner"]})
    if not project["basicops_cockpit_id"]:
        alerts.append({"type": "missing_basicops_cockpit", "recipient": project["project_manager"]})
    return {
        "schema_version": 1,
        "mode": "read_only",
        "client_id": client_id,
        "project_ref": project_ref,
        "workflow_template": project["workflow_template"],
        "current_phase": meta.get("current_phase"),
        "active_gate": meta.get("active_gate"),
        "immediate_owner": meta.get("immediate_owner"),
        "go_live_date": go_live,
        "days_to_go_live": days_to_go_live,
        "ready_steps": [_step_payload(step) for step in ready],
        "ready_steps_with_existing_task": [step.step_id for step in mapped],
        "alerts": alerts,
        "morning_brief": {
            "ready": True,
            "generated_by": "website_sweep",
            "consume_at": project["morning_sweep"]["morning_hello_time"],
            "timezone": project["morning_sweep"]["timezone"],
        },
        "mutations": [],
    }


def evaluate_board_snapshot(project_result: dict, tasks: list[dict], *, today: date) -> dict:
    """Reconcile a read-only BasicOps export against one evaluated project."""
    project_ref = project_result["project_ref"]
    ready = {item["workflow_step"]: item for item in project_result["ready_steps"]}
    by_step: dict[str, list[dict]] = {}
    ignored: list[str] = []
    for task in tasks:
        task_id = str(task.get("id", ""))
        try:
            metadata = parse_task_metadata(str(task.get("description", "")).splitlines()[0])
        except (WebsiteSweepError, IndexError):
            ignored.append(task_id)
            continue
        if metadata.get("work_type") != "project-task" or metadata.get("service") != "website":
            ignored.append(task_id)
            continue
        if metadata.get("project_ref") != project_ref:
            continue
        step_id = metadata.get("workflow_step", "")
        if not re.fullmatch(r"WEB-[A-Z]+-[0-9]{3}", step_id):
            ignored.append(task_id)
            continue
        by_step.setdefault(step_id, []).append(task)

    duplicates: list[dict] = []
    overdue: list[dict] = []
    reconciliation: list[dict] = []
    open_steps: set[str] = set()
    complete_status = {"complete", "completed"}
    for step_id, matches in sorted(by_step.items()):
        open_tasks = [task for task in matches if str(task.get("status", "")).lower() not in complete_status]
        complete_tasks = [task for task in matches if str(task.get("status", "")).lower() in complete_status]
        if len(open_tasks) > 1:
            duplicates.append({"workflow_step": step_id, "task_ids": [str(task.get("id")) for task in open_tasks]})
        if open_tasks:
            open_steps.add(step_id)
        if complete_tasks and step_id in ready:
            reconciliation.append({
                "workflow_step": step_id,
                "task_ids": [str(task.get("id")) for task in complete_tasks],
                "action": "verify evidence then reconcile Obsidian",
            })
        for task in open_tasks:
            due = task.get("due_date")
            if due and date.fromisoformat(str(due)) < today:
                overdue.append({
                    "workflow_step": step_id,
                    "task_id": str(task.get("id")),
                    "owner": task.get("assignee"),
                    "due_date": due,
                    "alert_owner": True,
                    "alert_kristalyn": True,
                })

    candidates = [value for step_id, value in ready.items() if step_id not in open_steps and not any(
        item["workflow_step"] == step_id for item in reconciliation
    )]
    return {
        "mode": "read_only",
        "matched_steps": sorted(by_step),
        "ignored_task_ids": sorted(ignored),
        "duplicates": duplicates,
        "overdue": overdue,
        "obsidian_reconciliation": reconciliation,
        "next_task_candidates": candidates,
        "mutations": [],
    }


def _step_payload(step: WorkflowStep) -> dict:
    return {
        "workflow_step": step.step_id,
        "title": step.title,
        "owner": step.owner,
        "depends_on": list(step.depends_on),
        "completion": step.completion,
        "basicops": step.basicops,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run Lily's read-only website project sweep")
    parser.add_argument("client_id")
    parser.add_argument("project_ref")
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--board-snapshot", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_project(args.vault.resolve(), args.client_id, args.project_ref, today=date.fromisoformat(args.date))
    if args.board_snapshot:
        tasks = json.loads(args.board_snapshot.read_text(encoding="utf-8"))
        if not isinstance(tasks, list):
            raise WebsiteSweepError("board snapshot must be a JSON task list")
        result["board"] = evaluate_board_snapshot(result, tasks, today=date.fromisoformat(args.date))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
