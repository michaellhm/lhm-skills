# Astro pre-launch security checks

Use these IDs in the report. Apply controls to the actual architecture; record N/A with evidence when a surface does not exist. Read current primary sources linked in research-and-sources.md for implementation details. Each row needs source/configuration evidence and deployed behaviour where applicable.

## A — Rendering, scripts and navigation

| ID | Review and verification | Expected outcome |
| --- | --- | --- |
| A1 | Trace URL query/hash, CMS content, form fields, API responses, storage and message events into HTML/JS. Inspect `set:html`, DOM HTML sinks, dynamic script creation and island framework equivalents. | Untrusted content is encoded for its output context or sanitised with a maintained HTML sanitizer where HTML is required. Schema validation alone is insufficient. |
| A2 | Inspect rich text, Markdown/MDX, embeds and JSON-LD. Check script termination when serialising JSON into an HTML script element. Treat executable CMS/MDX contributions as code with publishing permissions. | Ordinary content cannot introduce script, unsafe URLs or handler attributes. Trusted code boundaries and reviewer rights are explicit. |
| A3 | Trace redirect destinations, booking links, `returnTo`/`next` parameters, timers, refresh metadata and host-derived URLs. Test external, protocol-relative and encoded destinations in staging. | Fixed destinations or parsed URL allowlists; scheme/origin/path validated after normalisation. No naive string-prefix checks. Legitimate external bookings still work. |
| A4 | Inspect `message` listeners and iframe bridges. | Exact expected origin and sender/source checks, schema validation and safe sinks; no wildcard trust for privileged messages. Ordinary click listeners remain functional. |
| A5 | Use clean-browser benign marker tests on reachable inputs and inspect resulting DOM/network locally or in staging. | Marker is rendered as inert data where expected; no unexpected button mutation or navigation. Console-injected scripts do not establish an attacker-controlled path. |

## B — Browser and hosting controls

| ID | Review and verification | Expected outcome |
| --- | --- | --- |
| B1 | Inspect effective enforcing CSP, including response headers, any meta policy and multiple policies. Check browser console on key journeys. | Script permissions limited to necessary code/origins with hashes/nonces as appropriate; broad wildcards, `unsafe-inline` and `unsafe-eval` justified or removed. Report-only is observation, not enforcement. |
| B2 | Review `object-src`, `base-uri`, `form-action`, `frame-ancestors`, `connect-src`, `frame-src` and resource sources against the integration inventory. | Restrictive values appropriate to the site, with necessary APIs/embeds/forms allowed. `default-src` does not substitute for every directive. CSP does not generally prevent arbitrary top-level redirects. |
| B3 | Check CSP delivery against deployed Astro version and rendering mode. | Static hashes can suit generated assets; SSR nonces are unpredictable per response and consistent with caching. Do not bake a fixed nonce into static HTML or copy unverified configuration syntax. Meta CSP cannot deliver `frame-ancestors` or report-only; set those controls in response headers. |
| B4 | GET representative static, dynamic, error and API responses and compare host config. | `X-Content-Type-Options: nosniff`, appropriate `Referrer-Policy`, framing policy and narrowly justified Permissions-Policy. Cookies/response bodies are redacted in receipts. Cloudflare Pages `_headers` does not cover Pages Functions responses; verify function headers separately. |
| B5 | Check production certificate, HTTP-to-HTTPS and canonical-domain redirects, mixed content and HSTS. | HTTPS throughout. Enable HSTS only with domain/subdomain readiness; do not blindly add includeSubDomains or preload. Preview-provider headers do not prove production-domain readiness. |
| B6 | Review private response caching, CDN variation and error handling. | Authenticated or personal responses are not publicly cached; generic errors disclose no stack traces or secrets. Secrets are absent from public artifacts. Source maps alone are not evidence of secret leakage. |

Derive CSP from the built site's actual script/style/network inventory. Use report-only during controlled rollout when useful, then verify enforcement. Retest the project’s analytics, marketing integrations, consent controls, booking widgets, fonts and forms; do not widen to all origins simply to quiet violations. A trusted tag manager can execute powerful third-party code, so review its access and publishing controls too.

## C — APIs, integrations and forms

