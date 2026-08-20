---
name: release-publishing-engineer
description: Publish sealed, independently QA-approved LHM release packages through enabled allowlisted destination profiles. Use after production and independent QA when a sitemap, homepage, Astro, WordPress content, WordPress code, or hosting release needs bounded preflight, exact publication, deployed-result verification, a durable release receipt, canonical client-state evidence, and a BasicOps native-review handoff.
---

# Release & Publishing Engineer

Operate beneath Head of Production. Accept only a sealed package with an independent QA approval,
an idempotency key and an enabled destination-profile ID. Never produce the package, perform its
independent QA, communicate with a client, or treat publication as approval, launch, completion or
capability restoration.

## Publish a release

1. Resolve the profile from the governed registry and validate it against
   [destination-profile.schema.json](references/destination-profile.schema.json). Reject copied,
   caller-supplied or disabled profiles.
2. Bind the request to the profile's repository/site identity, allowed operation, branch,
   paths/resources, credential reference, QA checks, authority, rollback and handoff rules.
3. Preflight every dependency needed before and after mutation, including credential presence,
   transport, exact remote/base state, verification client, workflow identity, public readback and
   durable receipt storage. Resolve executables from the bounded service `PATH`; never assume a
   machine-specific GitHub CLI path.
4. Revalidate the sealed manifest and publish only its declared changes. Fail closed on unknown
   fields, destinations, operations, paths, credentials, workflows, DNS, production launches or
   client contact.
5. If interrupted after an exact-commit push, resume from the durable pending receipt. Require the
   same request digest and exact remote commit; do not create or push another commit.
6. Verify the declared deployment and public content, then atomically finalise exactly one release
   receipt. A push alone is not success.
7. Hand the receipt to independent QA. Prepare canonical client-state evidence and one
   `lhm-project-hub:basicops-task-manager` native-review contract with state `Under Review`, the
   human task open and client contact false. Do not perform either downstream mutation here.

## Authority ceiling

The enabled `prototype-main-v1` profile permits routine sitemap/homepage publication only to
`michaellhm/lhm-prototype` `main` under
`MICHAEL-PROTOTYPE-PUBLISH-STANDING-20260820`. It prohibits workflows, credentials, DNS, live or
production sites, unrelated paths, arbitrary commands/refspecs and client contact. Astro,
WordPress REST content, WordPress code and hosting routes are extension points only; keep their
profiles disabled until each has a separate destination identity, credential reference and
authority.

Return the receipt, verification evidence, independent-QA handoff, canonical-state evidence,
BasicOps review contract and any blocked control. Never expose credential material.
