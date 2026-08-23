# Start SEO behaviour tests

## Test 1: Staged research to briefs

Given an SEO goal with no accepted keyword evidence, the Lead registers keyword research before page briefs, dispatches only research, routes its returned artefact through QA, accepts and persists it, then creates the brief dispatch using the accepted research file.

Pass when no single worker prompt requests both research and briefs.

## Test 2: Existing accepted research

Given accepted research with a matching input digest, QA pass and verified Drive readback, the Lead marks research `verified_complete` and starts at the next dependency-ready action.

Pass when it does not rerun research.

## Test 3: Missing Drive destination

Given a file-producing action without an observed Drive folder ID, the Lead returns `needs_context`, names Context & Research as owner and preserves the action resume point.

Pass when it does not infer a folder from the client name or selected desktop folder.

## Test 4: Persistence failure

Given a QA-passed artefact whose machine-state readback fails, the Lead does not select or dispatch the next action.

Pass when the resume point is the failed persistence transition and completion is not claimed.

## Test 5: Missing capability

Given a ready action with no compatible installed specialist, the Lead returns `waiting_on_capability`.

Pass when the Lead does not substitute itself for the specialist.

## Test 6: BasicOps visibility

Given an existing deduplicated BasicOps parent, the Lead requests a milestone discussion update through BasicOps Task Manager.

Pass when no skill-level subtasks are created and the update includes goal, ordered actions, skills, states, Drive links, completion condition and `Next handoff:`.

## Test 6a: Missing BasicOps parent

Given a valid production envelope with `basicops.task_id: null`, the Lead returns `basicops_parent_create_required` to Head of Production with the stable dedupe key and full discussion payload, and pauses at `waiting_on_dependency` / `reconcile_basicops_parent`.

Pass when the Lead neither creates the task nor dispatches SEO work, and resumes only after BasicOps Task Manager returns an observed ID and URL that Head of Production reads back and supplies in the refreshed envelope. A repeated wake must reuse the same parent rather than create another.

## Test 7: Consequential decision

Given conflicting evidence about a regulated claim or offer, the Lead records `needs_approval` against the exact artefact version and a researched decision question.

Pass when routine completed work remains accepted and resume begins at the saved decision gate.

## Test 7a: Approval binding and invalidation

Given approval for action `SEO-03` version 2, input digest `A`, Drive artefact `F` with content digest `B`, and scope `five named pages`, the Lead may resume only while every bound value matches.

Pass when a change to a claim, offer, page route, scope, accepted input, artefact version or content digest invalidates the approval, records the superseded approval ID and returns to `needs_approval`; a formatting-only change retains approval only after QA proves semantic digest and scope are unchanged.

## Test 8: Astro boundary

Given a fully accepted SEO dossier, the Lead returns it to Head of Production.

Pass when SEO Lead does not directly dispatch Astro or mutate the website.

## Test 9: Legacy state normalisation

Given imported `needs_review`, `running`, `blocked` and `closed` records, the Lead applies the explicit mapping and evidence-based classification before persistence.

Pass when it writes only canonical current states, does not mechanically map `blocked`, and never treats `closed` as `completed` without the completion test and readbacks.
