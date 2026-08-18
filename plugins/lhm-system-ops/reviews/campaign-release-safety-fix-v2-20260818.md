# Campaign release safety correction v2

Parent: `campaign-playbook-flow-20260818-01`  
Incident: `campaign-release-safety-fix-v2-20260818`  
Return point: `head_of_production.release_and_live_test`

This record covers repository-only iteration 2. Nothing was installed, enabled, deployed, committed, pushed, or exercised against live connectors.

## Pass 1 — Capability Researcher

Selected existing native capabilities from the verified evidence: Claude 2.1.232 with the installed `lhm-marketing-hub` `content` agent, the authenticated Google Drive repair HOME, and Hermes `lhm_brain` one-shot mode with `fathom-meeting-lookup`. Rejected the invalid Hermes `mcp call` assumption and any new OAuth owner, copied credential, third party, or shared-gateway patch.

## Pass 2 — Platform Engineer

Replaced the shared-gateway release assets with additive `lhm-evidence-claude-dispatcher`, `lhm-evidence-claude-worker`, and `lhm-evidence-fathom-backend` assets. The four adapter routes translate actions directly to these backends and reject adapter recursion. Fathom uses `/usr/bin/docker exec -i -u hermes hermes /opt/hermes/.venv/bin/hermes -p lhm_brain -z ... --skills fathom-meeting-lookup`. Claude production maps the external agent id to `--agent content`; Drive stays in `/home/claudeworker-repair` with profile-minimum tool allowlists.

## Pass 3 — QA Tester

Added assertions for immutable shared paths and supplied hashes, additive executable names, disabled path state, numeric Fathom identifiers, non-recursive backend configuration, host/container path separation, Claude result-envelope extraction, and exact rollback controls. Result: `45 passed`; `validate_system_ops.py` reports 10 valid skills; shell syntax and `git diff --check` pass.

## Pass 4 — Security/Reliability Reviewer

Confirmed the installer never has an install destination at `/usr/local/libexec/lhm-claude-dispatcher` or `/usr/local/libexec/lhm-claude-worker`; both paths are verified before and after install by hash, owner/group, mode, and size. Backend stderr is suppressed, result parsing fails closed, Drive profiles preserve the authenticated HOME, production has an empty tool allowlist, Fathom requires one exact tool and JSON shape, static preflight does not confuse host and container paths, and rollback excludes shared gateways, profiles, credentials, registrations, sourceworker, and run evidence.

## Pass 5 — Plugin Release Manager

The corrective branch workspace is release-candidate ready but unpublished. The release guide now requires the exact additive argv mapping, pre-install inventory, separate container/authenticated smoke, shared-hash checks after install and rollback, and exact restore-or-remove semantics. The systemd path remains disabled pending separate human preflight and enablement authority. The root-owned bounded publisher remains responsible for commit, push, and remote verification; publication is not restoration or deployment approval.
