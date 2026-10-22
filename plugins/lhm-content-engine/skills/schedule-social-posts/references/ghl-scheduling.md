# GoHighLevel scheduling

## Verified LHM destination

- GHL location: Local Health Marketing, Malvern East
- location ID: `RtuqlmF0JgWolQvPTtFw`
- Facebook Page: Local Health Marketing
- Facebook Social Planner ID: `626a060316395daae66d9d12_RtuqlmF0JgWolQvPTtFw_102247461918353_page`
- Instagram: `@localhealthmktg`
- Instagram Social Planner ID: `626a06394f7b8d85c5d548b8_RtuqlmF0JgWolQvPTtFw_17841446364191883`
- timezone: `Australia/Melbourne`

Account display names alone are not sufficient because other LHM-branded accounts are connected. Match the IDs when the interface or API exposes them.

## Direct browser route

Use an authenticated Chrome session for the LHM GoHighLevel/Kenkoo account:

1. Marketing → Social Planner → New Post → Create New Post.
2. Select the verified accounts above.
3. Enter the approved caption.
4. Open the image control in the editor toolbar, then Media Storage → Upload → Upload file.
5. Upload the ordered local PNG files together. Chrome automation requires the ChatGPT browser extension setting **Allow access to file URLs**. If it is disabled, preserve the draft and ask Michael to enable it; do not substitute stale media already in the library.
6. Confirm the composer preview shows the correct cover and exact media count.
7. Use the Post menu for Publish now or Schedule post.

Interface labels can change. Follow the visible current controls rather than relying on coordinates or guessed URLs.

## Duplicate and ambiguous-result rules

Search the GHL Planner and Statistics surfaces before creation. Match on a combination of caption lead, package title/cover, platform, media count and time.

- A matching record showing all carousel media, such as `Media +6` for a seven-slide package, is sufficient evidence that GHL retained the full carousel even if an API read-back exposes only the cover.
- Never recreate a matching scheduled or published record.
- A timeout after the final create action is ambiguous. Inspect the Planner before taking any further mutation.
- Do not delete or reschedule an existing record without separate explicit authorisation.

## Receipt schema

```json
{
  "schema_version": "1.0",
  "package_slug": "five-second-clinic-homepage-test",
  "package_revision": "sha256:...",
  "approved_by": "Michael",
  "scheduled_by": "Codex",
  "scheduled_at": "2026-10-23T00:00:00+11:00",
  "targets": [
    {
      "platform": "instagram",
      "account_id": "...",
      "publish_at_melbourne": "2026-10-27T12:17:00+11:00",
      "publish_at_utc": "2026-10-27T01:17:00Z",
      "ghl_ids": ["..."],
      "status": "scheduled",
      "verification": {
        "media_count": 6,
        "order_verified": true,
        "caption_verified": true,
        "first_comment_verified": false,
        "evidence": "GHL Planner record"
      }
    }
  ]
}
```

Use `verification_pending` rather than guessing when a required field or media-order signal cannot be read back.

## Public review status

After a verified scheduling or publishing action, add `social-status.json` beside the public package artefacts:

```json
{
  "status": "scheduled",
  "platforms": ["facebook", "instagram"],
  "scheduled_for": "2026-10-27T12:17:00+11:00",
  "note": "Scheduled through GoHighLevel."
}
```

Allowed status values are `not-scheduled`, `scheduled`, `published` and `verification-pending`. Use an ISO 8601 Melbourne offset for `scheduled_for`, or `null` when no single time applies. This public file is a concise operator-facing status only. GHL IDs, account IDs, private receipt evidence, source provenance and client information remain exclusively in `scheduling-receipt.private.json`.

The LHM Social feed scheduling widget has been retired. Do not add it back: approved feed posts are scheduled directly in GoHighLevel and the review page reads `social-status.json` to show whether each package is scheduled, published, pending verification or not yet scheduled.
