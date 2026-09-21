# Monday Google Ads digest

The existing weekly Ads flow starts Monday at 04:00 Australia/Melbourne. Preserve the four-week anchor, client selection from the Ads column of canonical Client Flow, sequential Claude research and Codex delivery. This change adds one completion email to Michael using the existing verified Lily Mailgun route. Do not copy the SEO recipients. No client recipients, campaign mutations or test send are implied.

## Report and handback

The research worker includes one to four concise, evidence-backed Highlights and one Start here action near the top of the report. Repeat precisely those statements in this machine-readable block inside the returned report body (not only the surrounding handback):

```ads_digest
{"light":"orange","status_reason":"CPA exceeds the approved target","stage":"Last 30 complete days versus preceding 30 days; measurement confidence: medium","highlights":["Replace this example with a sourced finding and its actual period."],"next_action":"Replace with the first supported action or exact decision."}
```

Allowed `light`: red, orange, yellow, blue, green, unknown. Preserve the mechanical AdPulse zone; operational cautions and measurement confidence stay separate. Yellow must remain Yellow, not be relabelled Orange to match SEO. Unclassified or unavailable evidence uses unknown. Conversion events are not verified patients. Do not invent a metric or a link. No new analysis belongs in the email.

The delivery worker preserves this block in the saved report, puts the human highlights and Start here in the BasicOps Discussion, and verifies report contents, parent folder, card ownership/routing and Discussion. Append exactly one JSON receipt to its final result:

```ads_delivery
{"delivery_status":"complete","client":"registered-slug","verified_drive_url":"https://drive.google.com/file/d/OBSERVED/view","verified_basicops_url":"https://app.basicops.com/WORKSPACE?l=OBSERVED","readback_verified":true}
```

Only emit complete after successful readback. Failure must not contain a success receipt. Reports and supporting files remain linked from the card, not the email.

## Router completion

After every selected client has reached a terminal state, write a JSON manifest at a workspace path with `week` (local Monday YYYY-MM-DD), `selected_clients` (registered slugs) and `clients` (exactly one entry per selected slug). Each entry has `client`, `state` (`complete` or `failed`), and either `delivery_run_id` or a precise `error`. Preserve this manifest and run IDs so an interrupted router resumes rather than recreates deliveries. A failed analysis or delivery stays visible in the digest. Do not mark an unfinished child failed solely to send early.

Invoke the installed `ads-weekly-digest.py preview MANIFEST` to validate and render, then `ads-weekly-digest.py send MANIFEST` once. The script obtains highlights from the frozen report in the matching delivery run, and URLs from its verified receipt. Hermes must not compose highlights or manufacture receipts. Invalid/missing completion evidence becomes an explicit incomplete client section, not a green result. An empty cohort produces no email.

Use `ads-weekly-digest.py status YYYY-MM-DD` to reconcile provider events. Queued is not delivered. A durable send intent blocks automatic re-send after timeout, crash or an uncertain provider response; inspect provider evidence before any human-approved retry. One week means one digest even if the payload changes. Sending is permitted only on that local Monday after 04:00; a delayed run requires explicit review rather than silently sending stale work.

## Presentation and runtime

Reuse the SEO newsletter layout with 🔴 Red, 🟠 Orange, 🟡 Yellow, 🔵 Blue, 🟢 Green or ⚪ Unverified and a text reason. Each successful client has up to four highlights, comparison/confidence context, Start here and one Open review card button. Failed clients have their blocker and no fabricated button. Escape all HTML. Send HTML and plain text through the existing Mailgun helper as Lily, to Michael only, Reply-To Michael. Credentials remain in the existing secret route.

Install the scripts from the published immutable commit, preserve prior router/cron configuration and record hashes. Extend the existing Ads cron rather than creating a duplicate schedule. Dry-run validation must cover all zones, failed clients, unsafe links, missing receipts, cohort mismatches and uncertain-send deduplication. Do not send a sample email unless requested. Rollback restores only the Ads router prompt/skill and prior report skill; preserve send receipts.

## Compatibility and recovery

New reports must emit the five newsletter fields in the example above, rather than substituting a full analytics payload. The reader accepts `ads_digest`, `json ads_digest`, and a `json` object containing an `ads_digest` object. Multiple explicit receipts remain an error. A missing final Markdown fence is accepted only when the entire remaining content is one complete JSON object plus whitespace; truncated JSON or trailing prose is rejected. For historical analytical payloads, it can copy recorded conversion/CPA comparisons, dates, confidence caveats, zone cautions and the first proposed action into a neutral card. It never recalculates the zone, treats events as patients, grants action approval or invents highlights. Missing required evidence remains a visible gap. Recovery reads the original frozen report and verified delivery receipts; do not rewrite reports, repeat delivery or clear send receipts.
