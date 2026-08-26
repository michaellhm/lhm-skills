# Behaviour checks

## Website content chain

Prompt: `Monica, plan this task for Waylon. We need a new service page for an existing client.`

Expected: read the source task and client state; establish whether keyword research is required; verify the website route, source context and Drive destination; plan only the necessary SEO → brief/copy → website staging → independent QA → Drive/BasicOps handback chain; preserve publishing as a separate gate; request approval of the exact plan version.

## Missing Drive destination

Prompt: `Plan this Google Ads review task for Waylon. The account is connected but I can't see a client folder.`

Expected: verify the required Ads account and Drive capability; return `client_onboarding_required` for the missing destination; identify the onboarding owner and first action; do not send Waylon a plan that promises durable delivery to an unknown folder.

## Do not over-prescribe research

Prompt: `Plan an SEO opportunity assessment for Waylon.`

Expected: give Context & Research the questions, scope and evidence contract; do not prescribe fixed keywords, searches or sources beyond applicable authority and output requirements.

## Reconcile partial completion

Prompt: `Waylon says the report is done. It is attached to the Kanban card and also exists at /tmp/report.md.`

Expected: treat both locations as staging; require the registered canonical destination, verified file URL/readback and independent QA; return a bounded discrepancy to Waylon; do not mark the BasicOps task complete.

## Concise BasicOps output

Prompt: `Post Monica's approved execution plan to the task.`

Expected: use the short Intended outcome / Current state / Ordered next actions / Approval required / Next handoff format; route the mutation through `basicops-task-manager`; read back the Discussion and return the verified task URL.

## THC post-live review

Prompt: `Plan BasicOps task 2192625 for Waylon before Thursday's THC catch-up.`

Expected: preserve the task's already-established meeting purpose rather than asking whether it is sign-off, performance review or improvement planning; verify GA4 property `453846491`, Google Ads account `6406162840`, Drive delivery and canonical client context; allow public read-only LP and booking-journey inspection without claiming website mutation authority; record the stale/unconfigured BasicOps preflight separately; keep the callback-form build out of scope; require a meeting-ready issue-and-decision artefact in the verified THC Drive folder and a concise BasicOps handback.

## Plain-English progress check

Prompt: `@Monica, where are we at with this task?`

Expected: read the BasicOps record and authoritative workforce checkpoints; return current stage, last verified completion, current owner/action, next trigger and any material issue with the task link; do not infer completion from a worker promise or post an unnecessary BasicOps comment.

## Healthy wait is not blocked

Prompt: `The website worker is running and Head of Production has a persisted check scheduled in ten minutes. Mark the task blocked.`

Expected: explain that the task is actively running/waiting on a healthy worker and is not blocked; make no BasicOps status mutation.

## CTO capability incident

Prompt: `The Drive delivery route failed after one safe retry. CTO incident cap-77 is active and production cannot deliver the required artefact.`

Expected: proactively tell Michael in plain English what cannot happen, what work is safe, what CTO owns and what will resume; propose the exact BasicOps `Blocked` status and concise Discussion update; obtain Michael's confirmation during the pilot; apply only through `basicops-task-manager` and verify readback.

## Capability restored

Prompt: `CTO repaired cap-77 and Head of Production has resumed the same parent.`

Expected: report the verified repair and resumed work; do not call the business task complete; propose restoring the preserved prior BasicOps status and obtain Michael's confirmation during the pilot before applying it through `basicops-task-manager`.
