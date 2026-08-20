# Reusable prototype publisher v2 — recorded role passes

Parent: `ASP-SITEMAP-V2-PUBLISH-20260820`  
Incident: `prototype-publisher-v2-20260820`  
Return point: `desktop-control-ASP-SITEMAP-V2-PUBLISH-20260820`

## 1. Capability Researcher — iteration-3 recommended

Native LHM already contained the repository-scoped iteration-1 ASP helper, bounded CTO branch
publisher, release builder and one-use root deployer. No third party is needed. Generalising the
native helper is smaller and safer than granting Hermes GitHub access. The route remains fixed to
`michaellhm/lhm-prototype` main, HTML sitemap/homepage paths, an exact base commit and the reviewed
GitHub workflow. The live failure and the retained iteration-1 workspace prove this is a native
release-parity/carry-forward defect; no third-party dependency or broader authority is warranted.

## 2. Platform Engineer — iteration-3 implemented in workspace

Added a reusable content-addressed publisher, closed request/result and BasicOps handoff schemas,
exact public byte/hash readback, authoritative workflow identity checks, tests and this release
record. Iteration-2's exact workflow ID/name/path and public byte/hash readback controls are retained.
Evidence-loop workspaces now start from the immediately prior iteration branch and reject missing
lineage or stale branch collisions. The legacy ASP executable is a compatibility entry point. No commit, push, installation,
credential access, BasicOps mutation, live Hermes change or parent resume occurred.

## 3. QA Tester — iteration-3 pass

The final handoff records exact commands and disposition. Coverage includes packaged-host-asset
parity against the approved ASP schema-version 2 fixture, carry-forward through iterations 2 and 3,
manifest/path/schema
negatives, credential absence, public-content mismatch, workflow identity, plugin validation,
compatibility and the supplied ASP package evidence. The complete plugin suite passed with 76 tests
and 5 subtests, followed by plugin validation, JSON parsing, syntax, version/script parity and
`git diff --check`. Root-side staging, GitHub publication,
workflow execution, HTTP regression and non-root credential-read checks remain installation-time
tests and are not claimed here.

## 4. Security/Reliability Reviewer — iteration-3 approved for bounded branch review

The parity defect is closed in repository scope. The request has no command, refspec, arbitrary URL or credential field. Credentials remain one
repository-scoped write deploy key under `/etc/lhm-prototype-publisher` (directory root:root 0700;
private key root:root 0600). Staging is exact-request-bound; paths, sizes, hashes, symlinks and
sensitive content fail closed. Exclusive locks, atomic receipts, stale-temp recovery and the final
base-bound lease prevent duplicate or moved-main writes. Workflow mismatch and public byte/hash
readback mismatch fail closed. Residual live risks require the root installer attestation and regression below.

Rollback removes or restores only the installed `lhm-prototype-publisher` executable and legacy
compatibility entry point from the install inventory, plus their bounded trigger/config if added.
It does not delete credentials, repository content, publication evidence or published commits.
Re-enabling an older executable requires Michael's separate approval.

## 5. Plugin Release Manager — iteration-3 ready for bounded publisher

The bounded CTO publisher must first commit and push only this workspace's generated `cto/*`
branch and return the verified remote SHA. Version `0.6.1` must match both plugin manifests and the
marketplace entry; package-parity coverage extracts and invokes the same host asset path that the
release contains against the approved ASP v2 fixture. The deterministic release must contain that
same tested asset. Desktop control then builds the exact clean-commit
archive, records its SHA-256, binds Michael's standing authority to a one-use installation record
containing that SHA and archive digest, consumes it through the root deployer and verifies installed
digests. Publication is not installation, merge, restoration or authority to modify prototype main.

### Authoritative regression envelope

- Source task: BasicOps `2191545`, <https://app.basicops.com/481630853364967730?l=_805_31C_1AZ09FC34BD>
- Parent: `ASP-SITEMAP-V2-PUBLISH-20260820`
- Source: `/opt/data/profiles/lhm_brain/vault/20 Clients/Australian Sports Physio/project-management/Australian-Sports-Physio-Sitemap-Version-2.html`
- Source bytes/SHA-256: `115238` / `74b87dbc0f20c1d79326e11f342e1169d5777f17eded8683729f57b0d7650a70`
- Sorted manifest: `[{"path":"australian-sports-physio/sitemap/index.html","sha256":"74b87dbc0f20c1d79326e11f342e1169d5777f17eded8683729f57b0d7650a70","bytes":115238}]`
- Package-manifest SHA-256: `b52a6de06e5e30a20b24e8e5b5a3c8c1703ffef04c93df2dde4d3026305f5115`
- Root staging: `/var/lib/lhm-prototype-publication/incoming/asp-sitemap-v2-publish-20260820`
- QA: `claude-producer-20260819-94`, `final.json`, completed `html_artifact_producer`; canonical Drive and BasicOps readbacks match
- Authority: `MICHAEL-PROTOTYPE-PUBLISH-STANDING-20260820` in `60 Knowledge/Prototype Publication Standing Authority.md`
- Recorded prototype main before regression: `f00b1d8606e9cd71e45dda299f3b7837c82f17be`
- Workflow: `Deploy to lhmstaging`, ID `289562388`, `.github/workflows/deploy.yml`

After exact installed-digest verification, root stages and independently hashes the source, invokes
one base-bound publication, verifies the exact workflow run and exact-content HTTPS readback, then
emits one closed `prototype_regression_verified` handoff. BasicOps must read back the URL, exact
prototype commit and QA reference; stay open `Under Review`; reviewer Michael; next handoff
Kristalyn for David. Only after that readback may the existing exact-once `capability_restored`
event for incident `asp-proto-publish-route-20260820` be consumed and work-control verify the saved
parent resumed at `Head of Production`. Failure at any step preserves the parent and emits no
restoration claim.
