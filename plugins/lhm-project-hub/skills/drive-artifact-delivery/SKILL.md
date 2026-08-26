---
name: drive-artifact-delivery
description: Deliver completed LHM production artefacts from an approved worker staging location into the client’s registered Google Drive folder with exact metadata and content readback. Use whenever a Hermes, Claude or Codex workflow produces a report, brief, copy deck, audit, plan, export or other file that must be retained for a client; when Head of Production reaches durable delivery; or when a result exists only on a VPS, local path, Hermes workspace or Kanban attachment. This is a shared delivery capability, not a specialist content or publishing bot.
---

# Drive Artefact Delivery

Convert verified staging output into a durable client deliverable. Operate beneath Head of Production through the registered `google-drive-file-publish` route. Do not create or revise the specialist content.

Read `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before delivery.

## Required input contract

Accept only a bounded delivery manifest containing:

- parent and child run IDs;
- client ID;
- verified registered Drive folder ID;
- source artefact path inside the registered worker output boundary;
- intended file name and media type;
- source byte count and SHA-256;
- artefact purpose and whether delivery is required;
- producer receipt and QA disposition;
- permission ceiling, accountable reviewer and return point.

Reject arbitrary paths, unresolved folders, missing hashes, unverified producer output and files outside the registered worker boundary. Never accept credentials or a Drive folder guessed from a client name.

If a durable file is genuinely unnecessary, return `artefact_state: not_required` with the approved plan reason. Do not use `not_required` merely because upload is inconvenient or the Drive route is unavailable.

## Preflight

1. Read `_System/Hermes/clients/<client-id>/capabilities.json` and require `google_drive.status: verified`, the `file_create` and `file_readback` operations, and an exact folder ID.
2. Re-read the staging artefact and verify its byte count and SHA-256 against the manifest.
3. Confirm the producer and QA receipts belong to the same parent, child and artefact digest.
4. Preserve the source file. Delivery does not authorise deletion, renaming or mutation of staging output.

If the client destination is absent or unverified, return `client_onboarding_required`. If the registered publisher, authentication, transport or readback capability is broken, return `waiting_on_capability` to Head of Production with the exact return point and route a bounded incident to CTO.

## Publish and verify

Invoke only the registered `google-drive-file-publish` route.

Inside the exact registered folder:

1. Search for the exact intended file name.
2. If an identical file already exists, reuse it after full verification; do not duplicate it.
3. If a different file has the same name, refuse and return the conflict. Never overwrite it silently.
4. Otherwise create the file.
5. Read back file metadata and content.
6. Verify file ID, file name, parent folder ID, byte count and content SHA-256 against the manifest.

This skill may create or reuse the bounded file only. It may not share, move, rename, update, overwrite, trash, publish externally or change folder permissions.

## Receipt

Return one machine-readable receipt per artefact containing:

- `run_result`;
- `work_state`;
- `artefact_state: delivered`;
- parent and child run IDs;
- file name, media type and purpose;
- observed Drive file ID and URL;
- observed parent folder ID and folder URL when available;
- source and readback byte counts;
- source and readback SHA-256;
- action: `created` or `already_existed`;
- verification checks;
- approval still required;
- next owner, next action and return point.

Report success only when every expected value matches. A request ID, queued job, successful process exit, local path or worker assertion is not delivery evidence.

For a multi-file package, require a passing receipt for every required manifest item before returning `delivery_complete`. Preserve partial successes and retry only the first incomplete item when the operation is safe and idempotent.

Return receipts to Head of Production for independent final verification and the BasicOps handoff. Do not mark the business task complete.
