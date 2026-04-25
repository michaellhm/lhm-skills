---
name: lp-project-manager
description: "Read, create, or update the landing-page-project-management.md file for a landing page campaign. Use this when the user mentions 'LP project status', 'landing page status', 'where are we at with the landing page', 'update LP project', 'create LP project', 'LP progress', 'what's left on the landing page', or 'landing page project management'. Also run this at the start of any LP workflow to ensure the project file exists."
---

# LP Project Manager

Read, create, or update the `landing-page-project-management.md` file that tracks the full lifecycle of a landing page campaign — from copy through to go-live.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-project-manager/LEARNED.md` if it exists
2. Identify the client project directory (current working directory or parent)
3. Check if `lp/landing-page-project-management.md` already exists

## Step 1: Determine Action

If the file **exists**, read it and determine the current state:
- Show the user a summary: which phases are complete, which are in progress, what's next
- Ask if they want to update any tasks or add notes

If the file **does not exist**, proceed to Step 2 to create it.

## Step 2: Gather Project Details

Use `AskUserQuestion` to collect:

1. **Client name** — who is this landing page for?
2. **Campaign name** — Google Ads campaign (if applicable)
3. **Copy source** — does the user have existing landing page copy, or do they need to write it from scratch?
   - If existing: ask for the source URL(s)
   - If new: the copywriting skill will be used later (see Phase 1 copy workflow)
4. **Google Ads CSV** — does the user have a Google Ads export? If yes, ask them to provide it. Parse the CSV to extract:
   - Campaign name
   - Ad group names (each ad group may need a landing page variation)
   - Ad copy (headlines, descriptions) for reference
   - Current final URLs per ad group
5. **Environment details:**
   - Multisite base URL (default: `http://localhost:8084/`)
   - Subsite slug (e.g. `dry-eye-solution`)
   - Docker container name (default: `leadscalepro-wordpress-1`)
   - phpMyAdmin URL (default: `http://localhost:8085`)
   - Path to `.env` file for credentials
6. **GTM Container ID** — if the client has Google Tag Manager set up, collect the container ID (e.g. `GTM-XXXXXXX`)

## Step 3: Create the File

Create `lp/landing-page-project-management.md` using this template:

