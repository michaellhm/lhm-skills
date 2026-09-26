# Prototype publication host lane — recorded role passes

Parent: `RTB-SITEMAP-FRESH-2188809-20260821`
Incident: `rtb-sitemap-fresh-proto-publish-host-lane-20260821`
Return point: `head_of_production.RTB_sitemap_fresh_publish`

## 1. Capability Researcher — native capability selected

The existing root-owned `lhm-prototype-publisher`, schema-v3 contracts and `prototype-main-v1`
profile already enforce the required repository, main branch, base commit, root-only deploy key,
standing authority, content-addressed package, exact workflow and HTTP hash readback. The missing
capability is the native host consumer between Hermes's shared dispatch store and the publisher's
root staging store. No third party, connector, new credential or broader authority is needed.

## 2. Platform Engineer — implemented in isolated workspace

Added a root host runtime and path/service units. The runtime watches the same host-visible
`/home/hermes/.hermes/profiles/lhm_brain/dispatch/prototype-publication/incoming` directory into
which the container dispatches, claims one request atomically, accepts only its matching sealed
request-id directory, verifies the exact sorted manifest, copies it into
`/var/lib/lhm-prototype-publication/incoming/<request-id>`, invokes only the installed bounded
publisher, validates receipt identity and exact verification evidence, and atomically returns the
schema-v3 receipt to the shared `processed` directory. Failures retain the request and an error in
`failed`; sealed evidence and publisher receipts are not deleted.

## 3. QA Tester — repository pass

Focused tests cover positive RTB staging/receipt return, tamper rejection before invocation,
extra-file and traversal rejection, publisher-result identity rejection, interrupted staging
retry, and restart replay of an atomic claim through the publisher's durable idempotency receipt.
The focused suite passed 6 tests; the full plugin suite passed 133 tests and 32 subtests. System-ops
manifest/skill validation, Python and JSON parsing, executable mode, version parity and
`git diff --check` also passed. These are local/mocked host
tests: live unit state, the queued request, GitHub publication, Actions and public HTTP evidence
remain installer/runtime evidence and are not claimed from the CTO sandbox.

## 4. Security/Reliability Reviewer — approved boundary

The consumer has no credential or network handling and no caller-selected executable. It uses a
single absolute publisher path; package and receipt identities fail closed; claims and results are
atomic; one process lock prevents concurrent queue scans; staging retry accepts only byte-identical
content. The systemd service can write only the shared prototype dispatch tree and prototype
publication state tree, with strict system protection and no-new-privileges controls. Repository,
branch, authority, credential, workflow, URL and content checks remain in the existing publisher.
Rollback disables/removes the two new units and runtime only; it preserves credentials, queue
evidence, receipts and published content.

## 5. Plugin Release Manager — bounded branch handoff only

Version `0.8.10` is aligned in both plugin manifests and validation. The root-owned bounded branch
publisher may reconcile the reported persisted paths, commit and push only the generated `cto/*`
branch, verify the remote SHA and write Michael's Obsidian review note. It must not merge or deploy.
After Michael separately approves an immutable release, root installation must install the runtime
and units, daemon-reload, enable/start the path unit, run the oneshot once to drain the existing
queue, and attest unit state plus exact processed receipt. Publication is not capability
restoration and Michael retains merge, release and deployment authority.
