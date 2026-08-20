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

## ASP sitemap publication route

`lhm-asp-sitemap-publisher` is a separate root-owned capability. Its closed request schema accepts
only `michaellhm/lhm-prototype`, branch `main`, an exact expected base commit, files below
`australian-sports-physio/sitemap/`, and at most one minimum README link update. There are no fields
for commands, refspecs, DNS, client contact, unrelated repositories or prototype paths, or the live
ASP production site. Its repository-scoped credential and GitHub CLI session remain root-only.
Source packages are accepted only from the exact root-controlled request staging directory.

The route fails closed if main moved, the checkout contains an unapproved path, the exact remote
commit cannot be read back, the exact-commit GitHub Actions run is absent or unsuccessful, or the
staging sitemap URL does not return a bounded non-empty HTTP 200 response. A commit or push alone is
never success. Installation records prior executable metadata and digest; rollback restores or
removes only that executable and its bounded trigger/config, never credentials or published content.
A separately recorded, base-bound human authority is required before invoking the installed route.
