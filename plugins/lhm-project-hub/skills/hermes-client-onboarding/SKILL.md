---
name: hermes-client-onboarding
description: Create, verify, or repair the machine-readable client preflight Hermes needs before autonomous SEO, Google Ads, GA4, website, Drive, BasicOps, or knowledge work. Use for new-client onboarding, missing client access or identifiers, connector readiness checks, and workflows blocked with client_onboarding_required.
---

# Hermes Client Onboarding

Create one simple client preflight record. Do not call it a capability passport in user-facing language.

## Canonical files

Store both files in the Obsidian vault:

- `_System/Hermes/clients/<client-id>/capabilities.json` — canonical machine record.
- `_System/Hermes/clients/<client-id>/onboarding.md` — readable summary generated from the JSON.

Use a stable lowercase client ID containing only letters, numbers, and hyphens. Never store credentials, tokens, cookies, private keys, or secret values.

## Workflow

1. Identify the client unambiguously. Stop if the name maps to multiple records.
2. Find the canonical JSON. If absent, run `scripts/client_capabilities.py init` and complete onboarding before specialist dispatch.
3. Read `references/client-capabilities-schema.md` and mark capabilities required by the requested workflow.
4. Record identifiers, governed route, allowed operations, and owner. Do not invent missing values.
5. Test each required capability at its real boundary. Prefer a small read-only smoke test before the orchestration loop.
6. Record dated evidence in `last_test`, including its exact SHA-256. Search Console evidence must structurally contain the exact property and read capability, and its required explicit binding must match the client, property, read capability, and allowed operations defined in the schema reference. Configuration alone is not verification.
7. Run `scripts/client_capabilities.py check --require ...`.
8. Run `scripts/client_capabilities.py render` to update the readable note.

## Preflight rule

Before Research or another specialist starts, require the JSON and check every capability needed by the workflow.

- If every required capability is `verified`, continue only within its `allowed_operations`.
- If the file is absent, a capability is absent, or its status is not `verified`, stop with `client_onboarding_required` and route to this skill.
- Research may report the gap but must not invent identifiers, broaden permissions, or bypass onboarding.

## Failure routing

- Missing client access or identifiers: return to the onboarding owner.
- Broken connector or host integration: escalate a bounded diagnostic to `lhm_cto`.
- New consequential permission or mutation authority: stop for Michael.
- Evidence mismatch after work: return to Production and Verifier.

This skill fixes readiness. It does not perform the client's specialist work.
