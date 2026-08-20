# Work Resumer Response Schema Review

Incident: `work-resumer-response-schema-20260820`

The native LHM work resumer now generates the one-shot response field list from the same
`AGENT_RESPONSE_FIELDS` contract used by validation. The prompt requires all seven exact fields,
including `parent_sha256`, and interpolates the SHA-256 of the canonical JSON parent copied into
the bounded handoff before Hermes is invoked.

The captured Hermes CLI fixture emits the required digest and exercises a complete successful
transition. Regression coverage rejects a wrong digest without changing the parent. When a Hermes
response is missing or invalid, the resumer writes a root-service-owned mode `0600` failed-audit
diagnostic before removing the mode `0700` ephemeral handoff. Present responses are bound by their
raw-byte SHA-256, byte count, and preserved content; missing responses are recorded explicitly.

This change is limited to the persisted host executable, its non-live regression fixtures, and this
review. It does not invoke live Hermes, alter the work-control store, deploy, publish, or transition
the waiting parent.

## Recorded role passes

1. **Capability Researcher:** Inspected the native Hermes `--in`/one-shot invocation and existing
   LHM handoff, validator, deployment parity, and prior review evidence. The native implementation
   is sufficient; no third-party or custom capability was introduced.
2. **Platform Engineer:** Centralized the response field contract, generated the prompt field list
   from it, computed the canonical handoff parent digest before subprocess invocation, and added the
   private failed-response audit.
3. **QA Tester:** Exercised the captured agent fixture, exact prompt paths and digest, schema parity,
   wrong-digest rejection, missing-response audit, cleanup, idempotency, and exact-once transition.
4. **Security/Reliability Reviewer:** Confirmed fail-closed validation, parent digest comparison,
   unchanged canonical parent on failure, atomic mode `0600` diagnostics, mode `0700` handoff
   isolation, cleanup ordering, and no live-state access.
5. **Plugin Release Manager:** Reviewed the bounded three-file release and clean-tree evidence. No
   commit, push, merge, installation, deployment, or live Hermes invocation was performed.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests/test_work_resumer.py` — 27 passed,
  13 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests` — 110 passed, 32 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed,
  11 skills.
- Python compile validation and `git diff --check` — passed; generated compile bytecode was removed
  from the release tree.
