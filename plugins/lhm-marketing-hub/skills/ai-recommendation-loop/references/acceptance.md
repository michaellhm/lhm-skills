# Behavioural acceptance scenarios

Use these scenarios to review the skill and any future collector/scorecard implementation. They are acceptance criteria, not simulated live results.

1. No engine access: save a buyer panel and collection table, return `waiting_on_capability`; no invented recommendation baseline.
2. Branded verification names the client, discovery answers omit it: branded mention rate rises; discovery mention rate remains zero. No blended discovery win.
3. Expected three runs, two captured and one failed: denominator two, coverage 2/3 and incomplete flag; no negative third result.
4. A cited client URL with no recommendation: citation rate increases; recommendation rate remains zero.
5. An unordered list mentions the client: mention counted; no invented numerical position.
6. A recommended client has an incorrect location: recommendation counted, accurate recommendation excluded, misdescription recorded with evidence.
7. Same source cited repeatedly in one answer: every URL retained; domain frequency increases by one run.
8. A new model or API replaces consumer UI: start a new series; no unqualified month-over-month delta.
9. Winning question proposed for retirement: retain it in the fixed panel; additions are exploratory or a new version.
10. Staging deployment fails after push: state pushed/failed, no ready review email. Preserve exact candidate and recovery point.
11. Staging verified, email denied/unavailable: save the exact email, report `notification_pending`, preserve verified staging result.
12. Retry after successful email/task: reuse sent ID and equivalent open task, no duplicate notification or task.
13. Reviewer task completed without release approval: remain review_pending/needs_approval; no production merge.
14. Staging changes exist but production is unchanged: do not attribute AI visibility change to those staging changes.
15. Search bot allowed but training bot blocked: no automatic training permission change; record independent policies.
16. Destination/client identity unresolved: block dependent writes and preserve draft; never write another client's records.
17. Existing authorised scope includes staging/email/task: finish those actions without repeated confirmation; production still requires its own authority.
18. Schedule suggested but activation not requested: recommend cadence, do not activate recurring work. An authorised schedule resumes from durable state and reports collection capability honestly.
19. Competitor mention set changes or panel coverage differs: compute only a labelled comparable subset or mark the delta unavailable.
20. A client is outside healthcare: apply that client's industry requirements and website platform; no inherited LHM slugs, prices, email address or regulated claims.
