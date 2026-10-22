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

## Protected API route

The production entrypoint is `https://lhm-social.pages.dev`. It is protected and forwards approved immutable packages to GoHighLevel with the production private-integration token held only by Cloudflare Pages Functions.

Authentication uses the authorised LHM Social shared login. The scheduling script reads it only from `LHM_SOCIAL_API_USERNAME` and `LHM_SOCIAL_API_PASSWORD`. Never store those values in this skill, the content repository, an automation prompt, a receipt or command history.

The API sequence is:

1. `GET /api/setup` to require live scheduling and the verified configured accounts.
2. `GET /scheduling-catalogue.json` to resolve the exact package and revision.
3. `GET /api/status?packageId=...` to enforce the durable duplicate lock.
4. `POST /api/approval` with the package ID, revision, approved platforms and Melbourne `localTime`. The returned nonce expires after five minutes and is bound to that exact intent.
5. `POST /api/schedule` with the same fields, `approved: true` and the nonce.
6. `GET /api/status` and, only for a known post ID in `verification_pending`, one `POST /api/verify` followed by one final status read.

Every mutation includes `Origin: https://lhm-social.pages.dev`. Requests use `redirect: manual` so credentials are never forwarded to another origin. The script never accepts a base URL other than the production HTTPS origin unless its source is intentionally changed and reviewed.

The catalogue is the approval boundary. It must contain the approved package and its current revision before scheduling. A package present only in the local checkout cannot be scheduled through production.

## Duplicate and ambiguous-result rules

Call `/api/status` before creation. Any existing attempt for the package is a durable duplicate lock and must be handled by status inspection rather than a new create.

- `scheduled_verified` or `published_verified` is success.
- `verification_pending` with a known post ID permits one `/api/verify` call, which performs read-back and never creates another post.
- `outcome_unknown`, `creating`, `uploading`, `failed` or a pending state without a usable post ID requires inspection in GoHighLevel. Never submit another approval or schedule request for that package.
- A timeout or malformed response after `/api/schedule` is ambiguous. Read `/api/status` before any further action.
- Do not delete or reschedule an existing record without separate explicit authorisation.

## Script result

`scripts/schedule_via_api.mjs` returns a sanitised JSON object. It never prints the Basic credentials, approval nonce or GoHighLevel private-integration token. Its completion state is based on the final attempt states, not the create response.

The current contract supports scheduled feed carousels and scheduled Story sequences. Feed times must be at least five minutes in the future. Immediate feed publication is intentionally unsupported.

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
