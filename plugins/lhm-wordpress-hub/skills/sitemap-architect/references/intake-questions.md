# Sitemap Architect — Upfront Intake Questions

Ask these **before** any keyword research or architecture work. Every question here exists because not asking it, on a real project, forced rework after the architecture was already built.

Put them to the user via `AskUserQuestion`, batched. Do not ask things already answered in `client_profile.md` or the campaign playbook — read those first and only ask the gaps.

Record answers in the PM doc.

---

## Block A — Build Type & Scope

**A1. Is this a rebuild of an existing site, or greenfield?**
- Rebuild of a live domain
- New domain, no existing site
- Rebuild + domain change

*Why:* rebuilds require full live-site reconciliation (Step 1) before keyword research. Greenfield skips it entirely. Getting this wrong wastes a whole pass.

**A2. Is the live site still being edited while we build?**
- No, it's frozen
- Yes, content is still being added
- Unsure

*Why:* if the client is publishing during the rebuild, the audit is a moving target and needs re-running before launch. Check `lastmod` in the sitemap index — a date within the last week or two is the tell.

**A3. Is any of the current site deliberately excluded from the rebuild?**

*Why:* catches "we're dropping that service" before you build pages for it.

---

## Block B — Hidden Content Types (highest value block)

**B1. Does the site have any programmatic or templated page sets?**
- Area / suburb / proximity pages
- Service × location combination pages
- Product or inventory pages
- Directory or listing pages
- None that I know of

*Why:* **this is the single highest-value question in the intake.** Programmatic sets are frequently absent from `page-sitemap.xml`, invisible in a casual review, and represent dozens of live ranking pages. A missed set has led to a redirect map that would have deleted working pages.

If yes, ask for the URL pattern and, ideally, the full list.

**B2. Are there custom post types beyond pages and posts?**
- Staff / practitioner / team profiles
- Testimonials or reviews
- Case studies / projects / portfolio
- Resource or education library
- Products
- Locations
- None / unsure

*Why:* each CPT is a content type with its own sitemap that a page-level audit will not see.

If unsure, that's fine — Step 1 will surface them. The question is still worth asking because the client often knows about a section you'd otherwise misclassify as legacy.

**B3. Is there any content you already know is legacy or want retired?**

*Why:* saves analysing content that's being killed anyway, and surfaces the client's own view of what's stale.

---

## Block C — Locations & Services

**C1. Confirm the full list of physical locations, and which are real premises vs service areas.**

*Why:* a "location" page may be a real clinic or a proximity page for a suburb with no premises. Treating one as the other produces wrong redirects and wrong NAP blocks.

**C2. Confirm the full service list, including anything not currently on the site.**

*Why:* live-site audits routinely surface services missing from the client profile. Ask both directions: what's on the site that shouldn't be, and what's missing that should be.

**C3. Does each location offer every service, or does it vary?**

*Why:* drives Step 4. If services vary by site, the service × location matrix has structural gaps before you even look at volume.

**C4. Which service leads at each location?**

*Why:* the dominant modality differs by site and is often not the flagship. Ask, then validate against volume data — the client's perception and the search data sometimes disagree, and that disagreement is worth surfacing.

---

## Block D — Access & Data

**D1. Do we have working Google Search Console access?**
- Yes, verified and working
- Property exists but access is broken
- No

*Why:* GSC is how you validate ambiguous suburb volumes and identify which existing pages are actually performing. If broken, flag it as a blocker early — it has a lead time to fix and it gates decisions about which pages are worth keeping.

**D2. Is Screaming Frog available in this environment?**

*Why:* determines whether Step 1b runs properly or falls back to sitemap enumeration, which cannot see orphans or noindex.

**D3. Any known ranking pages we must not disturb?**

*Why:* the client often knows which page brings in the work. Worth hearing before you propose consolidating it.

---

## Block E — Strategy Posture

**E1. Metro-level or suburb-level targeting for service pages?**
- Metro (e.g. "physio melbourne")
- Suburb-level
- Both, with a defined split

*Why:* determines whether service pages are single metro pages or a location-scoped set, which changes the whole services silo.

**E2. Anything already agreed with the client we should not relitigate?**

*Why:* avoids reopening settled decisions and wasting a review cycle.

---

## Follow-Up Questions Worth Asking Later

Not upfront, but flag early so the client can gather them:

- Practitioner or author details: discipline, qualifications, registration numbers, special interests, which location(s). Needed for staff profiles and any service × location pages, and typically slow to collect
- Formal certifications, partnerships, affiliations — feeds trust and qualifications pages
- Founder/team background copy where the playbook has gaps
