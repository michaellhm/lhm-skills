# Disabled Site/Codex staging plan

1. Keep all `lhm-workflow-*.path` units disabled and stop both site launcher
   transient-unit prefixes. Confirm bridge queues are empty.
2. Verify the release tree hash, then install the candidate launcher under a
   versioned root-owned path. Do not replace the live launcher symlink yet.
3. Run `install-site-governed-assets.sh` against the pinned canonical
   `lhm-wordpress-hub/1.2.20` tree. Verify both installed SHA-256 values and the
   alias manifest byte-for-byte. The contract alias `start-astro` is the exact
   canonical `wp-start` file; this naming debt must remain explicit.
4. Provision root-owned `0640` Cloudflare provider profile and token file. The
   token is read-only and limited to Pages deployment metadata for the single
   account/project. Provision a root-owned scoped SSH config/key restricted to
   the single GitHub repository. No inherited Git config, agent, or PATH.
5. Create `/home/hermes/.hermes/profiles/lhm_brain/dispatch/site-reconciliation`
   as root:root `0700`. Install the reconciliation candidate root:root `0750`.
6. Run the full offline suite against installed bytes. Run negative tests as
   Codex UID: missing skill, changed prompt, wrong remote SHA, wrong provider
   project/branch/commit, alias without deployment metadata, symlinked recovery
   input, active unit, and post-skill retry.
7. With watchers still disabled, manually invoke one synthetic governed worker
   whose Git/Cloudflare calls use recorded fakes. Confirm event order is admit,
   skills, Git capability, preview capability, terminal.
8. Only then run one real staging branch manually. Independently read back the
   Git ref, Cloudflare deployment metadata, alias HEAD/noindex, promoted
   evidence ownership, and controller receipt. Do not merge or deploy main.
9. Obtain independent QA approval before changing the live launcher symlink or
   enabling any watcher. Rollback is symlink reversal; preserve protected event
   streams and evidence.
