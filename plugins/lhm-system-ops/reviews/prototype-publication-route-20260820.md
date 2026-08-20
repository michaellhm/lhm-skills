# Prototype publication route review — 2026-08-20

Incident: `rtb-proto-publish-route-20260820`  
Parent: `RTB-SITEMAP-PUBLISH-2188809-20260820`  
Return point: `release_publishing_engineer.RTB_sitemap_publish`  
Branch: `cto/rtb-proto-publish-route-20260820`  
Base commit: `5aedac70eafb09d4dcbe394879f4ecf9a25ddaaa`

## Capability Researcher pass

Decision: use the existing native LHM closed handoff pattern. `source-dispatch`,
`lhm-source-production.path`, `lhm-source-production.service`, and
`lhm-source-production-runtime` demonstrate the required container-to-root queue boundary. The
already installed `lhm-prototype-publisher` remains the sole publication authority and already
enforces the fixed repository, branch, destination profile, credential reference, standing
authority, manifest digest, expected-base lease, and idempotency contract. No third-party
dependency, new credential, or publisher change is required.

## Platform Engineer pass

Implemented `prototype-dispatch`, a container-side submit/status helper that accepts only schema_v3,
the fixed `prototype-main-v1` route, and a sorted, exact, digest-matching sealed package below its
fixed sealed root. Implemented a root systemd path/service consumer that independently validates
the queued request and every staged byte, rejects unmanifested files and symlinks, stages only at
`/var/lib/lhm-prototype-publication/incoming/<request_id>/`, and invokes only
`/usr/local/libexec/lhm-prototype-publisher --request <staged-request>`. Public queue receipts are
mode `0644`; staged requests remain mode `0600`. The helper contains no host credential path or key
reference. Plugin and marketplace versions move in parity from 0.8.4 to 0.8.5.

## QA Tester pass

Disposition: **pass**.

- `PYTHONDONTWRITEBYTECODE=1 pytest -q` — 140 passed, 32 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 11 skills.
- `git diff --check` — passed.
- AST parse of both new executable Python assets — passed.

Coverage includes exact submission and staging, fixed publisher argv, structured readable receipt,
manifest/package digest, expected base commit, idempotency/replay mismatch, arbitrary and parent
symlink paths, extra files, repositories, branches, destination profiles, credentials, standing
authorities, client/project slugs, commands, and refspecs. Existing prototype publisher tests also
remain green. Root/systemd execution and live publication are intentionally static or mocked because
this lane has no authority to install, use host root, access credentials, or mutate a live site.

## Security and Reliability Reviewer pass

Disposition: **approved for bounded branch handoff**.

- Authority ceiling is unchanged: `michaellhm/lhm-prototype`, `main`, `prototype-main-v1`,
  `LHM_PROTOTYPE_MAIN_DEPLOY_KEY`, and
  `MICHAEL-PROTOTYPE-PUBLISH-STANDING-20260820` only.
- The container asset neither names nor reads `/etc/lhm-prototype-publisher`; the host unit makes the
  sealed container source inaccessible to the root consumer and grants the existing publisher only
  its existing read-only credential directory plus bounded state/checkout writes.
- Closed schemas and literal publisher argv prevent command/refspec injection. Resolved-path checks,
  symlink rejection, sorted unique manifests, byte counts, per-file SHA-256, package SHA-256, and
  rejection of unmanifested files prevent source substitution.
- Atomic directory/receipt replacement and exact staged-request comparison support interrupted-run
  recovery without accepting a changed request under the same idempotency key. The installed
  publisher retains its own exclusive lock, receipt, expected-base lease, exact remote verification,
  workflow verification, and public byte readback.
- Public failure status is deliberately generic. No credential material or subprocess stderr is
  returned to Hermes. No BasicOps mutation or `capability_restored` event is present.

Residual risk: actual systemd ownership/mount wiring and installed-publisher execution require the
separately authorized root installation/release process and independent host QA. Rollback is removal
or disabling of only the new path/service/helper/runtime assets; the existing publisher and its
credential directory are unchanged.

## Plugin Release Manager pass

Disposition: **ready for the bounded publisher; not committed or pushed by the CTO lane**.

The generated `cto/*` branch name, 0.8.5 manifest/marketplace parity, base commit, changed paths, QA,
and security disposition are recorded. Per incident authority, this workspace must be handed to the
root-owned bounded branch publisher to reconcile persisted paths, create and push the generated
feature-branch commit, verify GitHub, and write Michael's Obsidian review note. No commit, push,
merge, install, publication, live mutation, or capability-restored event was performed here.
