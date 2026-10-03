# Conversion tracking investigation and GTM imports

## 1. Establish access and current evidence

Record website and form/booking domains, GA4 property/stream/measurement ID, GTM account/container/workspace and live version, and Ads account/action IDs. Verify the mapping rather than inferring it from similar names. Inspect workspace changes separately from the published container; save a baseline export and relevant settings for rollback. Record the date range and source of counts. Keep reported figures, observed evidence and hypotheses separate. If access is missing, identify the exact permission, container export, event report or conversion-action settings required.

## 2. Find the event source

Inspect website code, the form provider, embeds/iframes, redirects and success behaviour without sending an enquiry. For each event, determine whether it comes from GA4 enhanced measurement, a GTM tag, website code or the embedded provider. A parent-page GTM exception cannot suppress an event generated independently inside a cross-origin iframe. Do not assume the enquiry provider and booking provider are the same.

Compare event hostname/page, counts and success signals. Similar booking and form-submit totals suggest duplication but do not prove it. Check whether form_submit has legitimate enquiry use on other pages before changing collection. Disabling GA4 automatic form interactions may affect form_start as well as form_submit across the stream; state that scope and propose explicit success tracking where needed. Collection changes do not remove historical events or change Ads conversion settings.

## 3. Prepare the smallest supported correction

Track confirmed success: server acceptance, a documented provider callback, or a verified success message/event. A button click, form start or submit attempt is insufficient. A thank-you page can count direct visits and refreshes; use it only with a supported success/deduplication mechanism or an explicitly accepted limitation. For third-party forms, inspect an agreed test or documented callback before inventing a trigger. Validate postMessage origin and payload if used; never trust arbitrary iframe messages.

Send one enquiry event per successful enquiry within the existing browser session before redirect where possible. Use the existing consent-aware Google tag and intended stream. Retain safe page/referrer and campaign/session context; strip personal or sensitive query values. Do not send names, email addresses, phone numbers, patient details or form answers. Do not fabricate source/medium or start a new session to fill missing attribution. Keep booking success separate from enquiry success and preserve existing meaningful event names.

Verify the event's specific GA4 destination and Ads path separately. Inspect whether an Ads import/action already exists, which event/property it uses, its status, count setting, Primary/Secondary setting, campaign goals and custom goals. GA4 receipt does not establish Ads receipt. If duplication is supported, assess making the redundant action Secondary while preserving genuine booking conversion; check custom goals which can still use Secondary actions for bidding. Use the Ads audit/implementation skills for this assessment and execution.

Show the exact tags, triggers, variables, files and account settings affected, expected result and rollback before requesting approval. Require authorization before publishing website/GTM changes, changing Ads settings or submitting a live enquiry. Coordinate test submissions with the clinic; do not assume a synthetic enquiry is harmless. Keep other platform tracking work separate unless included in scope.

## 4. Build an import that GTM accepts

Use a fresh native export from the target container as the schema baseline. API responses and import exports are not interchangeable. Preserve the export wrapper, exportFormatVersion, containerVersion structure and native enum casing. A verified successful web import used `"usageContext": ["WEB"]`; lowercase `web` was rejected with `Error deserializing enum type [UsageContext]. Unrecognized value [web]`. Validate other enum values against the baseline rather than changing them blindly.

Check JSON syntax, tag/trigger/variable references, IDs, destination values, hostname scope and a small merge diff. Select a merge option that avoids overwriting unrelated entities. Inspect the resulting workspace additions and conflicts. A parsed file is not an accepted import; an accepted import is not a published or tested implementation. Keep container exports and working examples in client work records, with no client identifiers copied into cross-client skill instructions.

## 5. Test and hand back

After authorized implementation, verify that failed/abandoned submissions do not count, successful enquiries emit once, and refresh/repeated UI signals do not duplicate. Use GTM Preview/Tag Assistant and GA4 DebugView or request evidence when these are unavailable. Confirm the intended property, safe page context and retained session/campaign attribution. Confirm the specific Ads action/source and account goal settings without treating ordinary import/reporting delay as immediate failure or proof of success. Confirm booking success still counts once as a primary conversion and no redundant primary action counts the same booking.

Provide evidence, changed entities/settings/files, rollback, remaining dependencies and next owner in a short handback. Close tracking as fixed only after the relevant end-to-end checks pass. If the user explicitly closes an administrative task after handoff, record that decision and the open verification work separately; do not turn task closure into a claim that tests passed.
