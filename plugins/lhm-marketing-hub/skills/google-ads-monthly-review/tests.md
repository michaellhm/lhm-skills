# Google Ads monthly operating model tests

## 0. Canonical departmental entrypoint

Given `/lhm-marketing-hub:start-googleads Any Stage Physio — review the last 30 days`, invoke the
`google-ads` Lead and run `google-ads-monthly-review` before any downstream action skill. Return a
new zone-led action register; do not resume an earlier action register unless the request says to
resume.

## 1. Scheduled morning review

Given canonical Obsidian context and all connectors, the run must compare current/prior 30 days, verify prior commitments, save/read back Drive, create one BasicOps parent without execution subtasks, and return `waiting_michael_hermes`.

## 2. Missing canonical goals

Given absent CPA economics, the run must report the precise canonical gap. It must not create `goals.md`, `current-projects.md` or `client_profile.md` in the plugin or working directory.

## 3. Ads/GA4 anomaly

Given zero Ads conversions and GA4 conversions in the same campaign/window, the run must describe an attribution/import discrepancy, lower measurement confidence, and not turn the performance zone Red solely because of tracking.

## 4. AdPulse unavailable

The run must label its zone source `manual_fallback`, show the calculation and continue. It must not claim an AdPulse pull.

## 5. Approval boundary

Saving Drive and creating BasicOps must not approve consequential Ads mutations. After delivery,
the Lead may approve a routine reversible action from observed evidence, but no specialist action
starts merely because the report or task exists.

## 6. Resume through Hermes

Given Michael approves GA-02 and GA-04 later, Hermes must preserve those IDs, dispatch only one action, record its evidence in Obsidian and BasicOps, then dispatch the other. Rejected/deferred actions remain explicit.

## Delivery bridge acceptance

Given Hermes has neither a Drive nor BasicOps connector, a completed review must automatically dispatch the configured ChatGPT/Codex delivery worker. It must not ask Michael whether to save the report or offer a pasteable BasicOps payload. `waiting_michael_hermes` and “review complete” are invalid until the worker returns verified Drive and BasicOps URLs. A pending or failed worker returns `analysis complete; delivery incomplete` plus its resumable run ID.

## 7. Specialist approval gate

If an approved analysis action discovers a consequential live change, the worker must return `waiting_approval`; Hermes must update BasicOps and stop rather than infer permission.

## 8. Delivery failure

If Drive readback or BasicOps writing fails, return `needs_review` with the exact blocker and preserved report/handback. Never claim completion.

## 9. Target versus trend

Given 82.3% pacing, current CPA at 108.9% of the canonical weighted target, and an 18% worsening versus the prior period, the mechanical zone must remain Yellow because performance is still inside the matrix's Good threshold. Report the negative trend and an Orange operational caution separately; do not turn the trend into Red/Poor performance.

## 10. Prior-work reconciliation

Given an action that appears in a prior Drive report, BasicOps discussion and live settings, classify it as `verified_complete`, `complete_unverified`, `partially_complete`, `not_started`, `superseded` or `cannot_verify`. Do not present verified or superseded work as a new recommendation. Preserve recurring incomplete work as a delivery failure with its history and owner.

## 11. Bounded action and QA

Given Michael approves GA-02, dispatch only GA-02 with the departmental action packet and selected specialist skill. The result must pass `google-ads-delivery-qa` before the Lead records it or reveals GA-03. A QA correction returns to the same worker as one bounded correction.

## 12. Implementation pack

Given a negative-keyword action, return a quoted one-per-line TXT, evidence for the safest sufficient match scope and a collision check against converting or strategically valuable queries. Do not blindly convert every poor multi-word search term into single-word negatives.

## 13. Production and Steward closeout

When every approved action is terminal, return a completion dossier to Head of Production. Only after `accepted` send the Learning Steward intake. Do not route a normal accepted delivery to Chief of Staff. Do not label a proposed skill change `Applied` before its named regression passes.

## 14. Cross-department dependency

Given Ads requires an Astro landing-page tracking change, the Google Ads Lead returns an exact technical handoff and acceptance test. Head of Production owns formal routing; the Ads worker must not silently create or prioritise another department's workload.

## 15. Zone candidates map to skills, not automatic checklist work

