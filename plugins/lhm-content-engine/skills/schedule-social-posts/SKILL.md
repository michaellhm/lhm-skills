---
name: schedule-social-posts
description: "Schedule approved Local Health Marketing feed carousels and Instagram Story sequences through the protected LHM Social GoHighLevel API, with duplicate prevention, exact media-order checks and durable receipts. Use when Michael says a social post is approved, asks to schedule approved LHM posts, says 'push the posts', or wants approved carousel or Story packages added to the LHM GoHighLevel Social Planner. Do not use for creating content, unapproved drafts or browser-based scheduling."
---

# Schedule Social Posts

Schedule an already approved LHM Social package through the protected API at `https://lhm-social.pages.dev`. That backend performs the GoHighLevel uploads, creates the post, preserves duplicate locks and reads the result back. Do not use the GoHighLevel browser composer for the normal workflow.

The API is the canonical scheduling path after approval. The LHM Social review page is for reviewing artefacts and reporting delivery status; do not reintroduce feed scheduling controls there.

## Required context

1. Read [GoHighLevel scheduling](references/ghl-scheduling.md).
2. Read this skill's `LEARNED.md`.
3. Read the package `manifest.json`, `caption.md`, optional `first-comment.md`, and `publish.json` from the verified `lhmorg/lhm-social` checkout.
4. For a feed post, read every `slide-NN.png` in manifest order. For a Story, read `story-manifest.json` and every file in `export_files` order.
5. Treat `source-receipt.private.json`, planning files and other private metadata as non-uploadable.

## Approval boundary

An explicit statement from Michael that the named posts or current reviewed set are approved authorises scheduling those exact immutable artefacts to the verified LHM accounts. It does not authorise editing copy, substituting media, changing account permissions, posting to another business, or publishing additional packages.

Resolve before mutation:

- exact package slug or unambiguous title;
- Facebook, Instagram, or both;
- publish now or a future Melbourne date and time;
- whether a supplied first comment should be included.

When Michael explicitly allows random days or times, choose future Melbourne times with meaningful separation and record them before scheduling. Do not silently randomise without that instruction.

The API's approval nonce is a technical control, not user consent. Create it only after Michael has explicitly approved the exact immutable package, platforms and Melbourne time. Never reuse approval from a different revision or infer social publishing approval from content-production approval.

## Preflight

1. Work from a clean, current checkout of `lhmorg/lhm-social`. Verify the origin before reading packages.
2. Require `publish.json.status` to be exactly `approved`. Confirm the caption, comment and ordered media still match the reviewed package.
3. Validate image count and dimensions:
   - feed carousel: 2-10 PNG slides, normally 1080 x 1350;
   - Instagram Story: one 1080 x 1920 PNG per frame.
4. Calculate or read stable hashes for the ordered media and public copy.
5. Build and deploy the current approved package so it exists in the protected `/scheduling-catalogue.json`; the catalogue revision is the immutable API identity.
6. Inspect the private scheduling receipt and call `/api/status` for the package. Any existing attempt is a durable duplicate lock. A matching verified record is success, not a reason to recreate it. A failed, creating, uploading, verification-pending or outcome-unknown attempt requires inspection, not a second create.
7. Call `/api/setup` and require `enabled: true` plus the exact configured LHM platforms.

## Schedule through the API

Use `node scripts/schedule_via_api.mjs <input.json>`. The script calls only the protected LHM Social API and never receives the GoHighLevel private-integration token. It reads the LHM Social shared login from `LHM_SOCIAL_API_USERNAME` and `LHM_SOCIAL_API_PASSWORD`; obtain those values from the approved secret store at runtime and never write, print, commit or pass them as command-line arguments.

The input must bind the approved intent:

```json
{
  "base_url": "https://lhm-social.pages.dev",
  "package_id": "2026/10/2026-10-16-two-minute-ai-service-page-test",
  "revision": "catalogue revision",
  "platforms": ["facebook", "instagram"],
  "local_time": "2026-10-25T10:43",
  "approved": true
}
```

Use a future Melbourne time at least five minutes away. Immediate feed publication is not supported by this API contract. Stop and report that limitation rather than opening the browser composer.

### Feed carousel

1. Pass the exact package ID and current catalogue revision.
2. Pass only the approved `facebook`, `instagram`, or both platform values.
3. Pass the approved Melbourne wall-clock time without a timezone suffix. The server resolves daylight saving.
4. Require `approved: true` only after the approval boundary above is satisfied.
5. Run the script once. It checks setup, catalogue identity and existing attempts before requesting a single-use nonce, then schedules exactly once.

### Instagram Story sequence

1. Use the sequence package ID generated in the catalogue and the `instagram` platform unless the verified backend contract explicitly supports the approved Facebook sequence.
2. The API schedules each frame as a separate Story in manifest order, one minute apart from the approved start time.
3. Do not add a caption, first comment, music, poll or sticker artwork unless the backend and package contract are separately updated and approved.
4. Verify every child attempt independently. If one attempt fails or becomes ambiguous, do not recreate the sequence.

## Verification and receipt

The script reads the result back through the API after scheduling and makes at most one verification call for a known pending post ID. Verify:

- correct LHM account and platform;
- `scheduled` or `published` state;
- exact Melbourne time;
- feed media count and visible order, or every Story child frame in order;
- caption and approved first comment where applicable.

Treat `scheduled_verified` and `published_verified` as complete. Treat `verification_pending`, `outcome_unknown`, `creating`, `uploading` or `failed` as incomplete. Never rerun scheduling to resolve an incomplete state.

Write or update `scheduling-receipt.private.json` beside the package with the package hash, platforms, Melbourne and UTC times, GHL IDs, verification evidence, operator and status. Keep it out of `dist`, ZIP files and public GitHub Pages output. Commit the private receipt only when the current request or saved workflow authorises repository writes.

After GHL verification, also write the package's public `social-status.json` so the LHM Social review page reflects the outcome. It contains only `status`, `platforms`, `scheduled_for` and a short non-sensitive `note`; never include GHL IDs, account IDs, hashes, operator identities or private provenance. Use `verification-pending` for an ambiguous or incomplete read-back. Treat status writeback as part of scheduling completion, then rebuild and deploy the review site only when the current request authorises those repository changes.

## Stop conditions

Stop without creating or retrying when:

- approval is missing or applies to different copy/media;
- the selected GHL location or account does not match the verified LHM account;
- the package is incomplete or fails dimension/order checks;
- a matching scheduled or published post already exists;
- upload order cannot be confirmed;
- a create result is ambiguous;
- the secure API credentials are unavailable;
- the production API reports scheduling disabled or the approved package is absent from the deployed catalogue;
- the requested action is immediate feed publication, which the current API contract does not support.

Report the exact blocker without opening the browser composer or trying a direct GoHighLevel token.

## Output

Return one JSON object:

```json
{
  "run_result": "scheduled | published | already_exists | verification_pending | blocked",
  "package_id": "...",
  "revision": "...",
  "platforms": ["facebook", "instagram"],
  "scheduled_for_melbourne": "YYYY-MM-DDTHH:mm",
  "attempts": [
    {"platform": "facebook", "state": "scheduled_verified", "ghl_post_id": "..."}
  ],
  "media_order_verified": true,
  "caption_verified": true,
  "first_comment_verified": true,
  "private_receipt_path": "...",
  "public_status_path": "...",
  "next_action": "none | inspect GoHighLevel | configure API credentials"
}
```

Distinguish verified, pending and blocked states precisely. Do not report completion from the HTTP acceptance response alone.
