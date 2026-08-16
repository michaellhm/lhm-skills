---
name: lhm-plugin-release-manager
description: Package and deliver an exact tested LHM plugin commit through GitHub and the approved Hermes installer. Use after QA and security review pass.
---

# LHM Plugin Release Manager

## GitHub handoff

Verify the working tree, base commit, branch naming, plugin version bump, marketplace parity and validation evidence. Push only the feature branch and create or update one pull request. Never push protected `main` or merge without separate authority.

The pull request must contain incident and parent IDs, outcome, changed plugins, tests, QA disposition, security disposition, permissions, rollout, rollback and the commit SHA intended for deployment.

## Hermes deployment

After merge or an explicitly approved immutable commit, build the deterministic plugin archive and digest. The root-owned installer must verify the allowlisted repository, clean exact commit, plugin name, package SHA-256, approval expiry and unused state before atomically replacing the installed plugin with a backup.

Verify installed version/commit, refresh Hermes's plugin catalogue in the supported way and run the original capability regression. Then instruct CTO to emit `capability_restored`; do not close at “PR merged” or “plugin installed.”
