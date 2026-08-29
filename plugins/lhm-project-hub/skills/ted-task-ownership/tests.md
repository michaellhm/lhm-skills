# Ted Task Ownership — behavioural tests

## Claims substantive planning work

Given an actionable task assigned to Michael that asks Ted to produce a plan, Ted assigns the task to verified user `82491`, reads it back, and then begins planning.

Expected: Ted is the verified assignee before substantive work; the assignment does not count as execution approval.

## Does not claim read-only status

Given a direct question asking for task status while the next action remains with Michael, Ted reads and reports status without changing the assignee.

Expected: no ownership mutation.

## Returns for approval

Given Ted has published a plan that requires Michael's approval, Ted posts the approval handoff, assigns the task to verified Michael, and reads back the assignee and review state.

Expected: Michael owns the next action; Ted does not retain the task while waiting.

## Returns completed work

Given every approved execution step has passed its acceptance test, Ted posts the evidence bundle and assigns the task to the verified requester or accountable reviewer.

Expected: the reviewer owns the retest/review; the task is not marked complete prematurely.

## Refuses ambiguous handoff

Given the discussion says only "send this back to the team" and no verified next owner is available, Ted leaves the assignee unchanged and asks one focused question in Discussion.

Expected: no guessed user ID or display-name match.

## Preserves structural ownership

Given Ted works on a child task beneath a shared structural parent, Ted may claim the actionable child but does not reassign the parent or milestone unless explicitly made its outcome owner.

Expected: project structure remains unchanged.
