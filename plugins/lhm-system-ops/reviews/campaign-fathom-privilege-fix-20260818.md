# Campaign Fathom privilege fix — recorded role passes

Incident `campaign-fathom-privilege-fix-20260818`; parent `campaign-playbook-flow-20260818-01`; return point `head_of_production.release_and_live_test`. Feature branch only; no host, live Hermes, GitHub, or deployment mutation occurred.

## 1. Capability Researcher — completed

Verified repository-native Hermes Fathom lookup, existing LHM adapters, source registration, and the supplied host evidence (`docker.sock` root:docker 0660; sourceworker deliberately lacks Docker membership). Selected a root-owned fixed-command helper reached through a no-argument sudo rule. Rejected Docker-group membership, general Docker sudo, shells, arbitrary commands, new authentication, third-party plugins, and custom network integrations.

## 2. Platform Engineer — completed

Added the root-owned helper and minimal sudoers asset; fixed adapters to `/usr/bin/sudo -n /usr/local/libexec/lhm-evidence-fathom-backend`; independently enforced exact JSON fields, positive numeric recording ID, bounded run ID, root-owned non-writable matching registration, and fixed Docker/Hermes argv. Updated installer, static preflight, numeric identifier schemas/workflow, rollback inventory, validator, fixtures, and executable tests. Installer validates policy with `visudo` and never enables or starts the path.

## 3. QA Tester — pass

`PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests` passed 54 tests. Coverage includes registered request/argv, unregistered and mismatched registration, extra fields, string/boolean/zero recording IDs, unsafe run IDs, helper arguments, exact non-recursive adapter configuration, minimal policy, installer policy validation, and the complete prior suite. `validate_system_ops.py` and `git diff --check` passed. Root ownership, sudo execution, and Docker itself are represented by executable fixtures/static assertions because this lane cannot mutate the host or use root.

## 4. Security/Reliability Reviewer — approved

The sudoers command uses the empty-argument marker and grants only the helper, not Docker or a shell. The helper repeats registration enforcement after privilege transition, accepts no argv, uses no shell, suppresses backend stderr, and constructs the sole Docker argv from a validated integer. Registration must be root-owned and not group/world-writable. Rollback restores or removes exactly the helper and policy while retaining registrations/evidence. Residual risk is limited to the separately approved install/live test of the host's sudo and Docker behavior.

## 5. Plugin Release Manager — ready for bounded publisher

Branch name and persisted scope are valid. Plugin/marketplace versions remain in parity; no dependency or credential was added. The bounded root publisher, outside this lane, may reconcile these files, commit/push only the generated `cto/*` branch, remotely verify it, and write Michael's review note. Publication does not authorize merge, release, installation, path enablement, or deployment.
