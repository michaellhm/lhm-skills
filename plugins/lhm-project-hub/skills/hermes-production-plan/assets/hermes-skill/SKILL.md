---
name: lhm-project-manager-dispatch
description: Identify the matching LHM Obsidian SOP from a natural-language BasicOps outcome, prepare its concise execution plan, and dispatch bounded project-management or production orchestration through the approved Project Hub worker.
---

# LHM Project Manager Dispatch

## Project Hub worker

Use:

`/opt/data/profiles/lhm_brain/bin/claude-dispatch submit-specialist-readonly project SUBJECT_TYPE SUBJECT_NAME OBJECTIVE`

Allowed subject types are `client`, `opportunity`, `internal`, and `general`.

The objective must name the exact Project Hub workflow required, such as client onboarding, sales handover, website kickoff, monthly review, client update, team work brief, project-manager review or `lhm-project-hub:hermes-production-plan`. Include the parent/project ID, canonical Obsidian records, known BasicOps/Drive links, current phase, permission ceiling and acceptance test.

Resolve the run with `claude-dispatch status RUN_ID`, then `claude-dispatch result RUN_ID`. The worker route is review-only: output is a proposed operational package, not an authorised BasicOps, Drive, email or client mutation.

For an existing WordPress or LeadScale landing-page implementation whose registered platform is WordPress REST, assign the production child to `@lhm_website` and have that profile invoke:

`/opt/data/profiles/lhm_brain/bin/claude-dispatch submit-specialist-readonly wordpress-rest client CLIENT_SLUG OBJECTIVE`

This routes Claude Code CLI to `lhm-wordpress-hub:wordpress-lead` with `lhm-wordpress-hub:wp-rest-operator` as the required skill. Do not route it to the Astro worker, Google Ads worker or generic project profile. The returned package remains review-only until a separately registered WordPress REST destination profile and exact mutation authority are present.

## Natural-language SOP discovery and planning

When an existing BasicOps task asks for production work:

1. Read the complete task, including Discussion, links, parent, subtasks, intended outcome and completion condition.
2. Classify the work from the requested outcome. Ask the LHM Brain or Project Hub worker to search `70 SOPs/AI Operations/`, match primarily against each SOP's **Use this when** section and read the closest matching SOP. Do not require the requester to name a bot, skill or SOP.
3. Invoke `lhm-project-hub:hermes-production-plan` through the Project Hub worker. Require it to cite the selected SOP and convert the detailed procedure into a short task-specific plan with the intended outcome, ordered roles/actions, artefacts, dependencies, completion condition, approval boundary and next handoff.
4. Post the plan through the governed BasicOps mutation route so the team can see and override it. The SOP remains canonical; the plan is its task-specific execution view.
5. If the BasicOps task clearly requests the outcome, treat it as authority for ordinary in-scope production and hand the versioned plan to `@lhm_chief_of_staff` without adding a second Michael approval gate. Chief of Staff owns execution and returns the result to Project Manager for reconciliation.

Pause only when the task is genuinely ambiguous, the SOP identifies an unresolved exception, or the plan includes a separately governed consequential action such as publishing, deployment, sending, spend, live-account mutation, scope expansion or an explicit approval-bound decision. An authorised override received before the affected step begins updates the plan; materially changed plans receive a new version.

If no SOP matches, say `SOP: none found` and use the existing governed Project Hub route. Do not invent a new agency procedure or block otherwise authorised routine work merely because the SOP library is incomplete.

Example: “Create a Dry Needling service page” matches `70 SOPs/AI Operations/Create Website Page Copy.md`. The plan uses SEO keyword research to determine the slug, then page brief, Markdown page copy, verified delivery to the client's Google Drive `Content` folder and BasicOps handback. It does not add Astro, WordPress, staging or publishing unless the task separately requests implementation and another approved SOP or governed route covers that stage.

## Multi-stage route

For a rough outcome spanning two or more roles or systems, first use the SOP-discovery and planning flow above. Preserve one parent ID and the selected SOP reference across all stages. Hand the executable dependency plan to `@lhm_chief_of_staff`; do not create routine AI-worker subtasks in BasicOps.

When no approved SOP covers the outcome, or the selected SOP explicitly requires the generic multi-stage brief, use:

`/opt/data/profiles/lhm_brain/bin/claude-dispatch submit-specialist-readonly project-multi-stage SUBJECT_TYPE SUBJECT_NAME OBJECTIVE`

The objective must request `lhm-project-hub:multi-stage-delivery-brief` and include the intended outcome, completion condition, known evidence, permission ceiling, final reviewer and parent ID or deduplication key. Preserve consequential approval gates even when the source task authorises ordinary production.

## Connector handoff

When an exact mutation is authorised and matches a registered workflow, hand the bounded operation to `@lhm_operations_connector`. Include workflow ID, required skill, capability ID, exact target IDs, before state, intended after state, authority or approval evidence and read-back completion test.

### Google Drive target preflight

Before issuing any handoff that creates, copies, moves or uploads a file in Google Drive:

1. Resolve the destination through an authenticated Drive lookup; do not rely on a typed, quoted or reconstructed folder ID.
2. Read the folder metadata and successfully list its children using the exact returned ID.
3. Confirm the item is a folder, is not trashed and the connector can list it. Record the canonical folder URL and exact case-sensitive ID in the handoff.
4. If lookup or listing fails, treat the destination as an unresolved dependency. Do not dispatch the mutation or report it as resumed. Ask for the missing access or authoritative folder only after searching the available Drive context.

The connector receipt must repeat the resolved folder title, canonical URL and read-back result. A plausible-looking link or HTTP 404 is not validation.

Never pass broad project judgment to the connector, invent a target or owner, bypass authentication, or call an unregistered mutation route. Return a missing capability to `@lhm_cto` while preserving the project return point.
