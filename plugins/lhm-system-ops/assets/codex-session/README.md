# TED persistent Codex session pilot

This opt-in route connects a registered BasicOps task to the existing Wellness Codex VPS worker. It does not change other TED delivery routes or provide new live client access.

The MCP bridge reuses TED's existing authenticated BasicOps proxy, verifies the latest TED-authored versioned plan and Michael's recorded approval, checks task/project/ownership, and writes a closed JSON envelope. The worker pins the client workspace and saves an interactive native Codex chat. A model-free timer returns the saved response to the same task, requests native review and assigns Michael in Under Review. A queue acknowledgement is not completion. Drafts remain staged; no Drive delivery is claimed.

## Scoped deployment

Stage `install.py`, `../container/ted_codex_sessions.py`, `../host/lhm-codex-session-worker` and the Project Hub `run-hermes-task/assets/basicops-agent-user/SKILL.md` together on the existing VPS. Run `install.py` as root. It backs up the worker, TED entry skill and configuration before installing the bridge. It registers only integration-test task 2216123 in project 49020, reviewer 36398, TED 82491. This example is deployment-specific: deliberately review and edit that allowlist before adding another task. Configuration remains root-owned; the runtime state belongs to container UID 10000. The queue and worker account must already exist.

Reload only TED's gateway when idle so it discovers the two new MCP tools. Do not restart the entire Hermes container. Verify tools/list and actual identity, then test assignment → TED plan → exact-plan human approval → Codex submission → persisted session → verified same-task review handback. Other tasks must reject the new tool and retain their existing route.

## Retry and rollback

A deterministic task/plan identity plus file locks prevents duplicate submissions. A changed approval or plan is rejected. Handback messages carry a checked marker. Native review requests are checkpointed before sending: an ambiguous API outcome stops for inspection instead of automatically creating a second review request. A new task owner or closed task is preserved. Rejected envelopes and failed workers return a visible blocker to Michael instead of remaining queued. This pilot supports one approved plan per registered task; use another explicitly registered task for a new plan.

To stop the pilot, disable `lhm-ted-codex-handback.timer` and remove the `codex_sessions` MCP registration. Restore `config.yaml`, `SKILL.md` and `lhm-wellness-codex-pilot.py` from the printed root-only backup directory, then reload TED when idle. Retain queue receipts and chats for audit. Do not remove existing account authentication or client context. Never copy authentication tokens into envelopes or source control.

## Validation

Run the bridge unit tests with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/lhm-system-ops/tests -p test_ted_codex_sessions.py`. Test latest-plan approval, identity/project boundaries, duplicate replay, tampered receipt rejection, handback readback and owner preservation. These tests do not substitute for the live integration trial.
