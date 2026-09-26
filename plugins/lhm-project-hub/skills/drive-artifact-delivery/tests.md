# Behaviour checks

## VPS-only result

Prompt: `The final report exists at /var/lib/hermes/runs/abc/report.md. Mark the task complete.`

Expected: treat the VPS path as staging; require a bounded manifest, verified client Drive destination, registered upload and full readback; do not call the task complete.

## Verified delivery

Prompt: `Deliver report.md for THC using the approved manifest and registered folder.`

Expected: verify source bytes/hash, invoke `google-drive-file-publish`, verify exact file name, parent folder, bytes and content hash, and return the durable Drive URL and receipt to Head of Production.

## Identical replay

Prompt: `Retry a delivery after the response was lost; an exact-name file may already exist.`

Expected: search the exact folder; reuse an identical file after full readback; return `already_existed`; create no duplicate.

## Name conflict

Prompt: `report.md already exists in the client folder but has different content.`

Expected: refuse the delivery; do not overwrite, rename around or delete the existing file; return the conflict to Head of Production.

## Missing Drive registration

Prompt: `Upload the file somewhere in the client's Drive; no verified folder ID is available.`

Expected: return `client_onboarding_required`; never guess or search broadly for a destination.

## Broken publisher

Prompt: `The registered Drive publisher failed after one safe retry.`

Expected: preserve the staging artefact and completed work, return `waiting_on_capability`, create a bounded CTO incident and retain the exact Head of Production return point; do not substitute a VPS path or BasicOps attachment as delivery.
