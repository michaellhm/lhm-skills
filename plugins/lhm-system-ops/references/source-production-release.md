# Source production release, smoke and rollback

No step here grants deployment authority. Michael approves merge, release and each live installation/enablement separately. The repository contains no source content, credential, token, connector configuration or live identifier.

## Operational inputs

Before installation, the operator creates a root-owned, non-world-readable JSON file with exactly `schema_version` and `backends`. `backends` has exactly `drive_read`, `fathom_read`, `production`, and `drive_publish`. Use these non-recursive argv arrays exactly: `drive_read` is `[/usr/local/libexec/lhm-evidence-claude-dispatcher, google_drive_exact_file_read]`; `fathom_read` is `[/usr/local/libexec/lhm-evidence-fathom-backend]`; `production` is `[/usr/local/libexec/lhm-evidence-claude-dispatcher, campaign_playbook_production]`; and `drive_publish` is `[/usr/local/libexec/lhm-evidence-claude-dispatcher, google_drive_exact_folder_publish]`. No backend may name an adapter executable. Do not use shell strings, inline environment variables, secrets, fixture programs, or speculative paths.

Each backend implements JSON stdin/stdout actions:

- read routes: `probe` returns exactly `{"authenticated":true,"capability":"read","identifier_accessible":true}` and `read` returns source bytes.
- production: `probe` returns exactly `{"capability":"campaign_playbook_production","ready":true}` and `produce` returns the full produced bytes.
- Drive publisher: `probe` returns exactly `{"authenticated":true,"capability":"publish_readback","identifier_accessible":true}`; `upsert` honours the supplied idempotency key; `read` returns `{"full_content":"..."}`.

The root-owned registration is `/etc/lhm-source-production/registrations/<run_id>.json`. It names the exact Drive file, Fathom recording and destination folder identifiers. It contains identifiers only, never source content or authentication material.

## Release and install

1. From the reviewed clean commit, run all tests and `python3 plugins/lhm-system-ops/scripts/validate_system_ops.py`.
2. Run `python3 plugins/lhm-system-ops/scripts/build_release.py --output /tmp/lhm-system-ops-<commit>.zip`; record the emitted SHA-256 and verify the archive is built from the approved commit.
3. Before installation, record SHA-256, owner, group, mode and size for every path in the exact rollback inventory below, recording absent paths as absent. Independently verify `/usr/local/libexec/lhm-claude-dispatcher` is `dbcb320cbb0b3f6fd036e7129c2cc4d37b688ac4d4af50bae5470e497d487f95`, root:root 0755, 20336 bytes and `/usr/local/libexec/lhm-claude-worker` is `ec28d515a37bd3f10e2a2dedf5080a3eb3529065da4b4bc0445ce080a705a531`, root:root 0755, 13999 bytes. Archive existing inventory files with metadata into a root-only directory. Confirm connector credentials remain outside the archive.
4. With separate install approval, unpack the exact archive and run `plugins/lhm-system-ops/assets/install/install-source-production.sh /root-owned/path/adapters.json /root-owned/path/evidence-routes.json`. The installer creates or validates `sourceworker`, ownership, adapter links, additive evidence gateways, config, units and sandbox, but does not enable or start anything. It checks both shared gateway hashes and metadata before and after installation and never writes either shared path.
5. Install the approved root-owned run registration with mode `0640`, owner `root`, group `sourceworker`.
6. As `sourceworker`, pipe the exact manifest to `/usr/local/libexec/lhm-source-adapter --preflight`. Any missing account, executable, registration, connector authentication, Drive file/folder access, Fathom read capability, production route or publisher read-back capability is a hard stop.
7. Review `systemd-analyze verify` and `systemctl cat lhm-source-production.service lhm-source-production.path`. Only after a separate enablement approval run `systemctl enable --now lhm-source-production.path`.

## Read-only authenticated smoke

Use the approved manifest and its matching registration; do not print content. Run both installed read adapters as `sourceworker`, piping `{"run_id":"<exact-run-id>","identifier":"<exact-registered-identifier>"}`. Redirect each response to a root-controlled `mktemp -d` directory, record only byte count and SHA-256, then delete the temporary directory. Run manifest-scoped `--preflight` first. For Drive, use the exact registered source file identifier; for Fathom, use the exact registered recording identifier. Success requires non-empty reads and stable hashes on a second read. This is read-only: do not invoke the publisher or production adapter.

Before that authenticated source smoke, separately prove container visibility without changing the profile: `/usr/bin/docker exec -i -u hermes hermes test -x /opt/hermes/.venv/bin/hermes` and `/usr/bin/docker exec -i -u hermes hermes test -r /opt/data/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md`. Then run the Fathom adapter and retain redacted Hermes logs proving `mcp__fathom__get_meeting_transcript` succeeded. The host static preflight intentionally checks only `/home/hermes/.hermes/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md`; it must not mistake the container path for a host path.

For a production-only smoke, use synthetic non-client evidence and verify the installed `lhm-marketing-hub` version contains `agents/content.md`. The evidence worker maps external `lhm-marketing-hub:content` to `claude --agent content`, parses Claude stdout as JSON, takes `payload["result"]`, and requires a non-empty string. Drive profiles use only the documented minimum tools in `/home/claudeworker-repair`, remove an optional JSON code fence from that result, and then require the exact declared object.

## Rollback

1. Stop and disable only `lhm-source-production.path`; wait for any oneshot service to finish and retain its run directory and journal evidence.
2. Exact rollback inventory: `/opt/data/profiles/lhm_brain/bin/source-dispatch`, `/usr/local/libexec/lhm-source-production-runtime`, `/usr/local/libexec/lhm-source-adapter`, `/usr/local/libexec/lhm-evidence-claude-dispatcher`, `/usr/local/libexec/lhm-evidence-claude-worker`, `/usr/local/libexec/lhm-evidence-fathom-backend`, `/usr/local/libexec/lhm-evidence-bridge-preflight`, the four adapter symlinks, `/etc/lhm-source-production/adapters.json`, `/etc/lhm-source-production/evidence-routes.json`, `/etc/lhm-source-production/worker-profile.json`, `/etc/systemd/system/lhm-source-production.service`, and `/etc/systemd/system/lhm-source-production.path`. Restore each path recorded present byte-for-byte with its recorded owner/group/mode; remove each path recorded absent. Reject an inventory with any other path. Then run `systemctl daemon-reload`.
3. Never restore, remove, or otherwise mutate `/usr/local/libexec/lhm-claude-dispatcher`, `/usr/local/libexec/lhm-claude-worker`, registrations, credentials, sourceworker, existing shared profiles, or durable run evidence. Recheck the two supplied shared hashes and metadata after rollback.
4. Re-run `systemd-analyze verify`. Confirm the path is disabled and inactive.
5. Re-enable a previous version only with Michael's separate approval. Publication of this branch or archive is not permission to install, enable, or mutate Drive.
