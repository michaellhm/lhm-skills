---
name: run-hermes-task
description: Run substantive LHM client or internal work through the governed Hermes workforce from source intake to durable delivery, independent QA and human review. Use when Michael or an LHM team member asks Claude, Codex or another desktop agent to "run this through Hermes", execute a BasicOps task through Hermes, test the Hermes employee chain, supervise delegated AI work, or recover a Hermes-run task that stalls. Routes capability failures to the Hermes CTO with a persisted return point and resumes automatically after verified repair.
---

# Run Hermes Task

Act as the desktop control client for Hermes. Enter the existing governed workforce; do not
recreate its employee roles locally or do the specialist work merely because dispatch is awkward.

## Establish the contract

1. Authenticate the requester and read the complete source task, its Discussion, canonical client
   record and relevant project state.
2. Record one parent outcome with: source ID and URL, objective, deliverables, authoritative
   destination, completion condition, permission ceiling, accountable reviewer and next handoff.
3. Resolve unknown folders, repositories and evidence through Context & Research. Do not guess IDs,
   paths or client facts.
4. Treat these as separate permissions: internal research, production, Drive/file mutation,
   BasicOps mutation, deployment/publishing, client contact, credentials and commercial decisions.
5. If the user says to run or execute an existing task, ordinary internal production, durable Drive
   delivery and a BasicOps review request are authorised unless the source task narrows them.
   Deployment, publishing and outbound contact still require explicit authority.

## Preflight Hermes

Before dispatch, verify the configured Hermes host/profile, container or service health, registered
role routes, writable checkpoint storage, provider admission and required repository/tool access.
Use bounded read-only checks. Never use a large model turn as a health probe.

Classify a launch as accepted only after obtaining a run ID plus one authoritative sign of life:
active process state, growing log, accepted queue state or role checkpoint. A request ID alone,
successful shell return or armed monitor is not acceptance.

## Dispatch and supervise

1. Dispatch the parent to `lhm-chief-of-staff` with the full contract and return point.
2. Require the governed route:
   `Chief of Staff → Context & Research → Head of Production → specialist worker → independent QA`.
   Skip a role only when its work is genuinely unnecessary and record why.
3. Preserve the parent ID through every child. Record child run IDs, dependencies, artefact paths,
   idempotency keys and status evidence.
4. Check health after launch before starting a long monitor. A zero-byte log with no live process,
   terminal queue state, admission error or missing checkpoint is an immediate failure, not a wait.
5. Use one bounded connection per check where practical. Reuse an existing session and back off
   after transport throttling; never create a pile of SSH sessions to compensate for uncertainty.
6. Announce only genuine role transitions, material replans and waits longer than two minutes.

## Route capability failures to CTO

Treat provider/rate/billing admission failures, absent fallbacks, dead launchers, broken schedulers,
missing repositories, missing skills/MCP routes, authentication failures, SSH throttling, corrupt
checkpoints and inaccessible destinations as capability incidents.

On a capability incident:

1. Stop retries after one safe idempotent retry.
2. Persist the parent ID, incident ID, failed child, exact evidence, completed work, mutation state,
   first incomplete step, acceptance test, resume token and safe `next_wake_at`.
3. Use Hermes `work-control block` (or its current authoritative equivalent) to set
   `waiting_on_capability`.
4. Dispatch `lhm-cto` with the incident and required verification. Retain ownership in Chief of
   Staff/Head of Production; CTO owns capability restoration, not the business outcome.
5. Do not ask Michael to choose a worker, retry a process, wire a fallback, locate a repository or
   watch a run. Ask only when repair needs new billing authority, unavailable credentials, security
   approval or another consequential choice. Present the researched smallest decision.
6. Accept repair only from a matching, idempotent `capability_restored` event with verification
   evidence. Record it as consumed, restore the saved checkpoint, and automatically resume the
   original parent from the first incomplete step.
7. If durable continuation itself is broken, CTO must repair continuation before the outcome can
   be resumed. Never substitute the current chat window for the checkpoint.

Do not claim that a billing limit makes all work impossible until deterministic non-model steps,
existing artefacts and authorised alternative routes have been assessed. Do not silently change
providers or spend limits.

## Verify and deliver

1. Require independent QA against the source acceptance test. A worker's self-report is evidence,
   not verification.
2. Treat Hermes workspaces, container paths, logs and Kanban attachments as staging only.
3. Resolve the existing authoritative client destination, normally the client's Google Drive
   project folder. Upload the approved package and verify each expected file by destination listing
   or metadata/readback. Preserve source files and existing organisation.
4. Record durable folder/file URLs, QA result, remaining exceptions and hashes or revision evidence
   when useful.
5. Route the BasicOps write through `basicops-task-manager`. Put actionable handoff context and
   artefact links in Discussion; keep Description to governed metadata and useful working URLs.
6. Use BasicOps' native review request. Leave every human-owned task open in `Under Review`, assign
   the accountable human reviewer, set `handoff_trigger=ready-for-review`,
   `workflow_state=ready-for-review` and `approval_status=pending-<reviewer>` as applicable.
7. Never mark a human-owned BasicOps task `Complete` unless the authenticated accountable human
   explicitly requests that exact mutation after reviewing the outcome.
8. Read back the task status, reviewer, board/list, assignee, metadata, Discussion and URLs.

## Hand back

Return one concise receipt containing:

- outcome and current state;
- source and parent IDs;
- worker/role chain and run IDs;
- durable artefact folder and key file links;
- QA and readback evidence;
- BasicOps review link and reviewer;
- exceptions or approvals still required;
- exact next handoff;
- CTO incident, repair and automatic-resume evidence when recovery occurred.

Call the outcome complete only when the source acceptance condition, durable delivery and review
request are all verified. Describe work awaiting human inspection as `ready for review`, not
completed.

