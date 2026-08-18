# LHM plugin release contract

The Git checkout, installed Hermes plugin and deployment authority are separate:

- `/srv/lhm-plugin-source` — restricted development checkout owned by `ctoworker`;
- `/home/hermes/.hermes/profiles/lhm_brain/skills` — live generated installation, never a working tree;
- `/etc/lhm-plugin-approvals` — root-owned one-use approval records;
- `/var/backups/lhm-plugin-deployments` — timestamped rollback copies;
- root-owned deployer — validates and installs an exact commit/package only.

Development authority may fetch, branch, edit, test, commit and push `cto/*`. It cannot push protected `main`, merge, edit the live install or create approval records.

The branch publisher holds a repository-scoped SSH deploy key in a root-only directory. The CTO
worker cannot read it. The publisher accepts only an existing isolated CTO workspace based directly
on `origin/main`, a generated `cto/*` branch and reconciled persisted paths under `plugins/` or the
two reviewed repository metadata files. It creates the commit, pushes the exact SHA without force,
verifies the remote ref and then writes a Michael review note. GitHub branch protection remains the
independent control preventing direct protected-main publication.
GitHub transport uses its documented SSH-over-HTTPS endpoint on port 443 with the official pinned
Ed25519 host key, avoiding general outbound-network expansion and interactive host-key trust.

Deployment approval binds approval ID, repository, commit, plugin name, package SHA-256, target profile, issue/expiry time and unused state. The deployer consumes it atomically and records the result.
