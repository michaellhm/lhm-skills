# Google Ads monthly operating model tests

## 1. Scheduled morning review

Given canonical Obsidian context and all connectors, the run must compare current/prior 30 days, verify prior commitments, save/read back Drive, create one BasicOps parent without execution subtasks, and return `waiting_michael_hermes`.

## 2. Missing canonical goals

Given absent CPA economics, the run must report the precise canonical gap. It must not create `goals.md`, `current-projects.md` or `client_profile.md` in the plugin or working directory.

## 3. Ads/GA4 anomaly

Given zero Ads conversions and GA4 conversions in the same campaign/window, the run must describe an attribution/import discrepancy, lower measurement confidence, and not turn the performance zone Red solely because of tracking.

## 4. AdPulse unavailable

The run must label its zone source `manual_fallback`, show the calculation and continue. It must not claim an AdPulse pull.

## 5. Approval boundary

Saving Drive and creating BasicOps must not approve Ads mutations. Proposed actions remain `pending`; no execution subtasks or specialist mutations occur.

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
