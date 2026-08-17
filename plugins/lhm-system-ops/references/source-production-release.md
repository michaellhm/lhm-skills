# Source production release, smoke and rollback

No step here grants deployment authority. Michael approves merge, release and each live installation/enablement separately. The repository contains no source content, credential, token, connector configuration or live identifier.

## Operational inputs

Before installation, the operator creates a root-owned, non-world-readable JSON file with exactly `schema_version` and `backends`. `backends` has exactly `drive_read`, `fathom_read`, `production`, and `drive_publish`; each value is a non-empty argv array whose first item is the verified absolute executable of the existing authenticated route. Use the proven Claude dispatch/Drive connector, Fathom MCP profile command, campaign production worker and registered Drive publisher on that host. Do not use shell strings, inline environment variables, secrets, fixture programs, or speculative paths.

Each backend implements JSON stdin/stdout actions:

- read routes: `probe` returns exactly `{"authenticated":true,"capability":"read","identifier_accessible":true}` and `read` returns source bytes.
- production: `probe` returns exactly `{"capability":"campaign_playbook_production","ready":true}` and `produce` returns the full produced bytes.
- Drive publisher: `probe` returns exactly `{"authenticated":true,"capability":"publish_readback","identifier_accessible":true}`; `upsert` honours the supplied idempotency key; `read` returns `{"full_content":"..."}`.

The root-owned registration is `/etc/lhm-source-production/registrations/<run_id>.json`. It names the exact Drive file, Fathom recording and destination folder identifiers. It contains identifiers only, never source content or authentication material.

## Release and install

1. From the reviewed clean commit, run all tests and `python3 plugins/lhm-system-ops/scripts/validate_system_ops.py`.
2. Run `python3 plugins/lhm-system-ops/scripts/build_release.py --output /tmp/lhm-system-ops-<commit>.zip`; record the emitted SHA-256 and verify the archive is built from the approved commit.
3. On the host, verify the four configured backend absolute executables and their owning packages/profiles. Confirm connector credentials remain outside Hermes and the release.
4. With separate install approval, unpack the exact archive and run `plugins/lhm-system-ops/assets/install/install-source-production.sh /root-owned/path/adapters.json`. The installer creates or validates `sourceworker`, ownership, adapter links, config, units and sandbox, but does not enable or start anything.
5. Install the approved root-owned run registration with mode `0640`, owner `root`, group `sourceworker`.
6. As `sourceworker`, pipe the exact manifest to `/usr/local/libexec/lhm-source-adapter --preflight`. Any missing account, executable, registration, connector authentication, Drive file/folder access, Fathom read capability, production route or publisher read-back capability is a hard stop.
7. Review `systemd-analyze verify` and `systemctl cat lhm-source-production.service lhm-source-production.path`. Only after a separate enablement approval run `systemctl enable --now lhm-source-production.path`.

## Read-only authenticated smoke

Use the approved manifest and its matching registration; do not print content. Run both installed read adapters as `sourceworker`, piping `{"run_id":"<exact-run-id>","identifier":"<exact-registered-identifier>"}`. Redirect each response to a root-controlled `mktemp -d` directory, record only byte count and SHA-256, then delete the temporary directory. Run manifest-scoped `--preflight` first. For Drive, use the exact registered source file identifier; for Fathom, use the exact registered recording identifier. Success requires non-empty reads and stable hashes on a second read. This is read-only: do not invoke the publisher or production adapter.

## Rollback

1. Stop and disable only `lhm-source-production.path`; wait for any oneshot service to finish and retain its run directory and journal evidence.
2. Restore the previously recorded plugin archive/config and unit files, then run `systemctl daemon-reload`. If there was no prior version, remove only the five installed adapter/runtime paths and the two source-production units after copying audit evidence; do not remove registrations or run records.
3. Re-run `systemd-analyze verify`. Confirm the path is disabled and inactive. Do not delete `sourceworker`, connector profiles, credentials, registrations, or durable run evidence as part of rollback.
4. Re-enable a previous version only with Michael's separate approval. Publication of this branch or archive is not permission to install, enable, or mutate Drive.
