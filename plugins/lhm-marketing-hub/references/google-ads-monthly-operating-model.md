---
title: Google Ads Monthly Operating Model
description: The review, approval, dispatch and resumable handback contract shared by Hermes and Google Ads specialists.
---

# Google Ads Monthly Operating Model

Hermes is the control tower. The `google-ads` agent is the departmental Lead. Bounded workers execute specialist skills, Google Ads Delivery QA checks every returned action, Head of Production accepts the completed dossier, and Learning Steward routes verified learning. Obsidian is canonical context and workflow memory; Google Drive holds the human-readable report; BasicOps exposes the review and action queue.

Read `references/google-ads-departmental-delivery.md` before approved execution. This monthly model decides what matters; the departmental contract governs how approved work is prepared, checked, accepted and learned from.

## Review sequence

Run these stages in order:

1. **Canonical context** — Hermes resolves the client in the Obsidian vault and supplies a context envelope containing the canonical service-file path, objectives, conversion definitions, locations, budget and targets, campaign strategy, open issues, prior decisions, prior commitments, Drive destination and existing BasicOps record. Never create blank `goals.md`, `current-projects.md` or `client_profile.md` beside the plugin. If a canonical field is missing, record the precise gap and continue only where the remaining evidence supports it.
2. **Read-only specialist evidence** — the worker pulls the current 30 days and immediately preceding 30 days; reconciles prior commitments against live settings; runs `bid-budget-optimizer` across every active campaign; runs `google-ads-conversion-audit` across account and campaign goal settings; triggers `keyword-optimizer` when search waste, negatives, match types or dormant/duplicated search structure appear; and cross-checks GA4 whenever firing or import state is unclear. Pull AdPulse `pacing` and `kpiPercentage` when available. When it is unavailable, explicitly label the manual pacing/performance calculation as a fallback.
3. **Two judgements** — report the **performance zone** separately from **measurement confidence** (`high`, `medium`, or `low`). Determine the matrix's performance axis against the canonical business CPA/ROAS target, not against the prior period. Period-over-period change is an important trend, but it is not a substitute profitability target. A tracking concern can lower measurement confidence and raise an urgent action, but does not by itself change the performance zone. If evidence is too unreliable to classify performance, use `performance_zone: unclassified`; do not invent Red. An operational caution such as “treat as Orange” may accompany a mechanical Yellow result, but must not relabel the mechanical zone.
4. **Lead action selection and authority classification** — the Google Ads Lead uses the matched zone's action library as candidates, then selects no more than five resolved actions using the returned specialist evidence, economics, prior commitments and campaign-level exceptions. Each action names evidence, expected outcome, producing/owning skill, dependencies, authority class and verification method. Mark Lead-authorised actions `approved` now; leave consequential actions `waiting_approval`.
5. **Resolved decision pack** — build the executive review, conversion one-pager, specialist findings and atomic implementation checklist. Put approved routine work in the main checklist and consequential work under `Michael approval required`.
6. **Verified delivery and BasicOps handoff** — Hermes dispatches one bounded delivery request to the configured ChatGPT/Codex worker. That worker saves and reads back all four files in the canonical Drive destination, then creates or updates one BasicOps parent through `lhm-project-hub:basicops-task-manager`. Keep only the governed metadata line and useful URLs in the description. Put key metrics, campaign bid verdicts, the resolved top five, matched-zone optional checklist, authority classes and any exact consequential decision in the discussion. Return every observed URL; do not create execution subtasks merely from report delivery.
7. **Authority gate** — the Lead automatically approves routine reversible account-management actions. Consequential budget, pause, conversion-definition, major-targeting, commercial-strategy and subjective-brand decisions wait for Michael through Hermes. Ask only for the exact consequential decision; do not impose a blanket stop on independent Lead work.
8. **Sequential dispatch** — the Google Ads Lead dispatches exactly one dependency-ready approved action using the departmental action packet. Do not start the next action until the worker has returned evidence, Google Ads Delivery QA has passed it, and the Lead has recorded the outcome. Every live mutation observes the owning skill's approval gate.
9. **Completion loop** — after each QA-passed action, update the canonical Obsidian service file and BasicOps parent/action before selecting the next. When all actions are terminal, return the completion dossier to Head of Production for acceptance and then send the accepted evidence to Learning Steward. Chief of Staff is not a routine completion stop.

