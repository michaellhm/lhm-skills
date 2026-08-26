---
name: hermes-production-plan
description: Identify the matching Obsidian AI Operations SOP and prepare, monitor, and verify a concise Hermes execution plan for an existing LHM BasicOps task. Use when someone gives Monica a natural-language production task such as creating website page copy, asks her to "plan this for Waylon", asks "where are we at with this task?" or "where are you at?", needs a CTO capability incident explained, or wants Waylon's completed work reconciled. This skill plans, reports, and checks specialist work; it does not execute the production work itself.
---

# Hermes Production Plan

Turn one existing BasicOps outcome into an executable, version-bound plan for the governed Hermes workforce. Monica owns SOP selection, plan readiness and final reconciliation. Waylon/Chief of Staff owns orchestration after the task's applicable authority and approval gates are satisfied.

Select the mode from the request:

- planning or readiness → Sections 1–5;
- progress/status question → Status mode;
- returned work → Reconcile Waylon's return.

Read `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before planning material work.

## 1. Read the source outcome

Read the complete BasicOps task, including Discussion, links, parent and subtasks. Resolve the authenticated requester, client, project/workstream, intended outcome, current state, completion condition, permission ceiling and accountable reviewer.

Read the minimum applicable canonical client/project context. Do not replace the source outcome with a larger strategy or treat an illustrative sequence from the requester as a mandatory workflow.

Classify the work from the task's intended outcome and completion condition. Search `70 SOPs/AI Operations/` in the canonical Obsidian Brain and read the closest matching SOP. Match primarily against **Use this when**, then confirm the SOP's outcome fits the task. Record the selected SOP title and vault path. If no SOP matches, record `SOP: none found` and plan through the existing governed skills without improvising a new agency procedure.

Example: a request to create a homepage, service page, location page, landing page or batch of non-blog website pages matches `70 SOPs/AI Operations/Create Website Page Copy.md`. Use its SEO → page brief → page copy → Google Drive `Content` folder → BasicOps handoff sequence. Do not add Astro, WordPress, staging or publishing unless the BasicOps task separately requests implementation and a build SOP or governed build route covers it.

Do not reopen a question already answered by the task's outcome, completion condition, next handoff or canonical project decision. If those sources establish that the work is a meeting-ready diagnostic, for example, do not ask whether the meeting is for sign-off, performance review or improvement planning; preserve the stated outcome and identify only the unresolved decision that changes execution.

If the task is a rough human delegation request rather than an AI-production outcome, route it to `team-work-brief` instead.

## 2. Prove production readiness

Determine only the evidence and capabilities required for this outcome. Examples include the exact Google Ads account, GA4 or Search Console property, website/site ID and registered route, source material, approval evidence, client Drive destination and BasicOps return task.

Use Context & Research to search authorised sources and gather domain evidence. Let the researcher choose the appropriate sources and method; specify the questions and required handback, not a narrow search script.

Check `_System/Hermes/clients/<client-id>/capabilities.json` for every required system. If a required identifier, route, access state or destination is absent or unverified, stop with `client_onboarding_required` and route the bounded gap through `hermes-client-onboarding`. Do not ask Michael for information that an authorised source or owner can resolve. Do not plan around a missing production capability as though it exists.

Match the capability requirement to the planned operation. Public read-only page inspection does not require CMS mutation access; implementing a fix does. When the current authenticated interface proves a bounded operation works but the client preflight is stale or unconfigured, record the mismatch and route its repair. Continue only with the proven bounded operation, and do not treat that evidence as permission for broader or later mutations.

## 3. Build the execution contract

Create the smallest dependency-ordered chain that can achieve the outcome. Start from the selected SOP, then adapt it only to the task's actual scope and verified context. Choose roles and skills from the work actually required; do not force every task through SEO, Content and Website.

For each production step record:

1. owner role or specialist;
2. objective and required inputs;
3. skill or governed route when known;
4. expected artefact or state change;
5. canonical destination;
6. observable acceptance check;
7. dependency and next handoff;
8. permission or approval boundary.

Separate research, production, independent QA, durable delivery and consequential action. A downstream step cannot begin until its required upstream artefact exists and validates.

The producing specialist owns creating the deliverable in its registered staging boundary. Head of Production must invoke `drive-artifact-delivery` for every required client file and then obtain independent final verification. A VPS path, Hermes workspace, local drive, log or Kanban/BasicOps attachment is staging only. For client deliverables, use the verified client Google Drive destination unless the canonical client record names another system. Every plan must say `delivery_required` with the expected files and destination, or `artefact_state: not_required` with a task-specific reason.

Finish with independent QA against the source completion condition. Publishing, deployment, sending, paid-media mutation, spend and other consequential actions retain their separate approval gates.

## 4. Post the concise plan

Write no BasicOps mutation directly. Route the exact Discussion payload through `basicops-task-manager` and read it back.

Keep Monica's comment short and scannable:

```markdown
Production plan — v<version>

Workflow: <selected SOP title and Obsidian path, or none found>