Given a mechanically Yellow account with profitable PMax under pacing but a failing Search campaign,
retain Yellow as the account zone, label the Search campaign exception, and select up to five actions
from the zone library only where live evidence supports them. It is valid to select Orange repair
candidates for the failing campaign. Every selected action must name its owning skill, dependencies,
authority class and verification method. Do not select five Yellow scaling tasks merely to fill the
register.

## 16. Lead-authorised chaining starts automatically

Given the review selects a keyword-waste action owned by `keyword-optimizer` with `authority=lead`
and no dependencies, the Google Ads Lead marks it approved and dispatches it without asking Michael
whether to proceed. The worker runs only that action slice, Google Ads Delivery QA checks it, and the
result returns to the Lead before any next action starts.

## 17. Consequential action does not create a blanket stop

Given GA-01 is an independent Lead-authorised tracking diagnosis and GA-02 is a conversion-definition
change requiring Michael, dispatch GA-01 while GA-02 remains `waiting_approval`. Ask Michael only for
the exact GA-02 decision. Do not ask for permission to begin GA-01 and do not dispatch GA-02.

## 18. Manual execution versus decision authority

Given the Lead approves a routine reversible RSA or keyword change but no Ads write connector exists,
the Lead produces exact UI instructions and marks the action `manual_execution`. Michael is the human
executor, not the strategy approver. Close it only after his execution confirmation and the defined
live readback pass.

## 19. Mandatory campaign bid verdicts

Given three active campaigns including PMax, run `bid-budget-optimizer` read-only across all three
before selecting final actions. The campaign table must show each current bid strategy and exactly
one verdict: `keep`, `change`, or `insufficient_evidence`. Do not leave “confirm PMax scaling” as an
unresolved top-five item when the available evidence can support a verdict.

## 20. Conversion findings in the combined review

Given Ads-hosted and GA4 conversion actions, include a conversion section in `google-ads-monthly-review-YYYY-MM.md` with current
and recommended primary/secondary state, account-default inclusion, per-campaign goal usage, GA4
firing evidence and Ads import state. If an Ads-hosted action cannot be demoted or deleted, recommend
the exact campaign-goal exclusion rather than the impossible account-level mutation.

## 21. Active Search keyword diagnostic

Given any active Search campaign, run `keyword-optimizer` before finalising the five, even when the
first pass does not reveal obvious waste. Return exact pause/retain/add decisions, an explicit keep
finding or a bounded evidence blocker. Produce the Editor CSV and negative TXT only when evidence
supports changes; do not invent work to force those files.

## 22. Consolidated pack and BasicOps presentation

A completed monthly review must save and verify one `google-ads-monthly-review-YYYY-MM.md` containing
the executive review, conversion, bid/budget, keyword and PMax findings, other triggered evidence,
the implementation checklist and a separate consequential-approval section. The BasicOps discussion
must repeat key metrics, the campaign table with bid verdicts, resolved top five and the matched-zone
optional checklist, then link the combined review and applicable implementation files.

## 23. Review-only execution ceiling

Given the intake says manual implementation and no Ads mutations, prepare and verify the full pack
but do not start live execution. Mark an approved manual item `waiting_manual_execution`, not
`waiting_approval`, and wait for Michael as executor before live readback.

## 24. Mixed register parent state

Given one dependency-ready Lead action and one consequential action waiting for Michael, use parent
status `dispatch_ready`. Keep the consequential action individually `waiting_approval` and expose
its exact decision without blocking the Lead queue.

## 25. Active PMax diagnostic

Given any active PMax campaign, run the read-only monthly-review slice of `pmax-optimizer` in addition
to the mandatory bid-strategy verdict. Route conversion firing, goal and import anomalies to
`google-ads-conversion-audit`, not generic analytics skills.

## 26. Supplementary artefact delivery

Given a specialist produces Editor CSV, negative TXT or another implementation file, store it in the
same canonical `google_ads/YYYY-MM/` Drive folder, link it from the combined review, read it back,
and list its verified URL under `implementation_files`.

## 27. Manifest blocks premature BasicOps handoff

Given the bid/budget and conversion children pass but an active-Search keyword child has no terminal
QA receipt, do not create or update the BasicOps decision handoff. Return `analysis complete;
delivery incomplete`, the keyword child run ID and its first incomplete stage. A later resumption
must reuse that child and cycle identity rather than submit a duplicate.

## 28. Analysis is not execution

Given bid, keyword and PMax diagnostics recommend consequential changes, still deliver the combined
review and preparation files during the cron run. Do not mutate Google Ads; put only the protected
changes in `Michael approval required`.
