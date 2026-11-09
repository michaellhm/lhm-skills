# Research basis and maintenance

Researched 2026-11-09. This is an LHM pre-launch review baseline combining official Astro behaviour, browser policy documentation, OWASP application-security guidance and integration-provider documentation used as examples. It is not an assertion that any existing client site passed these checks.

Read the installed version and current primary documentation during each audit. Documentation may describe newer Astro features than the project supports. Adapt controls to static hosting, SSR, adapter and separate functions rather than copying configuration across them.

## Primary sources

| Source | How it informs the audit |
| --- | --- |
| [Astro configuration: security and CSP](https://docs.astro.build/en/reference/configuration-reference/) | Check actual origin-check coverage, forwarded-host settings and version-specific CSP support. These are separate controls. |
| [Astro environment variables](https://docs.astro.build/en/guides/environment-variables/) | Distinguish browser-visible variables and server environment handling; inspect generated output as well. |
| [Astro template directives](https://docs.astro.build/en/reference/directives-reference/#sethtml) | Treat raw HTML insertion as a trust boundary, including CMS and structured-data content. |
| [Astro Actions security](https://docs.astro.build/en/guides/actions/#security-when-using-actions) | Actions need endpoint-level permissions even when the caller appears to be internal UI. |
| [Astro middleware](https://docs.astro.build/en/guides/middleware/) | Separate build-time prerendering behaviour from request-time SSR protection. |
| [Astro security advisories](https://github.com/withastro/astro/security/advisories) | Match actual installed versions, adapter exposure and advisory prerequisites. Consult the adapter/runtime maintainers too. |
| [OWASP XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) | Trace untrusted input to sinks; use context-appropriate encoding and sanitization. CSP supplements these controls. |
| [OWASP redirect prevention](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) | Review destination validation independently of script injection. |
| [OWASP CSP guidance](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) and [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) | Check effective policies, delivery limits, source trust, hashes/nonces and normal integration behaviour. |
| [OWASP REST security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) | Review API permissions, input limits, errors and abuse boundaries. |
| [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) | Match cross-site protections to authentication and browser request behaviour. |
| [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | Review server-side URL fetching without probing real internal services. |
| [Cloudflare Pages headers](https://developers.cloudflare.com/pages/configuration/headers/) | Static `_headers` rules do not establish equivalent protection on Pages Functions. Use current provider documentation for whichever host is actually deployed. |

## Optional provider example

[Klaviyo API key management](https://help.klaviyo.com/hc/en-us/articles/115005062267) informed the distinction between public identifiers and scoped private credentials. It is an example only: no Klaviyo integration is required or assumed. For each actual provider, consult its current documentation for credential exposure rules, scopes, endpoint versions, webhook verification and test environments. Do not transfer one provider’s key prefixes or authentication conventions to another.

## Operational conclusions

A browser demonstration needs a reproducible trust-boundary failure to establish a remote vulnerability. A localhost harness can demonstrate a real flaw, or merely change a local rendering; the port number cannot decide which.

LHM's existing Astro build standard already recommends host-level security headers. That is a build convention, not verified evidence of deployment. This skill adds repeatable source/build/deployment review, integration checks and a reportable launch decision. A dependency scan, header score or failed console snippet cannot replace that review.
