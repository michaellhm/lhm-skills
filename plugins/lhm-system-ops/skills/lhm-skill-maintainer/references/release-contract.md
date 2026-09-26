# LHM skill release contract

Apply repository-local instructions first when they are stricter.

## Canonical repository

- Default LHM skill source: `michaellhm/lhm-skills`.
- Verify the remote URL and base SHA before editing.
- Installed profile paths such as `/home/hermes/.hermes/profiles/*/skills` and `/opt/data/profiles/*/skills` are generated/live destinations, not working trees.

## Version and catalogue rules

- Bump the affected plugin's patch version in every manifest required by the repository.
- Update catalogues, skill counts and agent routing entries required by repository instructions.
- Keep duplicated or generated artifacts in parity using the repository's validators.
- A profile-only operational skill must first be added to an appropriate governed plugin or explicit profile-asset package with a deployment path.

## Git and publication

- Branch: `cto/<incident-or-task>-<short-name>`.
- Commit only reviewed, allowlisted paths.
- Push through the bounded branch publisher; the coding worker must not receive its credential.
- Verify the remote branch SHA after push.
- Open a pull request; never push protected `main` directly.
- Merge and deployment require explicit authority for the candidate change or immutable commit.

## Deployment

- Build from a clean exact commit.
- Use the approved root-owned installer or profile-asset deployer.
- Install atomically with a recoverable backup.
- Verify plugin version, commit/digest and relevant file hashes after installation.
- Restart only affected gateways/services when required.
- Run the original acceptance test and confirm the originating workflow can resume.

## Rollback

- Record pre-deployment version, hashes, ownership and permissions.
- Restore the previous immutable release or exact backed-up profile asset.
- Restart only affected services and rerun the prior healthy smoke test.
- Report `rolled_back` with the failed candidate SHA and retained evidence.