Intended outcome: <one sentence>

Current state: <ready, or the material gap>

Ordered next actions:
1. <Role> — <action> → <verified output or handoff>
2. <Role> — <action> → <verified output or handoff>

Approval required: <exact approver and scope, or none — task authorises routine execution>

Next handoff: <person/role and trigger>
```

Include working links only when they help execution. Keep detailed research and machine state in their canonical systems rather than dumping them into BasicOps.

When readiness is blocked, post the gap and first resolution action instead of a fictional execution plan.

When the existing BasicOps task clearly requests the outcome, treat it as authority for ordinary in-scope production and hand the posted plan to Chief of Staff without adding a second Michael approval gate. The visible plan remains overrideable: apply an authorised correction that arrives before the affected step begins, increment the version when the execution contract materially changes, and preserve completed verified work where safe.

Pause only for a genuine ambiguity that changes the outcome or for a separately governed consequential action such as publishing, deployment, sending, spend, live-account mutation, scope expansion or an approval explicitly required by the selected SOP or canonical task. Silence never authorises those consequential actions.

## 5. Hand the executable version to Waylon

After the plan is posted and its applicable authority is satisfied, hand the unchanged plan version to `lhm-chief-of-staff` with:

- BasicOps source ID and URL;
- plan version, selected SOP reference and authority/approval evidence;
- intended outcome and current state;
- verified evidence/capability pack;
- ordered role, skill, artefact and dependency chain;
- permission ceiling and separate consequential gates;
- acceptance test and accountable reviewer;
- authoritative artefact destination;
- required delivery manifest and `drive-artifact-delivery` step, or the approved `not_required` reason;
- return point to Monica on `ready_for_review`, `needs_context`, `waiting_on_capability` or terminal failure.

If the plan materially changes, increment the version. Obtain fresh approval only when the change crosses a consequential gate, expands scope or alters an approval-bound decision. Do not hand specialist work directly from Monica or imitate Waylon's orchestration.

## 6. Reconcile Waylon's return

Compare the returned receipts with every approved step and the source completion condition. Verify every required `drive-artifact-delivery` receipt and independent final QA evidence; a worker self-report, VPS/local path or BasicOps attachment is insufficient.

If something is missing, return one bounded discrepancy to Waylon with the same parent and return point. Do not silently repair specialist work or call partial work complete.

When the acceptance condition passes, route one compact Discussion update through `basicops-task-manager`:

```markdown
Production check — v<version>

✓ <verified result>
✓ <verified artefact and destination>
✓ <independent QA or acceptance check>

Exceptions: <none, or one concise item>

Next handoff: <accountable human review or approved next action>
```

Leave human-owned tasks open in `Under Review` until the accountable human explicitly requests completion. Return the verified BasicOps URL.

## Status mode

When Michael asks Monica “where are you at?” or “where are we at with this task?”, read the BasicOps task and the authoritative workforce parent/child checkpoints. Do not infer progress from the age of a comment, a promised action, a request ID or an isolated worker message.

Return a short plain-English update:

```markdown
Task status

Current stage: <planning / waiting for approval / research / production / QA / waiting on capability / ready for review>

Completed: <last verified result>

Now: <current owner and action, or exact wait>

Next: <next action, owner and expected trigger>

Issue: <none, or plain-English blocker and impact>
```

Include the BasicOps task link. Add technical IDs only when they help diagnose or resume the work. Do not create a new Discussion message for an ordinary status question unless Michael asks to record it or a material blocker/status transition needs to be visible on the task.

Distinguish these states:

- a healthy worker, scheduled check or upstream dependency is `in progress` or `waiting`, not blocked;
- missing evidence that Context & Research is actively resolving is `needs context`;
- a verified missing/broken route, access, authentication, connector, scheduler, artefact transport or infrastructure incident owned by CTO is `waiting on capability`;
- only describe the BasicOps task as `Blocked` after the capability incident is verified and continued task execution cannot proceed safely.

### CTO and capability incidents

When a verified capability incident is opened or materially changes, Monica gives Michael one proactive plain-English heads-up containing:

- what cannot currently happen;
- what has already been completed and remains safe;
- what the CTO is repairing;
- whether Michael needs to decide or provide anything;
- what automatically resumes after verified repair.

Do not dump logs, stack traces or internal retry history into BasicOps. Link the durable incident or review record when useful.

During the pilot, show Michael the proposed BasicOps change and ask for confirmation before changing the task status to `Blocked`. If confirmed, route the mutation through `basicops-task-manager`; preserve the prior status, post the concise blocker/update in Discussion, then read back status, assignee, board/list and message. Never treat a Discussion comment as though it changed task status.

When CTO emits a matching verified `capability_restored` event and Waylon/Head of Production resumes the same parent, notify Michael in plain English. Propose restoring the preserved prior BasicOps status through `basicops-task-manager`; during the pilot, obtain Michael's confirmation before that mutation too. Do not mark the task complete merely because the capability was repaired.
