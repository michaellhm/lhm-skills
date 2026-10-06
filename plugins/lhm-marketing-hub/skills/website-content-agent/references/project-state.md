# Persistent website content state

Keep the source of truth in the website repo under `docs/website-content/`, outside public output. Use Markdown for human context and JSON for page state. Do not include these records in public builds. If the repo is public, omit sensitive internal notes and store those in the private client working folder, referenced by project.md without copying secrets.

## Files

- `project.md`: verified repo/remote, client knowledge and work paths, playbook, sitemap authority, renderer/content paths, current booking route, template references, build/check commands, publication authorisation and deployment behaviour.
- `content-plan.json`: one entry per canonical destination; menu aliases point to the same page ID.
- `content-plan.md`: readable view generated from the JSON, with Draft ready and Client approved checkboxes. Do not edit this view independently of JSON.
- `client-learnings.md`: evidence-backed client preferences, scope, origin page/revision, date, feedback quote or faithful summary, confirmation status and superseded lessons.
- `action-plan.md`: active scope, ordered next steps, missing facts, blockers and resume instruction.
- `templates/<family>.md`: discovered page family contract and approved reference URLs/source files. Approval may be pending; record it rather than invent it.
- `pages/<page-key>/`: stage outputs with source references and reviewed revision identifier.

## Page entry

```json
{
  "id": "exercise-physiology",
  "title": "Exercise Physiology",
  "url": "/services/exercise-physiology/",
  "family": "service",
  "exists": false,
  "stage": "planned",
  "draftReady": false,
  "revision": null,
  "clientApproval": {"status": "unknown", "revision": null, "by": null, "at": null, "evidence": null},
  "reviews": {"editor": {"status": "pending", "revision": null}, "compliance": {"status": "pending", "revision": null}, "technical": {"status": "pending", "revision": null}},
  "recovery": {"failedStage": null, "error": null, "lastAcceptedRevision": null, "correctionCycles": 0},
  "publication": {"destination": null, "commit": null, "status": "not-published", "url": null},
  "blockers": []
}
```

Stages: planned, researching, briefing, writing, editing, compliance-review, integrating, ready-for-review, revisions-requested, complete, blocked. Record nonapplicable compliance reviews explicitly for non-healthcare projects.

`draftReady` becomes true only after required reviews pass for the current revision and the review artifact exists. The client's approval checkbox is checked only when approval status is approved AND its revision equals current revision. Neither agent QA nor Michael's internal approval is silently recorded as end-client approval. Store the approver's actual role. Client requests for revision set status changes-requested; changed approved copy resets status pending. Retain prior approval evidence in page review history. Use an artifact hash or content commit identifying the reviewed copy; unrelated code commits should not invalidate copy approval.

## Learning capture

`/learn` means capture the current project's client feedback, not automatically edit a global skill. Record each lesson with an ID, scope (site-wide, family, page), feedback evidence, confirmation and affected pages. Explicit general preferences can apply immediately. If a single edit only suggests a broader rule, label it proposed and ask before generalising. A factual correction remains page-specific unless verified elsewhere. Keep a supersession trail when the client changes direction.

Before each batch, list relevant lessons in the source pack. After revisions, save what changed and why. Do not propagate a healthcare claim merely because the client prefers it. Notify the user of any requested wording that remains unsupported.

## Review access

A repo Markdown tracker is internal state, not a secure client portal. A server-side review screen must use authentication, per-client authorisation and version-bound approval events. Never expose private records through `public/`, Astro static routes or unauthenticated endpoints. Do not grant client reviewers Git credentials or deployment authority as a side effect of copy access.

## Stage and release invariants

Every review identifies the canonical copy revision/hash. The writer creates copy.md; the editor revises that same canonical file and logs changes in editor-review.md. Compliance and integration consume copy.md at the accepted hash. Any copy edit resets affected review results; clinical meaning changes reset compliance too. Technical review is bound to the integrated source revision.

Track failedStage, error, lastAcceptedRevision and correctionCycles so retries and the correction limit survive a new chat. Stage complete means all requested work for this page has finished, including client approval and publication when those are part of the requested scope. A local checked draft stays ready-for-review; do not label it complete to imply approval or deployment.

project.md records release authorisation as structured fields: destination URL, branch, push effect (prototype/production), authorisedBy, evidence and scope. Pending fields remain null. Do not manufacture evidence from a generic statement about writing pages.

Setup completion means project.md, a deduplicated content plan, relevant discovered template contracts or explicitly recorded discovery tasks, client-learnings.md and action-plan.md exist. No copy production is implied. Template approval that is unknown remains unknown.
