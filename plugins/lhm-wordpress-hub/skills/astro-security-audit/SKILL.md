---
name: astro-security-audit
description: "Evidence-based security review of an Astro site's source, production build and deployed preview before go-live, with API/Klaviyo checks and a launch readiness report. Use when the user says 'Astro security check', 'pre-launch security audit', 'harden our Astro site', 'check script injection or redirects', or 'check Klaviyo API security'. Also run as the Astro security specialist within site-launch-qa."
---

# Astro Security Audit

Review the release candidate before launch; retest relevant controls after fixes and domain cutover. This is a practical application-security review, not a penetration-test certification or a guarantee that a site cannot be compromised.

For client work, read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Save deliverables under verified `work_root/astro-security-audit/YYYY-MM/`; link the report from the combined site-launch-qa report and canonical project note. Do not audit the old Binsmart website merely because it motivated this skill.

## Establish scope and evidence

Resolve the repository, release commit, preview URL, intended production domain, hosting provider, Astro/adapter/runtime versions and deployed build identity from existing project records. Ask only for missing essentials; continue source review when deployment access is missing. Never mark an unavailable check passed.

Map static and on-demand routes, Astro Actions, separate serverless functions, middleware, forms, CMS/admin, third-party scripts and API connections. A static Astro frontend can still expose privileged functions. Read [Audit checks](references/audit-checks.md) and the relevant primary documentation in [Research and sources](references/research-and-sources.md). Recheck version-sensitive guidance at execution time; never upgrade blindly to match an example.

An audit authorises source inspection and bounded read-only requests against the specified site. Use a local production build or isolated staging with test data for injection, malformed requests, cross-origin tests and submissions. Do not trigger real email/SMS, marketing subscriptions, bookings, payments, destructive writes, bulk scans or load tests without specific authority and a controlled test route. Stop active tests on unexpected side effects. Do not send private source, secrets or customer data to public scanners.

## Resolve “listener” or localhost demonstrations

Record the exact URL/origin, script entry method, browser extensions/proxy/automation used, input and resulting navigation. A localhost port alone cannot identify the technique: it may be a proxy, local copy, harness or automation controller.

Event listeners are normal application code. Editing a personal browser or local proxy is not proof that a remote visitor is compromised. Conversely, do not dismiss a report just because tooling ran locally. The decisive evidence is whether an attacker-controlled input reaches an executable sink or unsafe redirect on the genuine deployed site in a clean browser without local injection. Separate XSS, open redirects, attacker-hosted copies, framing and compromised third-party scripts; a countdown is just an observed effect.

Reproduce only in the authorised test environment, trace the input-to-effect path, and record whether the issue persists for an ordinary visitor. A failed test on a different website proves nothing about this site's controls. Do not try to “block all listeners”, disable DevTools, or promise CSP prevents every navigation.

## Execute the review

1. **Source and build:** inspect the checklist's injection sinks, redirects, secrets, endpoints, authentication and third-party integrations. Use `rg` to find candidates, then trace inputs and actual callers. Record file/line evidence; a search hit is not automatically a vulnerability.
2. **Dependencies:** identify the package manager from the lockfile; check installed Astro, adapter, Vite and runtime against current official advisories. Use the package manager's audit command if available and retain its exit status. A network failure means unverified. Triage affected versions and reachability in build, preview and production separately; do not automatically run audit fixes or major upgrades.
3. **Production build:** review build scripts before execution, use the project's locked install/build/check commands in isolation, and inspect browser-delivered HTML, JS, JSON, maps and `public/` copies. Avoid printing raw secret matches. Record a filename and redacted fingerprint only. Server-only variable names are not proof that their values were kept out of rendered HTML.
4. **Deployed preview:** inspect actual GET responses for representative static pages, a nested page, forms, dynamic routes, APIs, errors and redirects. Check effective CSP from headers AND HTML, HTTPS and other controls. Use host-specific guidance; static host header rules may not cover functions. Identify the tested deployment and retain sanitised evidence.
5. **Behaviour:** test normal navigation, menus, form validation, authorised sandbox submissions and approved third-party integrations in a clean browser. Exercise bounded negative cases locally/staging as specified in the checklist. Capture CSP violations and network failures. Evaluate defence behaviour rather than a header's mere presence.
6. **Fix and retest:** an audit-only request produces recommendations. If fixes are authorised, make scoped reviewable changes, rebuild and retest the affected paths plus normal user journeys. Production deployment, account changes and key rotation follow the user's existing authority; an audit does not itself authorise them.

Useful initial searches (from the verified site root; exclude vendor/build trees and inspect results locally):

```sh
rg -n --glob '!node_modules/**' --glob '!dist/**' --glob '!.git/**' \
  'set:html|innerHTML|outerHTML|insertAdjacentHTML|document.write|eval\(|new Function|postMessage|location\.(href|assign|replace)|Astro.redirect|Response.redirect' src public functions
rg -l --hidden --glob '!node_modules/**' --glob '!.git/**' \
  'pk_[A-Za-z0-9]{20,}|PRIVATE.KEY|API.SECRET|PUBLIC_.*(SECRET|PRIVATE)' src public dist functions
```

Only include directories that exist; adapt redirect searches for framework islands and other functions. The second search returns filenames, not secrets; it is a heuristic, not a complete secret scanner. Use an available maintained secret scanner with redaction for broader coverage. Do not attach raw `.env` files or entire responses containing personal information.

## Deliver a launch decision

Write `security-report.md` with:

- Site, commit/build ID, environment/domain, timestamp, reviewer, scope and exclusions.
- Decision: **BLOCKED**, **CONDITIONAL** or **READY within reviewed scope**.
- Check matrix: check ID, PASS / FAIL / UNVERIFIED / N/A, evidence and reason. N/A requires an architecture-based explanation.
- Findings: severity, confidence, affected route/file, realistic attacker prerequisite and impact, safe reproduction, recommended fix, owner and retest evidence. Distinguish missing defence-in-depth from a demonstrated exploit.
- Coverage gaps, accepted exceptions (named owner, reason, review date), source links and post-cutover checks.

Block launch for confirmed critical/high issues such as executable untrusted input, exposed privileged credentials, broken access control or reachable severe advisories; also block where a material security-critical path remains unverified (for example the production form's privileged API boundary). Public marketing forms need abuse controls, not mandatory user login. Missing CSP alone is not proof of XSS; grade it in context. Never infer low risk from static rendering or a clean dependency scan alone.

Use CONDITIONAL when preview evidence is satisfactory but production-only checks remain, or lower-risk exceptions need an accountable decision. READY requires applicable reviewed controls verified and no unresolved blockers; it does not authorise deployment. After cutover verify production TLS, effective headers, redirects, function access controls, cache behaviour and safe form operation. Do not mark the security gate complete or the whole site ready while material gaps remain.

Return a short plain-language result, the report link, blockers and next owner/action. Preserve the project's established launch authority and approval flow; do not create a second client approval gate.
