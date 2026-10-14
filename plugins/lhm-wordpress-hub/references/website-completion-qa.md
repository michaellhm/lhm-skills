# Website completion QA — Jaimee's guided review

Use `site-launch-qa` as the single completion-QA entry point, with `visual-qa` supplying browser evidence and `website-delivery-qa` checking the final handback. This protocol applies to WordPress and Astro. It supplements checks during the build; screenshots never replace the human device review.

## Read the project before making the checklist

Follow `obsidian-context-contract.md` to resolve knowledge and work roots. Read the canonical client overview/profile, Goals.md, Current Projects.md, relevant project-management notes, approved brief, approved design/prototype, scope and change requests, meeting decisions and linked task discussions available for this project. Follow verified links to work files. Record which sources and versions were read and which could not be accessed. Do not search unrelated private staff/founder records.

Extract accepted client requirements into a test matrix:

| ID | Client requirement and source link/section | Page/element | Exact test steps | Expected result | Stage | Actual result/evidence | Status | Fix owner / recheck |
|----|-------------------------------------------|--------------|------------------|-----------------|-------|------------------------|--------|---------------------|

Keep approved requests distinct from suggestions, superseded requests and unresolved conflicts. Use the latest evidenced approval; ask a focused question if sources conflict or the expected behaviour is unclear. Do not silently choose or invent a requirement. Unavailable required source material is a visible coverage gap, not a pass. Standard QA checks may be added, labelled as standards rather than client requests.

Include every accepted request, such as a particular phone number, booking destination, service-specific button, referral form, download, location link or opening behaviour. Match contact details and destinations against approved records. A request to open a booking platform in a new tab becomes an explicit test; do not assume every external link has that requirement.

## Guided real-device review

Default completion reviewer: Jaimee. If someone else is running the session, prepare the checklist for Jaimee and keep her checks pending. Record the actual tester; never attest on her behalf. Preparing a handoff does not send a message, assign a task or schedule a run. Use existing authorised project-task routing for those actions and report whether the handoff was actually recorded.

Give Jaimee the URL, staging/live label, page list and short instructions. Work through small groups, asking for actual results rather than a blanket tick. Use the available question/chat interface; do not depend on a particular checkbox tool. Record phone model, operating system, browser and test date. Begin with:

- **Mobile menu:** On your own phone, open the site, open and close the menu, expand any submenus, tap each main destination and return. Confirm links work, text is readable, nothing overlaps and the menu can be dismissed.
- **Phone links:** Tap each distinct phone number and call button, including sticky/header/footer versions. Confirm the dialler offers the approved number. Cancel before placing a call; a real call needs separate agreement. Record the displayed number, not just that something opened.
- **Booking:** Tap each distinct booking entry point. Confirm the approved platform, practitioner/service/location and destination load. Where required, confirm a new tab opens and the original website remains available. Do not create a real appointment or payment merely to test a link.
- **Forms:** Confirm fields, validation, success/thank-you behaviour and notification receipt using an agreed test submission and recipient. Plan any external submission before sending it; record delivery evidence separately from the on-screen success message.
- **Page usability:** Scroll key pages, try sticky buttons, accordions, location/map links and requested downloads. Check readable text, usable tap targets, no sideways scroll, obscured content or overlapping elements. Check landscape where relevant.
- **Client-specific requests:** Walk through every accepted requirement from the matrix with its exact steps and expected result. A general mobile pass does not cover these by implication.

Browser automation can verify link attributes, destinations, layouts and event requests, but cannot certify an actual phone dialler, installed booking app, physical device or notification inbox without observed evidence. Keep real-device results separate from simulated viewport results. Test requested browser/device combinations; unavailable coverage remains pending or blocked.

## Tracking and search verification

Use authorised read-only tools/account views where available, otherwise guide Jaimee through the relevant screen and record her observed evidence. Missing access is blocked, never evidence of correct setup. Compare account/container/property IDs with verified project records; presence alone is insufficient.

- **GTM:** Verify the intended container, published environment/version, actual loading and relevant tag firing. Check for duplicate installations. A snippet-only check is provisional.
- **GA4:** Verify the intended property/data stream and an observed test page view in Realtime/DebugView or equivalent event evidence. Check for duplicate page views. Separate site-side requests from proof that the intended property receives them.
- **Events:** Use the agreed measurement plan. Test each form success, phone click, booking click and other required action; record trigger, event name, destination, parameters and observed count. Confirm success-only form events and no duplicate firing. A booking click proves a click, not a completed booking; claim booking completion only with evidence from the agreed integration. Confirm key-event configuration where required. Respect consent choices; do not bypass them to obtain a pass.
- **GSC:** Verify the intended property covers the production URL, ownership/access is confirmed, the correct sitemap is submitted and its status is recorded. Check representative production URLs for indexing eligibility and inspect reported issues. Do not equate sitemap submission with indexing or require a new site to be indexed immediately.
- **Performance:** Record mobile/desktop PageSpeed results, URL, date and available metric evidence against the accepted project target. Distinguish lab measurements from field data; absent field data is not a failure. Record unmet targets and their disposition rather than treating a score alone as launch approval.

## One report, fixes and final verification

Save one combined report under the verified work root using `site-launch-qa/YYYY-MM/`, with screenshot and specialist-report links. Include source coverage, requirements matrix, automated findings, Jaimee's device results, tracking/search evidence, performance, outstanding issues, fix owners and retest results. Use `pass`, `fail`, `pending`, `blocked` or `not_applicable` per check. Explain every not-applicable result. Untested is pending; inability to test is blocked. Mark accepted exceptions explicitly with approver, date and reason; do not rewrite a failed observation as a pass.

Return failed items to the responsible builder/tracking owner. Review does not authorise edits or live tracking changes. After fixes, repeat affected tests, including Jaimee's phone check when relevant, and record new evidence while retaining the original failure. Require no unresolved blockers/failures unless explicitly accepted by the authorised sign-off owner. Pending mandatory checks prevent completion. Read back the saved report and update the existing project record with the verified link and truthful status through its authorised workflow.

Separate staging readiness from post-launch verification. Staging may intentionally block indexing or use test tracking; judge against its declared environment. After launch, recheck the production domain, redirects, indexing settings, GTM/GA4/events, GSC/sitemap and key phone/booking/form journeys. Keep production-only checks pending until live evidence exists. QA approval does not itself authorise publication.
