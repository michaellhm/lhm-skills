# Completion QA acceptance scenarios

These are review scenarios for the instruction workflow, not automated website tests. Exercise them when changing the combined protocol; a document review does not certify a client site or a real device.

| Scenario | Required decision / evidence |
|----------|------------------------------|
| Approved brief says booking opens in a new tab; site opens it in the current tab | Source-linked requirement fails; record actual behaviour, owner and phone retest after correction. |
| Browser screenshots pass; Jaimee has not used her phone | Automated results may pass; real-device items remain pending and final completion is correction_required. |
| Phone link opens the dialler with a wrong number | Fail against approved contact record, even if the link works. Do not place a real call. |
| Earlier meeting note and later approval disagree | Use evidenced latest approval; if approval/order is unclear, request clarification and retain the gap. |
| Required project brief is inaccessible | Record missing source/coverage; delivery verdict blocked, not a generic requirements pass. |
| GTM snippet is present but GA4 receives no observed test event | Installation-only result; tracking cannot pass. Diagnose evidence gap or fail observed behaviour; return to tracking owner. |
| Booking click is recorded, but booking-completion integration is unavailable | Pass only the evidenced click test; keep required completion-event verification blocked. |
| Staging deliberately has noindex and test tracking | Judge staging against its declared configuration; production indexing/tracking checks remain pending until launch. |
| Wrong booking destination is fixed | Retain failure, rerun affected automated and Jaimee phone checks, and record new evidence before passing. |
| Actual tester is another team member | Record their identity and tested coverage; do not attribute results to Jaimee or complete her pending review. |
| Astro site has no WordPress state file or prototype | Use actual Astro project/URLs and responsive-only evidence; do not invent design-comparison evidence. |
| Report prepared while Jaimee is offline | Save pending checklist; do not claim a task assignment/message occurred without an authorised operation and readback. |
