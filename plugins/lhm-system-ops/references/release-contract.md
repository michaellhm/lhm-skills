# LHM plugin release contract

The Git checkout, installed Hermes plugin and deployment authority are separate:

- `/srv/lhm-plugin-source` — restricted development checkout owned by `ctoworker`;
- `/home/hermes/.hermes/profiles/lhm_brain/skills` — live generated installation, never a working tree;
- `/etc/lhm-plugin-approvals` — root-owned one-use approval records;
- `/var/backups/lhm-plugin-deployments` — timestamped rollback copies;
- root-owned deployer — validates and installs an exact commit/package only.

Development authority may fetch, branch, edit, test, commit and push `cto/*`. It cannot push protected `main`, merge, edit the live install or create approval records.

Deployment approval binds approval ID, repository, commit, plugin name, package SHA-256, target profile, issue/expiry time and unused state. The deployer consumes it atomically and records the result.
