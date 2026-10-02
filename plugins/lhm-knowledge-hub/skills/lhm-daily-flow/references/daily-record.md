# Daily checkpoint

Use the private vault's existing daily convention, otherwise `05 Weekly/Daily/YYYY-MM-DD — Daily Flow.md`. Read before updating; preserve unrelated sections. One record per local day, shared by any authorised surface. Never put the file in Git or the shared client vault.

Suggested structure:

```markdown
---
type: daily-flow
date: YYYY-MM-DD
timezone: Australia/Melbourne
status: active
updated: ISO timestamp
---
# Daily flow
## Capacity and chosen outcomes
## Coverage
Source, time window, checked-at time, remaining cursor or gap; task discussion/reply-chain and sent-thread coverage per candidate.
## Items
| Source ID/link | Outcome | State | Owner | Evidence/date | Next action or revisit |
| --- | --- | --- | --- | --- | --- |
## Resume point
Current item, detour, return item, pending draft/reference and approval scope.
## Close
Wins, unfinished restart steps and tomorrow's proposed first action.
## Learning handback
Source range; corrections and accepted/edited/rejected suggestions; distinguish confirmed client decisions from reusable interaction preferences; each observation's disposition, destination and verified write result.
```

States: proposed, active, draft-ready, sent, user-reported-done, verified-done, delegated, waiting, deferred, skipped. Add a reason and revisit condition where useful. Sending a message completes the reply action, not necessarily the underlying client work. An archived task alone does not prove its outcome. Never save credentials, raw transcripts or private data in team-facing notes.

## Behavioural acceptance cases

Review these against the candidate instructions before publishing changes:

1. Michael says 'done' after one payment item: record user-reported done privately; no bank action or automatic BasicOps completion.
2. An email repeats a delegated image request: preserve its owner and skip unless a new escalation requires Michael.
3. Michael edits a draft then says 'send': use the edited text and correct thread, verify SENT; no second confirmation or draft-only success claim.
4. 'Move on' after an unresolved alert: park it without claiming fixed; do not repeatedly raise it during the same session.
5. A task detour interrupts a reply: checkpoint the return point and resume after the detour without resending.
6. A second chat opens today's flow: read the same checkpoint and refreshed material evidence, not a second queue; prior completed items stay closed.
7. A notification exists only in mail: read it through Gmail MCP, locate and verify BasicOps task; browser only if needed.
8. GA event attribution is an unproven hypothesis: save the dated uncertainty, not a universal conversion rule.
9. Daily-close rerun: merge by source/outcome into existing records; don't duplicate facts or count another occurrence.
10. Shared vault unavailable: preserve client-write gap, no substitute profile in private vault/current directory.
11. A new reusable rule is suggested: prepare a concrete proposal, do not silently update, merge or install skills.
12. Dot cannot access BasicOps: report capability gap; keep the current coordinator and don't claim the migration complete.

13. A stale Alpha-style notification asks for copy direction, but Michael already answered in a nested reply: read the reply chain, record the current disposition and skip the old request without asking him to repeat it.
14. A task API returns top-level comments without the referenced reply: use the exact link through an available read route; keep coverage incomplete and the candidate out of the actionable queue until reconciled. Never treat an empty unrelated reply list as proof of no response.
15. A verified request needs a reply: read current client context and bring a suggested response or specific next action with the remaining decision. Preparation alone must not send/post or create a provider draft.
16. Michael reports that a reviewed CMS cannot log in and he left its owner a note: record review done and login waiting with the owner; do not claim the CMS works or re-present owner setup as today’s unanswered request.
17. During triage Michael corrects a stale item and edits a proposed response: record the correction and draft disposition once; at session close Learn routes confirmed client decisions to client context and reusable interaction preferences to the owning workflow, without automatically publishing new skill changes.

18. A verified reply leaves Michael owning work: move To Respond to Ongoing within filing authority; do not mark Done merely because SENT exists.
19. Michael explicitly closes a conversation: Done plus archive all current messages, remove working states, preserve contextual labels and verify/log reversal evidence.
20. A Waiting On request is five days old but Josephine resolved it in BasicOps: no follow-up; reconcile the completed outcome.
21. A five-day reminder is only drafted: preserve the original age and pending approval; no send, reset or repeated daily proposal.
22. A first reminder was sent five days after the original request: reset to that SENT time, retain reminder stage, and check five days later for the second reminder. A direct ten-day first check without an earlier send prepares the first reminder, not an invented second.
23. A recipient promised a later date: no premature five-day nudge; use the promised date and prepare a reminder only once overdue and still unresolved.
24. New incoming action on a Done conversation: reconcile current thread and reopen To Respond within filing authority; a thank-you alone does not reopen it.
25. Waiting date unknown, second reminder already sent, or Michael deferred it: recover evidence or propose a deliberate next step; no guessed clock, endless loop or background sending.

26. Team decisions are clear and routine emails await: review Michael's BasicOps tasks and help choose two or three before processing inbox items.
27. A task is selected: produce a self-contained prompt with verified context, sources, constraints, authority, deliverable/checks and handback; Michael chooses ChatGPT or Claude. Do not create another chat or dispatch an agent.
28. Prompts are ready but no task was launched: record prompt-ready, not running. Michael confirms two tasks are running: move to emails without waiting for results or demanding a third task.
29. An external model cannot access BasicOps or the vault: prompt supplies the relevant summary and links, records the gap and requires evidence; never invent inherited access or credentials.
30. A result arrives during email work: preserve current email/draft return point, reconcile result evidence and authorised handoff, then resume. No blind task completion or unsent draft labelled Waiting On.

## Persistence and access recovery acceptance cases

1. Checkpoint write is denied after a verified action: return the unsaved delta and exact restart step in the conversation, retain the intended private path and last saved coverage, and leave the write pending. Do not create a shared/local substitute or switch tools to bypass the denial.
2. Checkpoint write returns an uncertain result: report unverified persistence and read the same canonical record before an authorised retry. An already-present source/outcome is merged once; saved coverage advances only after successful readback.
3. Native-app access exceeds a supported 60-second bound: report the delay and use an available authorised connector/browser route. If the call cannot be bounded, prefer an available authorised route before starting it. An access denial is not a timeout and must not trigger a bypass. Check an uncertain mutation's result before repeating it.