| ID | Review and verification | Expected outcome |
| --- | --- | --- |
| C1 | Follow each credential from environment binding to request. Inspect browser assets, rendered data, error output, logs and repository exposure using redacted scanners. | Private keys remain server-side with minimum required scopes. `PUBLIC_` is not for secrets. Provider-documented public identifiers or publishable keys are not private credentials; verify their permitted use and restrictions against that provider’s documentation. If a private key was exposed, removing it is insufficient: report the need for revocation/rotation and exposure review. |
| C2 | Map each browser/form → server endpoint/action/function → external service data flow, plus documented direct browser integrations. Review provider endpoint/version/scopes against current documentation. | Server chooses allowed operation, destination/resource and permitted fields; no arbitrary API proxy, user-chosen provider URL or unrestricted privileged operation. Never trust client-side hidden fields as authority. |
| C3 | Test wrong method, malformed/oversized body, unexpected fields and missing required values with mocks or sandbox destinations. | Server validates type, length, field allowlist and content type before side effects; bounded upstream timeouts and payload sizes. No sensitive data returned to visitors or logged unnecessarily. |
| C4 | Review rate limits, server-verified CAPTCHA where used, replay/deduplication and abuse monitoring. Test only bounded cases in isolated staging. | Controls work server-side and across relevant deployment instances; failure cannot bypass them. Honeypots and client JavaScript alone do not protect an endpoint. Limit repeated signups/notifications; honour provider retry guidance without duplicate side effects. |
| C5 | Inspect cookies, state-changing handlers and browser-origin policy; exercise relevant cross-site cases in staging. | CSRF protection appropriate to session/cookie use and supported request types. Check installed Astro's origin-check coverage; do not assume JSON endpoints or separate functions inherit it. CORS is neither authentication nor a block on direct server-to-server callers. |
| C6 | Review consent flow, sandbox test identity and success/failure handling. | Subscription consent is explicit where required by the agreed flow; a generic enquiry does not silently subscribe someone. No real campaign/email triggered by audit. Display success only after the intended operation succeeds; handle provider failures safely. |
| C7 | If webhooks exist, inspect provider-specific authenticity, timestamp/replay checks and idempotency. | Authenticity is verified using the provider's supported mechanism before processing; missing/invalid evidence is rejected in staging. Do not invent a signing-header convention. |

## D — Dynamic routes, CMS and deployment

| ID | Review and verification | Expected outcome |
| --- | --- | --- |
| D1 | Enumerate Actions, API routes, middleware, functions, private pages and server islands; test anonymous and wrong-role access with test accounts. | Server-enforced authentication and per-operation/object authorisation where required. Astro Actions are public endpoints by default. Hidden UI, guessed route secrecy and cookie presence alone are insufficient. |
| D2 | Inspect prerendering and access control timing. | Private data is not generated into public static files. Build-time middleware is not treated as per-request protection for static pages. Dynamic routes have real runtime checks. |
| D3 | Review session storage/cookies, CMS OAuth and admin access. | Secure/HttpOnly/SameSite and session expiry appropriate to use; redirects and OAuth state checked. CMS/repository/host permissions are limited, MFA enabled where available, former collaborators removed through authorised account owners. Public admin UI is not by itself proof of unauthorised write access. |
| D4 | If remote fetching/image proxies/uploads exist, trace supplied URLs and file paths. | No arbitrary private-network/metadata fetches, unrestricted redirect following or path traversal; upload validation/storage rules appropriate to use. Confirm by code review or isolated mocks, not requests to real internal/cloud metadata services. |
| D5 | Inspect proxy trust, forwarded host headers, allowed host configuration and absolute URLs. | Only intended hosts/proxies influence origin-dependent decisions. Astro `security.allowedDomains` concerns forwarded-host validation, not a general CORS or script allowlist. Verify adapter behaviour. |
| D6 | Check dependency advisories against the lockfile, runtime and reachable behaviour; include build/preview tooling risk. | No unresolved applicable high/critical issues. Record advisory link, affected/fixed versions and applicability; avoid pinning a perpetually 'safe' version in this skill. Dev servers and debug tools are not production entry points. |
| D7 | Inspect CI/deploy access, preview exposure, environment separation and rollback. | Preview uses test credentials/data, sensitive previews have access controls, production build comes from intended commit. Preview `noindex`/robots is not access control. Backup/rollback and incident owner are known; no production cutover performed by the audit. |

## Evidence and retests

Use a route matrix covering each distinct execution path rather than only the homepage. An ordinary `curl` GET with headers saved to a private local receipt is useful; HEAD may differ. Do not follow untrusted redirects automatically or forward credentials to a different origin. Record each hop when investigating redirects. Do not disable certificate verification to manufacture a pass.

For sandbox submissions verify the downstream result in the sandbox, not only HTTP 200. For auth tests prove both a permitted test user succeeds and an unauthorised user fails. For CSP changes prove expected UI/integrations work while the relevant disallowed behaviour is rejected. Retest evidence must identify the new build/commit; an old screenshot does not close a new finding.
