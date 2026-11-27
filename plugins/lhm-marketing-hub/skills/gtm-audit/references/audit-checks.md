# Audit checks and decisions

Use public resources as static evidence and Preview/received hits for runtime claims. Consult current primary documentation where product behaviour matters; UI labels and Google tag packaging can change.

## 1. Ads conversion linking

Find standalone Conversion Linker tags, all-page Google/destination tags and relevant Ads destination association. A missing standalone linker is not automatically a defect: current [Google guidance](https://support.google.com/tagmanager/answer/7549390) allows appropriate all-page Google/destination tagging to supply linking. Check landing-page coverage, effective consent and authorised ad-click identifier persistence. An `_gcl_au` component in `_gl` alone does not prove `gclid` capture or successful Ads matching.

If no equivalent linking exists, the supported GTM route is Tags → New → Conversion Linker → All Pages → Save → Preview. Verify before publishing. Explain lost ad-click association as a risk, not a measured loss unless reporting proves it. Do not add another base tag/linker solely to silence a warning.

## 2. Universal Analytics

Identify active UA tags/settings variables and runtime `analytics.js` loading; an ID in paused code is not active collection. UA is retired ([Google migration documentation](https://support.google.com/analytics/answer/11583528)). Inspect dependencies, sequencing, cross-domain auto-link domains, allowLinker, cookie domain, form decoration and any legacy event collection bridge. Recreate still-required measurement intent in GA4; UA's `allowLinker` is not the GA4 domain configuration.

After replacement validation, pause the specific UA tag in GTM, Preview website/provider journeys and publish the scoped change. Delete unused variables only after reference checks. Keep the baseline version for rollback; do not disable GA4 or Ads tags that merely have similar names.

## 3. Cross-domain handoff

Follow [Google cross-domain setup](https://support.google.com/analytics/answer/10071811): GA4 Admin → Data streams → intended Web stream → Configure tag settings → Configure your domains. Verify the same measurement ID on each domain and the actual booking host, including redirects. Prefer precise verified hostname conditions; don't add all domains belonging to a provider without need. For an upgraded Google tag container, these settings may be workspace changes requiring separate publication.

Click the real link, including new-tab paths, and inspect the destination URL. UA `_ga` decoration is not GA4 `_gl`. No `_gl` at source is different from a redirect stripping it; inspect the first navigation and redirect chain where possible. Arrival with `_gl` passes decoration/survival only; compare received client/session IDs for continuity when available. Referral exclusion suppresses referrals but does not stitch sessions. Provider consent and iframe cookie constraints may affect loading; don't prescribe third-party cookie flags without demonstrating need.

## 4. Event source and counting

Trace GTM event tags, Custom HTML/listeners, provider integration, GA4 created/modified rules and any observed server-side sender. The answer may be “GA4 creates it from a GTM-sent pageview”, rather than either GTM or a provider's native event. Public Google tag configuration can expose [GA4 event-creation rules](https://support.google.com/analytics/answer/10085872) absent from GTM exports. Inspect operators, parameter names, actual received parameters and event modifications before changing a suspicious-looking rule.

Separate click, submit attempt, accepted enquiry and confirmed booking. Inspect history-based pageviews and confirmation reloads; once-per-event GTM firing is not once per appointment. GA4 once-per-session key-event counting limits counted key events, not raw event creation or duplicates across sessions, and may undercount multiple legitimate bookings. Equal aggregate pageview/event counts support a source hypothesis but do not prove unique bookings. Don't add a second event or arbitrary transaction-ID deduplication when the provider supplies no reliable identifier. Never use patient details as deduplication parameters.

For Cliniko, verify the actual integration and its consent gate using [Cliniko's tracking guidance](https://help.cliniko.com/en/collections/107746-marketing-tracking); don't assume a native `new_booking` event or hardcode a confirmation path from another clinic. Keep provider-specific tests free of real patient information.

## 5. Calls versus clicks

Check [Google website-call setup](https://support.google.com/google-ads/answer/6095883). Verify displayed number formatting, conversion ID/label against the intended Ads action, site-wide Google tag association and the page trigger. Number replacement needs initialisation before a click; changing the website-call tag to fire on phone clicks can break it. “Fired” does not prove forwarding-number allocation, a connected call or Ads attribution. Use supported diagnostics; don't purchase an ad click or place a live call without authorisation.

A separate GA4 phone-click tag should inspect Click URL on the link event, not Page URL. Preview should show one intended event to the correct stream. Preserve the intended number scope; don't silently expand a single-number trigger to every tel: link. Swapped forwarding-number URLs can also affect exact-match click conditions: test the relevant DNI case before changing the matching strategy.

## 6. Consent and duplicate triggers

Inspect Tag Assistant's default/update timeline, CMP behaviour and provider cookie gates. A GTM additional-consent status of `notSet` is not the effective consent state. An empty default consent state is a documented configuration gap, not enough evidence to choose granted/denied values or a geographic consent policy. Confirm requirements before consent changes; don't bypass provider consent to make tests fire. Use [Google Consent Mode guidance](https://developers.google.com/tag-platform/security/guides/consent) for the implementation selected.

Check base tag installations and actual requests, not only IDs present in source. Different event names for the same action can also inflate totals, including separate Ads imports. Form-submit plus thank-you triggers create a duplicate risk but should not be pruned until a supported success signal is validated. Text-only booking triggers can match unrelated UI; destination-link filters are a supported correction when false matches or missing legitimate links are evidenced. Unused triggers aren't causing runtime errors by themselves. Respect paused base pixels and existing sequencing; an image pixel doesn't initialise a JavaScript event API.

## Report format

For each of the six headings: verdict; concrete evidence/version/source; impact; observed versus untested behaviour; exact supported fix steps; validation result or missing evidence. Include the audit date and tested pages. For implementation add before/after entities, published release links, rollback and next owner/action for every outstanding dependency. Redact preview auth values and personal URL/query content.
