---
name: gtm-audit
description: Audit Google Tag Manager, GA4 and Google Ads tracking using GTM MCP and runtime evidence. Use when the user asks for a "GTM audit", "audit my container", "Tag Assistant review", "cross-domain tracking check", "Cliniko tracking audit", or investigation of duplicate or missing booking, enquiry and phone conversions. Supports authorised fixes and publication; route Ads bidding/goal changes to google-ads-conversion-audit and google-ads-implementation.
---

# GTM Audit

Audit the implementation that is actually published, identify the source of each conversion, and distinguish configured behaviour, observed firing, received events, attribution and unique business outcomes. Audit is read-only unless implementation is authorised in the current session. Existing explicit authorisation persists; do not ask again merely to save or publish the scoped, validated changes.

## Context and access

For client work, read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Load the verified client overview/profile, goals and affected project records. Keep client identifiers and raw evidence in that client's work folder, never in this reusable skill. For non-client work use the requested destination.

Record the website, booking/form provider and actual destination hostnames, public GTM ID, GTM account/container/workspace IDs, published version, GA4 property/web stream/measurement ID and relevant Ads conversion IDs/labels. Verify mappings; account names alone are insufficient. Ask only for missing inputs that block useful work. If promised Preview output was not pasted, say so and continue with available evidence.

**Use the GTM MCP first.** Discover the available tool schemas at runtime; namespace spelling varies. Verify access with account/container listing and live-version reads, then inspect workspace status separately. Do not assume the MCP can preview, publish, pause tags or update Google tag settings merely because it can read a container.

If GTM MCP tools are absent, explicitly recommend installing/connecting a GTM MCP in that user's local AI client and completing Google authentication. Read [MCP setup and fallback](references/mcp-setup.md) for the supported provider link and setup options. Do not silently skip this suggestion, automatically install a server, request secrets in chat or treat installation as required for a partial public audit. If tools exist but authentication/permissions fail, explain that specific gap rather than recommending a reinstall.

Use authenticated GA4/Ads connectors for supported reads. When the required setting or operation is unavailable or a connector fails, continue through the host's supported browser controls. Open the relevant service and offer login handoff if needed; never bypass a denial. Otherwise request a native container export, exact setting screenshot or Preview evidence and label inaccessible checks UNSURE. A public container response cannot establish account permissions, unpublished changes or actual event delivery.

## Evidence collection

1. Save the live container baseline, version metadata and workspace status before edits. Preserve unrelated workspace changes; use a separate workspace when necessary. API snapshots support comparison/rollback but are not automatically valid UI import exports.
2. Inspect website installation and the public `gtm.js?id=<verified-id>` resource, tags, triggers, variables, paused state, exceptions and sequencing. Identify hardcoded/plugin tags and provider installations as well as GTM. Do not count GTM's noscript iframe, a normal Google tag child script or debug bootstrap as independent duplicate installations.
3. Inspect the GA4 web stream, Google tag settings and served `gtag/js?id=<verified-id>` configuration where useful. Domain settings and GA4-created/modified events may be absent from the web GTM container. Google may expose tag settings through a separate upgraded Google tag container: verify its destination ID and record its own workspace/version before changing it.
4. Use Preview/Tag Assistant on representative landing, contact, booking and confirmation journeys, plus GA4 DebugView or received-hit evidence when available. Keep successful tests distinct from planned tests. Do not submit a real booking, enquiry or call without specific authorisation/coordinated test arrangements.

Read [Audit checks and decisions](references/audit-checks.md) when assessing the six areas below. Verify current technical guidance against linked primary sources before recommending a change whose behaviour or UI may have changed.

## Required findings

Give each area its own heading and one **PASS / FIX / UNSURE**, scoped to what was actually checked:

1. **Google Ads conversion linking:** standalone linker, equivalent Google/destination tag, page coverage, click persistence and destination association.
2. **Legacy Universal Analytics:** active loading, dependencies and GA4 replacement of still-needed cross-domain behaviour before retirement.
3. **GA4 cross-domain measurement:** same stream across domains, configured hostnames, actual click decoration and `_gl` survival; client/session continuity where observable.
4. **Booking/event origin and counting:** GTM versus GA4 rules versus provider code, repeated success-page views, event and key-event counting, duplicate paths.
5. **Website calls and phone clicks:** replacement number/ID/label, page-load firing, forwarding-number diagnostics and click-trigger correctness, assessed separately.
6. **Consent, duplicates and trigger correctness:** effective consent timeline, additional-consent settings, success versus attempt signals, duplicate base/event tags and incorrect conditions.

For each, include evidence with its source/version and observation date, practical impact, limits, and exact current UI steps for supported fixes. PASS requires relevant evidence; a tag firing can pass a firing check while attribution remains UNSURE. FIX requires a demonstrated defect. Label conditional actions as conditional; don't propose removing a working rule solely because it looks unusual.

## Authorised implementation

- Read the existing [conversion investigation checklist](../analytics-tracking/references/conversion-investigation.md) for form/booking success changes or GTM imports. Use `google-ads-conversion-audit` for Ads goal/Primary/Secondary decisions and `google-ads-implementation` for Ads account changes; a GTM fix alone does not authorise those changes.
- Prepare the exact scoped diff, expected behaviour and rollback against a fresh baseline. Obtain any missing authorisation only after the proposal is concrete. An audit request alone does not authorise live changes. If the user already requested implementation/publication, proceed within that scope.
- Change the smallest supported set. Keep event names and destinations unless evidence calls for changing them. Preserve a working GA4-created booking event instead of adding a second GTM event. Retire UA reversibly after GA4 replacement is verified; identify whether it was paused or deleted.
- Read back every mutation. Some MCP wrappers mis-serialize conditions or partially update entities. On a schema error, inspect the actual workspace state before retrying; use a supported browser fallback rather than repeatedly guessing payloads. Never turn a permission failure into an elevated or indirect bypass.
- Preview before publishing where supported: valid click/success sends once; irrelevant click and failed/abandoned submission send no success; inspect reload/repeat behaviour. Validate website and consented provider pages. Never fabricate a production success event, confirmation URL or patient data to make a test pass. Where a real success test is unavailable, leave it explicitly outstanding.
- Inspect the final workspace diff, conflicts and destination scope. Publish only the authorised changes; separately publish an upgraded Google tag settings container if needed. Verify published version(s) through the service and public resources, then perform the relevant runtime retest. Watch for older cached tabs and Preview/live differences rather than claiming universal cache eviction.

## Deliverables and handback

Save `audit.md`, `evidence/` and, if implementing, `implementation-log.md` under the verified work root's `gtm-audit/YYYY-MM/`. Keep preview authentication URLs, credentials, personal form data and patient details out of shared reports. Store redacted request/event evidence, scoped before/after snapshots and exact release/rollback references.

Report the six verdicts, implemented versus proposed changes, verified runtime results, published version links, rollback and unresolved checks with next owner/action. Do not call the whole implementation fixed when call attribution, booking uniqueness or form success remains untested. Update the affected canonical client knowledge record with concise evidenced facts and the deliverable link. Distinguish saved, previewed and published states.