```markdown
# Landing Page Project Management — [Client Name]

## Overview
- **Client:** [Client Name]
- **Landing Page:** [Primary page name]
- **Campaign:** [Campaign name or "pending Google Ads CSV import"]
- **Last Updated:** [Today's date]

## Reference Documents
- **Design Spec:** `docs/superpowers/specs/[spec-filename].md`
- **Implementation Plan:** `docs/superpowers/plans/[plan-filename].md`
- **Client Profile:** `wordpress/client/client_profile.md`
- **Brand Guidelines:** `wordpress/design/brand_guidelines.md`

## Environment

### Localhost
- **URL:** [e.g. http://localhost:8084/client-slug/]
- **WP Admin:** [e.g. http://localhost:8084/client-slug/wp-admin/]
- **Username:** admin
- **Password:** See `.env` file at [path to .env]
- **Docker Container:** [container name]
- **phpMyAdmin:** [e.g. http://localhost:8085]

### Staging (when applicable)
- **URL:** —
- **WP Admin:** —
- **SSH Access:** See credentials at [path or vault reference]

### Production (when applicable)
- **URL:** —
- **WP Admin:** —
- **SSH Access:** See credentials at [path or vault reference]

## Pages

| Page | Slug | Post ID | Status |
|------|------|---------|--------|
| [Page name from ad group] | /lp/[slug] | — | Not started |

## Google Ads — Ad Groups

| Ad Group | Impr. | Clicks | Conv. | Current Final URL |
|----------|-------|--------|-------|-------------------|
| [populated from CSV] | — | — | — | — |

## Location Data

| Clinic | Phone | Address | Maps Embed | Booking URL | Free Call URL | Hours | Post ID |
|--------|-------|---------|------------|-------------|---------------|-------|---------|
| [clinic name] | — | — | — | — | — | — | — |

## Tasks

### Phase 1 — Copy & Content

**Copy workflow:** Master copy first, then ad group variations.

1. Import Google Ads CSV and populate the Ad Groups table
2. Determine copy source (existing page OR write from scratch)
3. **Write/revise the master copy** using the copywriting skill:
   - Use `AskUserQuestion` to confirm copy direction before writing
   - Write hero copy (above the fold) first — present to user for approval
   - Write remaining sections — present to user for approval
   - The master copy becomes the canonical version for the primary landing page
4. Once master copy is approved, create ad group variations:
   - Review each ad group's keywords, ad copy, and intent
   - Adapt headline, subheadline, and key messaging per ad group
   - Variations are lightweight — same page structure, different hero/CTA copy
   - Use `AskUserQuestion` to confirm variations before finalising

- [ ] Import Google Ads CSV export (campaign, ad groups, ad copy)
- [ ] Populate Ad Groups table and Pages table
- [ ] Determine copy source: existing copy OR write from scratch
- [ ] If existing: extract and review copy from source URL
- [ ] Write/revise master copy — copywriting skill with `AskUserQuestion` approval flow
- [ ] Client approval on master copy (hero + full page)
- [ ] Create ad group copy variations (if multiple ad groups)
- [ ] Client approval on variations

### Phase 2 — Theme & Infrastructure
- [ ] Implement per-subsite CSS feature (manual — functions.php edit)
- [ ] Build new theme patterns if needed (manual — pattern PHP files)

### Phase 3 — Prototype
- [ ] Build HTML prototype — `lp-prototype` skill
- [ ] Internal review
- [ ] Client approval on prototype

### Phase 4 — Subsite Setup

#### 4a. Create & Configure Subsite
- [ ] Create subsite on multisite — `lp-subsite-setup` skill
- [ ] Activate theme — `lp-subsite-setup` skill
- [ ] Create subsite CSS file — `lp-subsite-setup` skill

#### 4b. Brand & Customizer Settings
- [ ] Logo uploaded and set
- [ ] Site icon (favicon) uploaded and set
- [ ] Site title and tagline configured
- [ ] Brand colours configured (primary, dark, light, heading)
- [ ] Typography configured (heading font, body font)
- [ ] Phone number set
- [ ] GTM container ID configured (if applicable)
- [ ] Social media URLs configured (if available)
- [ ] Google review data / social proof configured (if available)

#### 4c. Location Data Completeness
For each clinic, ensure all fields are populated in the Location Data table:
- [ ] All clinic phone numbers confirmed
- [ ] All clinic addresses confirmed
- [ ] All Google Maps embed URLs generated
- [ ] All booking URLs confirmed (Cliniko/other booking system)
- [ ] Free call / national number confirmed
- [ ] All clinic hours confirmed
- [ ] Location CPT entries created in WordPress — `lp-subsite-setup` skill

#### 4d. Pattern Testing
- [ ] Test new theme patterns in block editor (requires active subsite)

### Phase 5 — HTML Deploy
- [ ] Deploy HTML blocks to WordPress — `lp-deploy-1` skill
- [ ] Extract CSS to subsites/{slug}.css — `lp-deploy-1` skill
- [ ] Deploy remaining pages (if multiple ad groups) — `lp-deploy-1` skill
- [ ] Verify frontend matches prototype
- [ ] Mobile / tablet / desktop check

### Phase 6 — Gutenberg Conversion
- [ ] Convert HTML blocks to native Gutenberg blocks — `lp-deploy-2` skill
- [ ] Verify frontend matches HTML version
- [ ] Test block editor usability (can client edit content?)
- [ ] Mobile / tablet / desktop re-check

### Phase 7 — Remaining Pages Deploy
Deploy all remaining ad group landing pages after the primary page is fully converted.
- [ ] Identify ad groups that need dedicated landing pages (review Ad Groups table)
- [ ] Create copy variations for each remaining page (if not done in Phase 1)
- [ ] Build prototypes for remaining pages — `lp-prototype` skill
- [ ] Deploy remaining pages to WordPress — `lp-deploy-3` skill
- [ ] Verify all pages match prototypes
- [ ] Mobile / tablet / desktop check on all pages
- [ ] Update Pages table with Post IDs and statuses

### Phase 8 — QA & Go-Live
- [ ] All links tested
- [ ] Forms / CTAs tested end-to-end
- [ ] Page speed check
- [ ] AHPRA compliance review (healthcare clients)
- [ ] SEO: title tag, meta description, schema
- [ ] Analytics / GTM tracking confirmed
- [ ] Deploy to staging/production — `lp-subsite-deploy` skill
- [ ] Final verification on live domain

## Notes & Decisions
- [Today's date]: Project kicked off. [Brief context note.]

---

## Handoff Prompt

Copy and paste the following into a new Claude Code session to pick up where we left off:

\```
I'm continuing work on the [Client Name] landing page project. Read these files in order to get up to speed:

1. `lp/landing-page-project-management.md` — project status, completed tasks, environment details
2. `[path to design spec]` — full design spec (section architecture, CSS features, content mapping, deployment workflow)
3. `[path to implementation plan]` — implementation plan with task breakdown (check the PM file for which are done)

After reading all three, tell me where we're at and what the next task is. Use the lhm-wordpress-hub plugin skills (lp-prototype, lp-subsite-setup, lp-deploy-1) as specified in the plan.
\```
```

