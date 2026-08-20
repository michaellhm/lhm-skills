# Prototype scanner false-positive repair — recorded role passes

Parent: `ASP-SITEMAP-V2-PUBLISH-20260820`  
Incident: `prototype-scanner-false-positive-20260820`  
Return point: `desktop-control-ASP-SITEMAP-V2-PUBLISH-20260820`

## 1. Capability Researcher — native repair selected

The reusable packaged `lhm-prototype-publisher` is the existing authoritative LHM capability. Its
bytes regex treated the `sk-` substring inside `desk-worker` and `desk-workers` as a provider
token. No third-party dependency, new permission, credential, connector or host capability is
needed. The smallest repair is a left alphanumeric boundary on only the existing `sk-` branch.

## 2. Platform Engineer — implemented in the supplied workspace

Added `(?<![A-Za-z0-9])` immediately before the existing `sk-[A-Za-z0-9]` expression. All other
secret alternatives and all schema-v2, source-path, manifest, idempotency, workflow, public-readback
and authority controls are unchanged. Added unit and packaged-host regressions and bumped the plugin
release version to `0.6.2` across both manifests, marketplace metadata and validation. No commit,
push, prototype publication, BasicOps mutation, credential access, live Hermes edit or parent resume
occurred.

## 3. QA Tester — pass

The focused publisher and packaged-parity suite passed 18 tests and 15 subtests. The full plugin
suite passed 79 tests and 15 subtests. Positive coverage includes the exact `desk-worker` and
`desk-workers` strings. Negative coverage includes provider tokens at the start and end of content,
in prose, assignment and JSON contexts, plus private-key, GitHub, AWS, password and client-secret
patterns. The packaged test extracts the release asset and validates the ASP schema-v2 fixture
identity with a content-addressed staged HTML surrogate while command and URL-fetch tripwires are
installed. The exact 115238-byte approved live artifact is not present in this isolated workspace,
so no claim is made that those unavailable bytes were rerun here.

Plugin validation, JSON parsing, Python and shell syntax, manifest/marketplace version parity and
`git diff --check` pass. Stateful idempotency, interrupted receipt recovery, moved-main rejection,
lease enforcement, workflow identity and exact public-readback controls continue to pass in the
full suite.

## 4. Security/Reliability Reviewer — approved for bounded branch review

The change neither broadens the scanned token alphabet nor weakens any other secret class. A true
`sk-` token remains rejected at a string boundary and after whitespace, punctuation, assignment or
JSON delimiters. Only an `sk-` substring immediately preceded by an ASCII alphanumeric byte is
excluded, closing the reported word-substring false positive. No dependency or supply-chain change
was introduced. Credential, network, filesystem, atomic receipt, lease, workflow and readback
boundaries are unchanged. Rollback is the exact prior packaged publisher asset/version; deployment
or rollback remains under Michael's separate authority.

## 5. Plugin Release Manager — workspace ready for bounded publisher

The persisted feature workspace is based on `origin/main` at
`f93a24525029683f9a4509a19f5cc728e079cd83` on
`cto/prototype-scanner-false-positive-20260820`. Version `0.6.2` is parity-bound across release
metadata. The root-owned bounded publisher may reconcile these exact persisted files, commit and
push only this generated `cto/*` branch, verify its remote SHA and create Michael's review note.
This record does not authorize merge, release, installation, prototype publication, parent-state
mutation or a capability-restored claim.
