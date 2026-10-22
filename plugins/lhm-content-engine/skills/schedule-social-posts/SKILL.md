---
name: schedule-social-posts
description: "Schedule approved Local Health Marketing feed carousels and Instagram Story sequences directly in GoHighLevel, with duplicate prevention, exact media-order checks and a durable private receipt. Use when Michael says a social post is approved, asks to schedule or publish approved LHM posts, says 'push the posts', or wants approved carousel or Story packages added to the LHM GoHighLevel Social Planner. Do not use for creating content or publishing unapproved drafts."
---

# Schedule Social Posts

Schedule an already approved LHM Social package directly in the Local Health Marketing GoHighLevel Social Planner. Cloudflare and the protected review site are not required for this publishing step.

Direct GoHighLevel scheduling is the canonical path after approval. The LHM Social review page is for reviewing artefacts and reporting delivery status; do not reintroduce feed scheduling controls there.

## Required context

1. Read [GoHighLevel scheduling](references/ghl-scheduling.md).
2. Read the package `manifest.json`, `caption.md`, optional `first-comment.md`, and `publish.json` from the verified `lhmorg/lhm-social` checkout.
3. For a feed post, read every `slide-NN.png` in manifest order. For a Story, read `story-manifest.json` and every file in `export_files` order.
4. Treat `source-receipt.private.json`, planning files and other private metadata as non-uploadable.

## Approval boundary

An explicit statement from Michael that the named posts or current reviewed set are approved authorises scheduling those exact immutable artefacts to the verified LHM accounts. It does not authorise editing copy, substituting media, changing account permissions, posting to another business, or publishing additional packages.

Resolve before mutation:

- exact package slug or unambiguous title;
- Facebook, Instagram, or both;
- publish now or a future Melbourne date and time;
- whether a supplied first comment should be included.

When Michael explicitly allows random days or times, choose future Melbourne times with meaningful separation and record them before scheduling. Do not silently randomise without that instruction.

If the active computer-use environment requires an action-time confirmation for the final Schedule or Post control, obey it. Do not mistake the skill's approval model for permission to bypass tool safety controls.

## Preflight

1. Work from a clean, current checkout of `lhmorg/lhm-social`. Verify the origin before reading packages.
2. Require `publish.json.status` to be exactly `approved`. Confirm the caption, comment and ordered media still match the reviewed package.
3. Validate image count and dimensions:
   - feed carousel: 2-10 PNG slides, normally 1080 x 1350;
   - Instagram Story: one 1080 x 1920 PNG per frame.
4. Calculate or read stable hashes for the ordered media and public copy.
5. Inspect the private scheduling receipt and the GHL Planner for an existing matching package, caption, account and time. A matching scheduled or published record is success, not a reason to recreate it.
6. If an earlier creation result is ambiguous, stop and inspect GHL. Never retry a possibly accepted create request.

## Schedule

Prefer a connected GoHighLevel capability or authenticated direct GHL browser session. Do not route through Cloudflare merely because the package also appears on the review site.

### Feed carousel

1. Select only the verified Local Health Marketing Facebook Page and Instagram account requested by Michael.
2. Set both channel types to Feed.
3. Add `caption.md` without private notes or Markdown headings that are not intended for the public post.
4. Upload slides in manifest order and confirm the composer shows the exact count and cover.
5. Add `first-comment.md` only when it exists, has been approved and the selected platform supports the intended behaviour.
6. Set the Melbourne publish time or choose Publish now as approved.
7. Re-read the accounts, media count/order, caption, first comment and time immediately before the final action.
8. Schedule once.

### Instagram Story sequence

1. Use only `@localhealthmktg` unless Michael explicitly requests another verified account.
2. Set the channel type to Story.
3. Schedule each frame as a separate Story post in manifest order, one minute apart unless Michael specifies otherwise.
4. Do not add a caption, first comment, music, poll or sticker artwork unless separately approved.
5. Verify every frame independently. If one definite failure occurs, stop before creating later frames.

## Verification and receipt

Read the result back from GHL after scheduling. Verify:

- correct LHM account and platform;
- `scheduled` or `published` state;
- exact Melbourne time;
- feed media count and visible order, or every Story child frame in order;
- caption and approved first comment where applicable.

Do not report a carousel as verified when GHL exposes only the cover and gives no second signal for the remaining media. The GHL Planner showing `Media +N` for the matching record is an acceptable second signal.

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
- authentication, file-upload permission or another browser prerequisite requires Michael's action.

Report the exact blocker and preserve any prepared draft without clicking the final Post or Schedule control.

## Output

Return the post title, platforms, Melbourne schedule time, GHL IDs, media-count/order verification, caption/comment status, private receipt path, public status writeback and any remaining delivery check. Distinguish `scheduled`, `published`, `verification_pending` and `blocked` precisely.