Populate the template with the details gathered in Step 2. If a Google Ads CSV was provided, add one row per ad group to the Pages table. Fill in the Reference Documents section with actual file paths. Fill in the Handoff Prompt with the correct paths and client name.

## Step 4: Update an Existing File

When updating (not creating), follow these rules:

- **Completing a task:** Change `- [ ]` to `- [x] (YYYY-MM-DD)` with today's date
- **Skipping a task:** Change `- [ ]` to `- [~] (YYYY-MM-DD) Skipped — [reason]` with today's date and the user's stated reason
- **Adding a note:** Append a dated line to the Notes & Decisions section
- **Adding a page:** Add a row to the Pages table
- **Updating status:** Change the Status column in the Pages table (Not started → Copy ready → Prototype ready → HTML Live → Gutenberg Live → QA passed → Live)
- **Updating environment:** Fill in staging/production URLs when known
- **Adding Post ID:** Update the Post ID column after `lp-deploy-1` creates the WordPress page

Never remove completed tasks — they serve as an audit trail.

## Step 5: Phase Gate-Check (REQUIRED before advancing)

**Before starting any task in the next phase, you MUST check the PM file for incomplete tasks in the current and all previous phases.**

1. Read the PM file and scan all phases up to and including the current one
2. Identify any tasks still marked `- [ ]` (incomplete)
3. If incomplete tasks exist, **stop and present them to the user**:

> **Phase gate-check:** Before we move to Phase [N], these tasks from earlier phases are still open:
>
> - [ ] [Task description] (Phase X)
> - [ ] [Task description] (Phase Y)
>
> For each one, would you like to:
> - **Complete it now** — we do the work before moving on
> - **Mark as done** — if it's actually been completed outside this session
> - **Skip it** — not applicable or deferring (I'll note the reason)
> - **Defer it** — keep it open but proceed anyway (I'll flag it as a known gap)

4. Wait for the user to respond for each task
5. Update the PM file accordingly:
   - Mark as done: `- [x] (YYYY-MM-DD)` 
   - Skip: `- [~] (YYYY-MM-DD) Skipped — [reason]`
   - Defer: Leave as `- [ ]` but add a note in Notes & Decisions: `[date]: Deferred [task] — [reason]. Proceeding to Phase [N] with known gap.`
6. Only proceed to the next phase once all tasks are resolved (completed, skipped, or explicitly deferred)

**Do not skip this check.** Even if the user says "let's move to the next task" — if that task is in a new phase, run the gate-check first.

## Step 6: Report Status

After creating or updating, show the user:

1. **Progress summary:** X of Y phases complete, X of Y tasks complete
2. **Current phase:** What phase is in progress
3. **Next action:** What task should be done next, and which skill to use
4. **Blockers:** Any tasks waiting on user input (hero copy, CSV import, client approval)
5. **Gate status:** Whether the current phase is clear to advance, or if tasks need resolution first