## Delivery ownership and completion gate

Hermes owns orchestration, not the external mutations. When Hermes lacks Drive or BasicOps tools, it must use the configured ChatGPT/Codex delivery bridge automatically; never ask Michael to paste a prepared payload or decide whether the report should be saved.

The delivery request contains the client, run month, four-file review pack, canonical Drive destination, stable BasicOps dedupe key, overview and resolved actions. The worker must use the installed Google Drive skills and `lhm-project-hub:basicops-task-manager`, then read every file and the task back.

Only use `status: waiting_michael_hermes` after all required artefact URLs and `basicops.task_url` are observed and verified and no dependency-ready Lead action exists. When the register contains both consequential waiting actions and a dependency-ready Lead action, use `dispatch_ready`, keep each consequential action at `waiting_approval`, and expose its exact decision in BasicOps without blocking the Lead queue. Before delivery verification, use `status: needs_review`, `waiting_on: delivery_worker`, and describe the exact failed or pending stage. Say **analysis complete; delivery incomplete**, never **review complete**. Preserve the delivery run ID so a later Hermes message resumes it instead of submitting a duplicate.

## BasicOps workflow state

Use the exact governed metadata format in `lhm-project-hub:basicops-task-manager`, followed only by useful URLs. For the normal morning handoff, its orchestration fields are:

`handoff_trigger=waiting; next_handoff=Michael via Hermes; handoff_channel=basicops; orchestration_owner=hermes; workflow_state=waiting-on-michael-via-hermes; approval_status=pending-michael`

The remaining required metadata fields keep their governed values for recurring Google Ads delivery. Do not introduce a second pipe-delimited metadata schema.

The human Discussion carries the stable run month, action IDs and resume instruction. Internal structured-handback statuses may use snake case, but map them to BasicOps metadata as follows:

- `waiting_michael_hermes` -> `workflow_state=waiting-on-michael-via-hermes`
- `dispatch_ready` -> `workflow_state=approved`
- `specialist_running` -> `workflow_state=executing`; active subtask `workflow_state=waiting-on-agent`
- `waiting_approval` -> `workflow_state=ready-for-review`
- `waiting_manual_execution` -> `workflow_state=waiting-on-michael`
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
  status: waiting_michael_hermes | dispatch_ready | specialist_running | waiting_approval | waiting_manual_execution | needs_review | complete
  waiting_on: michael_via_hermes | michael_executor | hermes | specialist | delivery_worker | none
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
  artefacts:
    monthly_review_url: "verified URL or null"
    conversion_tracking_url: "verified URL or null"
    specialist_findings_url: "verified URL or null"
    implementation_checklist_url: "verified URL or null"
    additional_execution_files: []
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
      authority: lead | michael
      mutation_scope: read_only | prepare_only | manual_execution | consequential_approval
      decision: pending | approved | modified | rejected | deferred
      execution_status: not_started | running | waiting_approval | waiting_manual_execution | complete | blocked
  next_prompt: "The concise question Hermes should ask Michael"
  mutations_performed: none
```

After an action completes, return its before/after values, tool evidence, Drive artefact if applicable, mutations performed, and verification result. Never mark an action complete from an instruction alone.

The action handback is not accepted until `google-ads-delivery-qa` returns `pass`. A prepared implementation file may pass artefact QA while execution remains `waiting_approval` or `waiting_on_michael`; only observed live readback or explicit manual confirmation plus the defined verification closes the action.
