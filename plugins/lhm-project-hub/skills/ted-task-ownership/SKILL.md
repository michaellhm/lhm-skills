---
name: ted-task-ownership
description: Keep the visible BasicOps assignee aligned with Ted's active ownership and verified human handoffs. Use on every Ted task event that begins work, pauses for another owner, or completes.
---

# Ted Task Ownership

Keep the BasicOps assignee aligned with who owns the next action. Ted's verified BasicOps user ID is `82491`.

## Claim active work

When Ted begins substantive work on an actionable task, call `update_task` and assign the task to user `82491` before deeper planning, orchestration or execution. Claim it when Ted is producing or revising a plan, coordinating an approved workflow, resolving an internal blocker, or reconciling delivery evidence.

Do not claim a task for a read-only status request, casual question, notification with no action for Ted, or a task whose next action remains explicitly owned by someone else. Do not take ownership of a structural parent or milestone merely because Ted is working on one child unless Ted is explicitly the parent outcome owner.

Read the task back after assignment. Continue only when the assignee is Ted. If the write or read-back fails, report the exact ownership failure in the task discussion and do not imply that Ted owns the task.

## Return ownership at every handoff

When Ted's active step finishes or another person owns the next action, assign the same task to that verified next owner in the same turn. This includes:

- clarification or authoritative input needed from a human;
- plan approval or review requested from a human;
- completed delivery returned to its requester or accountable reviewer;
- a correction, access request or decision assigned to a named teammate;
- any explicit handoff in the approved plan or current task discussion.

Use the verified BasicOps user record or governed AI-user registry ID. Never infer an assignee from display-name similarity, free text or an unverified email. If the next owner is missing or ambiguous, leave the current assignee unchanged, state the gap in Discussion and ask one focused question.

Update the Discussion with the outcome, next action and `Next handoff:` block before or alongside the reassignment. Read the task back and verify the intended assignee, section, status and Discussion message.

## State alignment

Assignment indicates next-action ownership; it does not grant approval or broaden authority.

- Active Ted work: Ted assigned; use the workflow's active status/section.
- Waiting on a human decision or retest: verified human assigned; use the applicable review/retest state.
- Delegated specialist execution: retain Ted only when he remains accountable for coordination; otherwise assign the verified handoff owner required by the governed workflow.
- Complete: assign the requester or accountable reviewer when a review is still required. Mark complete only when the task's completion condition is actually verified.

Never change an assignee merely to make a dashboard look tidy. Every assignment change must correspond to a real next-action handoff visible in the task Discussion.
