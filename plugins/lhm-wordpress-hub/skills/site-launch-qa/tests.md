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

| Jaimee chooses “I’ll do it” | Give a compact section checklist and expected evidence; do not force a step-by-step lesson or repeat the mode question per item. |
| Jaimee chooses “Coach me” for GSC | Explain briefly, give one step, wait for the observed screen/result; adapt if different. |
| Jaimee asks the assistant to do the checks but phone/account access is unavailable | Run authorised accessible checks; leave physical-device/account evidence pending/blocked and ask for only those steps. |
| Sitemap default path returns 404 but WordPress sitemap exists elsewhere | Discover and validate the existing endpoint; do not generate a competing sitemap. |
| Sitemap exists but omits a public page found in the approved route inventory | Audit the omitted page and fail coverage; prepare generator/configuration repair, then validate and recheck live. |
| No sitemap and no live-deployment authority | Generate/configure and validate a repair in authorised source/staging; record prepared, request only missing deployment/submission authority, and keep live verification pending. |
| Root robots.txt accidentally blocks production service pages | Record effective rule and affected pages; prepare minimal fix, preserve deliberate restrictions, verify after authorised application. |
| Staging has intentional disallow/noindex | Do not remove restrictions as a generic optimisation; production checks remain separate. |
| Homepage passes but service page has duplicate titles/descriptions, two H1s or broken image | Full-inventory audit reports page/element failures and duplicate groups; homepage spot-check cannot pass SEO. |
| Decorative image has empty alt; informative image lacks alt | Accept decorative semantics, flag informative image; do not demand keyword-filled alt everywhere. |
| Sitemap is live but GSC access is unavailable or submission is processing | Keep site-side validation separate; mark GSC blocked or pending and do not claim indexed. |
| Jaimee changes from self-led to coaching halfway through | Preserve evidence and current step, switch mode without restarting completed sections. |
