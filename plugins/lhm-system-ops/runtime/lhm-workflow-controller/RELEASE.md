# LHM SEO client-preflight release — 2026-08-22

Release version: `0.1.4`.

## Provenance

- Baseline: the audited RC10 controller tree retained at `/private/tmp/lhm-rc10-audit/lhm-workflow-controller`.
- Client gate: `src/lhm_workflow/client_preflight.py`, the `client_id` canary contract, and the
  direct preflight checks in `integration/lhm-seo-org-canary-mvp`.
- Supervisor fix: the root supervisor creates the bounded child run directory before validating
  its ownership and mode.
- Tracker fix: tracker artifact IDs are namespaced by parent run so separate runs cannot collide.
- Parent evidence fence: release bundles include only the selected parent's contracts, operations,
  receipts, mappings, bridge records, requests, registry entries, artifacts, and tracker block.
- Preflight evidence trust: the client record and its smoke-test evidence must be safe regular
  files, the evidence hash must match, and GSC evidence must bind the configured property and
  read-only capability.
- Linux gate portability: the root-only foreign-owner regression uses `os.chown`, which is
  available on every supported Python version, rather than the newer `Path.chown` convenience API.
- Vault/evidence owner split: the synchronized capability record must match the fixed canonical
  vault owner, while referenced runtime evidence remains independently root-owned and mode `0600`.
- Manual proof parent: `lhm-seo-onboarding-20260822-070717`.
- Manual proof evidence SHA-256:
  `6193b923f2464599c6755a1f4f0198f781224c8b6a2d922228c38f59b03df577`.

## Release boundary

This package contains controller source, fixed integration entry points, packaging assets,
documentation, and tests. It excludes caches, bytecode, transient run evidence, keys, credentials,
and live configuration.

No cron, watcher, service, or live route is enabled by this release record.

## Rollback

Before any later installation, retain the exact installed package and integration executable
hashes. Rollback is byte-for-byte restoration of those retained files followed by the same local
test suite and inactive-service verification. Do not roll back client JSON or run evidence as part
of a runtime rollback; those are independent canonical records.

For the current source-only checkpoint, rollback is simply removal of this versioned subtree from
the repository. There is no live-system rollback because this checkpoint performs no installation.
