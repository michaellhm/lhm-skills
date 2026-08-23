# Project Hub immutable production release

Project Hub is installed separately from the mutable `/home/hermes/.hermes/lhm-skills` checkout.
The supported target for this release is `lhm-project-hub` 0.1.73. Never `git pull` or copy files
into the live shared checkout as a deployment mechanism.

## Build

From the reviewed, clean, exact commit:

```text
python3 plugins/lhm-system-ops/scripts/build_project_hub_release.py \
  --output /var/lib/lhm-plugin-releases/lhm-project-hub-0.1.73.zip
```

Record the emitted commit and SHA-256. The builder reads only tracked bytes from `HEAD`, assigns a
fixed ZIP timestamp and mode, and refuses a dirty checkout or any version other than 0.1.73.

## Install approval

The deployer has one bootstrap step because an executable cannot install itself. After System Ops
0.8.8 is installed from its separately approved immutable archive, an operator with explicit
Michael approval verifies the source against `project-hub-deployer-release.json`, then performs the
single exact root-owned copy:

```text
sha256sum /home/hermes/.hermes/profiles/lhm_brain/plugin-sources/lhm-system-ops/assets/host/lhm-approved-project-hub-deployer
install -o root -g root -m 0755 \
  /home/hermes/.hermes/profiles/lhm_brain/plugin-sources/lhm-system-ops/assets/host/lhm-approved-project-hub-deployer \
  /usr/local/libexec/lhm-approved-project-hub-deployer
install -d -o root -g root -m 0750 /etc/lhm-plugin-approvals
openssl rand -out /etc/lhm-plugin-approvals/project-hub-approval.key 32
chown root:root /etc/lhm-plugin-approvals/project-hub-approval.key
chmod 0600 /etc/lhm-plugin-approvals/project-hub-approval.key
```

For deployer release 1.0.0 the first command must return
`2c2b2d80387d44ca2af85e87a793e1ad16ec678cd21006ac67b815c90391a747`; otherwise stop.

This bootstrap does not install Project Hub and must not enable a service. Record the installed
executable hash and keep the System Ops rollback available.

Michael or the delegated approver creates one root-owned `0600` record at
`/etc/lhm-plugin-approvals/<approval-id>.json`. It has exactly:

```json
{
  "schema_version": 3,
  "approval_id": "project-hub-0.1.73-install",
  "action": "install",
  "repository": "michaellhm/lhm-skills",
  "commit": "FULL_COMMIT_SHA",
  "plugin": "lhm-project-hub",
  "archive_sha256": "FULL_ARCHIVE_SHA256",
  "profile": "lhm_brain",
  "issued_at": "ISO-8601",
  "expires_at": "ISO-8601",
  "nonce": "32_TO_64_LOWERCASE_HEX_CHARACTERS",
  "used": false,
  "signature": ""
}
```

The root operator signs the exact closed-schema record without exposing the key:

```text
/usr/local/libexec/lhm-approved-project-hub-deployer sign project-hub-0.1.73-install
```

The HMAC covers schema, action, repository, exact commit, archive digest, plugin, profile,
issue/expiry times, nonce and unused state. Installation atomically claims the nonce with `O_EXCL`
in the root-private ledger before changing release pointers. Tampering, concurrent use or replay
therefore fails closed even if the JSON filename is reused.
Approvals must be timezone-aware, already issued, not expired and valid for no more than 24 hours.

After separate install approval, run as root:

```text
/usr/local/libexec/lhm-approved-project-hub-deployer install \
  project-hub-0.1.73-install \
  /var/lib/lhm-plugin-releases/lhm-project-hub-0.1.73.zip
```

The deployer verifies the allowlisted repository, clean exact commit, plugin identity/version,
archive digest and one-use approval. It extracts to the content-addressed immutable release root,
atomically switches the current symlink and each governed profile link, preserves displaced entries
in a root-only backup, and then consumes the approval. Verify the installed manifest, skill links,
`hermes -p lhm_brain skills audit`, enabled skill catalogue and a read-only BasicOps regression.

## Rollback

Rollback is a separate consequential action and needs a fresh schema-version 3 approval with
`action` set to `rollback`, a fresh nonce, `backup` set to the exact absolute backup returned by
installation, and `commit` plus `archive_sha256` copied from that backup's immutable release
binding. Sign it with the same bounded `sign` command, then run:

```text
/usr/local/libexec/lhm-approved-project-hub-deployer rollback \
  <rollback-approval-id> \
  /var/backups/lhm-plugin-deployments/<exact-backup>
```

The rollback restores the recorded prior symlink or directory for the current release, every
managed skill and the plugin-source registration. It does not delete immutable release evidence.
