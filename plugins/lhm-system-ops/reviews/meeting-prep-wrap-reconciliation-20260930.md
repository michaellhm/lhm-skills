# Meeting-prep wrap and knowledge reconciliation

Origin: Michael's 30 September request to check the last meeting-wrap email,
sweep BasicOps for missing work, consult Obsidian, and investigate the reported
Fathom gap. No external business task was specified. Base: merged PR #153,
bcb6928fef1e93baf33e0528eb7e2084fc2fc36c.

## Outcome and scope

System Ops profile assets for `lhm_brain` now require five source categories,
per-client latest-wrap evidence and a per-commitment BasicOps reconciliation.
The six-file installer includes the new source-reconciliation reference.
Source version: System Ops 0.9.105; Lily skill metadata 1.0.4. No additional
desktop skill, agent route, source mutation, recipient or schedule change.
The existing maintainer agent routing entry remains accurate; README asset
catalogue wording updated without changing skill counts.

## Findings and live read acceptance

Read-only verification through the existing server Google helper resolved the
actual meeting-wrap label and returned the same latest client wrap as the Codex
mail connector. The full wrap was read to check that the new instructions cover
its actions and decisions. The shared LHM Knowledge mount and existing client
overview, profile, goals, current-project and service/meeting note paths were
verified. No private-vault fallback, client writes or replacement email.

The scheduled profile logs report OAuthNonInteractiveError for Fathom, including
the recovered run. The connection requires browser reauthorisation; background
jobs cannot perform it. This release documents the operator reconnection and
requires an honest limitation rather than claiming no recordings exist. It
does not change authentication or substitute another session's credentials.
Reconnection remains outstanding and is not claimed fixed by source tests.

## Validation and limits

27 behavioural tests pass, including required wrap/Obsidian coverage, per-client
checks, full-message evidence, targeted search requirements, partial-source
failure, no-match versus unavailable distinction, existing recovery/dedup and
two-recipient verification. Plugin versions, script parity, System Ops validator,
frontmatter and diff whitespace checks pass. All 92 LEARNED files were scanned;
none contained pending entries. No source emails, client records or credentials
are committed. The ledger enforces traceability, not independent semantic truth.
No full unattended research run has been exercised with this candidate.

## Authority, rollout and rollback

Source edits, validation, feature-branch commit/push and review PR are authorised
by Michael's standing preference. Previous PR #153 merge approval applied to
that fix; this new candidate has not yet been approved for merge/installation.
After approval, export the exact candidate and use the existing allowlisted
installer; read back all six hashes, unchanged job fields and enabled schedule.
Use a research-only acceptance check, preserving today's existing send receipt.
Reauthorise Fathom with the account owner's browser consent, then verify a
bounded recording lookup from `lhm_brain`; never equate Codex availability with
scheduled-profile health. Installer metadata and originals provide rollback.
Return completion and any remaining connector limitation to Michael here.
