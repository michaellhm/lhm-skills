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
Source, time window, checked-at time, remaining cursor or gap.
## Items
| Source ID/link | Outcome | State | Owner | Evidence/date | Next action or revisit |
| --- | --- | --- | --- | --- | --- |
## Resume point
Current item, detour, return item, pending draft/reference and approval scope.
## Close
Wins, unfinished restart steps and tomorrow's proposed first action.
## Learning handback
Source range; each observation's disposition, destination and verified write result.
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
