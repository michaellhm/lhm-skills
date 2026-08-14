---
title: Google Ads Monthly Operating Model
description: The review, approval, dispatch and resumable handback contract shared by Hermes and Google Ads specialists.
---

# Google Ads Monthly Operating Model

Hermes is the control tower. A specialist worker gathers evidence and performs approved work. Obsidian is canonical context and workflow memory; Google Drive holds the human-readable report; BasicOps exposes the review and action queue.

## Review sequence

Run these stages in order:

1. **Canonical context** — Hermes resolves the client in the Obsidian vault and supplies a context envelope containing the canonical service-file path, objectives, conversion definitions, locations, budget and targets, campaign strategy, open issues, prior decisions, prior commitments, Drive destination and existing BasicOps record. Never create blank `goals.md`, `current-projects.md` or `client_profile.md` beside the plugin. If a canonical field is missing, record the precise gap and continue only where the remaining evidence supports it.
2. **Read-only specialist evidence** — the worker pulls the current 30 days and immediately preceding 30 days; reconciles prior commitments against live settings; checks Google Ads conversion actions; and cross-checks GA4 over the same windows whenever conversions are zero, falling, inconsistent or otherwise suspicious. Pull AdPulse `pacing` and `kpiPercentage` when available. When it is unavailable, explicitly label the manual pacing/performance calculation as a fallback.
3. **Two judgements** — report the **performance zone** separately from **measurement confidence** (`high`, `medium`, or `low`). Determine the matrix's performance axis against the canonical business CPA/ROAS target, not against the prior period. Period-over-period change is an important trend, but it is not a substitute profitability target. A tracking concern can lower measurement confidence and raise an urgent action, but does not by itself change the performance zone. If evidence is too unreliable to classify performance, use `performance_zone: unclassified`; do not invent Red. An operational caution such as “treat as Orange” may accompany a mechanical Yellow result, but must not relabel the mechanical zone.
4. **Verified Drive one-pager** — the specialist saves and reads back the monthly report using the canonical Drive destination and returns the observed URL/file ID.
5. **Hermes overview** — Hermes presents the compact state summary, headline findings, performance zone, measurement confidence and no more than five proposed actions. Each action names the evidence, expected outcome, specialist skill and whether a live mutation would require a further approval.
6. **BasicOps review record** — create or update one parent monthly-review task. Keep only the governed metadata line and useful URLs in its description. Put the overview, top five and approval question in the discussion. Do not create execution subtasks before approval. Set the workflow state to waiting for Michael through Hermes.
7. **Approval gate** — stop. Michael may approve, modify, defer or reject any subset through Hermes. A report save, BasicOps write or recommendation is never approval for a Google Ads mutation.
8. **Sequential dispatch** — after approval, Hermes dispatches exactly one approved action to its specialist skill. Do not start the next action until the current worker has returned evidence and Hermes has recorded its outcome. Every live mutation observes the owning skill's approval gate.
9. **Completion loop** — after each action, Hermes updates the canonical Obsidian service file and the BasicOps parent discussion (and approved subtask, if one was created), then either dispatches the next approved action or returns to a waiting state.

## BasicOps workflow state

Use the exact governed metadata format in `lhm-project-hub:basicops-task-manager`, followed only by useful URLs. For the normal morning handoff, its orchestration fields are:

`handoff_trigger=waiting; next_handoff=Michael via Hermes; handoff_channel=basicops; orchestration_owner=hermes; workflow_state=waiting-on-michael-via-hermes; approval_status=pending-michael`

The remaining required metadata fields keep their governed values for recurring Google Ads delivery. Do not introduce a second pipe-delimited metadata schema.

The human Discussion carries the stable run month, action IDs and resume instruction. Internal structured-handback statuses may use snake case, but map them to BasicOps metadata as follows:

- `waiting_michael_hermes` -> `workflow_state=waiting-on-michael-via-hermes`
- `dispatch_ready` -> `workflow_state=approved`
- `specialist_running` -> `workflow_state=executing`; active subtask `workflow_state=waiting-on-agent`
- `waiting_approval` -> `workflow_state=ready-for-review`
- `needs_review` -> `workflow_state=blocked` or `ready-for-review`, according to the evidence
- `complete` -> `workflow_state=complete`

The discussion must say what Michael is deciding and how Hermes should resume.

## Structured handback

Every monthly review and dispatched action returns this block to Hermes. Use valid YAML and preserve stable action IDs across resumptions.

```yaml
google_ads_monthly_handback:
  schema_version: 1
  client: "Client Name"
  run_month: "YYYY-MM"
  phase: review | execution
  status: waiting_michael_hermes | dispatch_ready | specialist_running | waiting_approval | needs_review | complete
  waiting_on: michael_via_hermes | hermes | specialist | none
  performance_zone:
    value: red | orange | yellow | blue | green | unclassified
    source: adpulse | manual_fallback | unavailable
    rationale: "Short evidence-led explanation"
  measurement_confidence:
    value: high | medium | low
    issues: []
  evidence:
    current_window: "YYYY-MM-DD/YYYY-MM-DD"
    comparison_window: "YYYY-MM-DD/YYYY-MM-DD"
    google_ads_pull: "observed pull id/time"
    ga4_cross_check: "observed result or not-triggered with reason"
    adpulse: "observed result or unavailable"
    prior_commitments_checked: []
  artefact:
    drive_url: "verified URL or null"
    verified: true
  basicops:
    task_url: "observed URL or null"
    workflow_state: waiting-on-michael-via-hermes
    approval_status: pending-michael
  proposed_actions:
    - id: GA-01
      title: "Action"
      evidence: "Why it matters"
      expected_outcome: "What success looks like"
      skill: keyword-optimizer
      mutation_scope: read_only | approval_required
      decision: pending | approved | modified | rejected | deferred
      execution_status: not_started | running | waiting_approval | complete | blocked
  next_prompt: "The concise question Hermes should ask Michael"
  mutations_performed: none
```

After an action completes, return its before/after values, tool evidence, Drive artefact if applicable, mutations performed, and verification result. Never mark an action complete from an instruction alone.
