---
name: wp-project-manager
description: "Read, create, or update the website-project-management.md file for a WordPress full website build. Use this when the user mentions 'WP project status', 'where are we at with the website', 'update website project', 'create the website PM doc', 'website progress', 'what's left on the build', or 'website project management'. Also called by phase agents after task completion to mark off checkboxes, and by wp-start at session start to detect current state."
---

# WordPress Project Manager

Manages the per-project `website-project-management.md` file that tracks the full state of a WordPress full website build: phase, step, completed tasks, page inventory, approval log, environments, and the continuation prompt.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/wp-project-manager/LEARNED.md`
2. Identify the project location: `[client_root]/wordpress/`
3. Check whether `website-project-management.md` exists in the wordpress folder

## Modes

This skill operates in five modes:

1. **Create** — generate a new PM doc at end of Phase 1 Step 1.5
2. **Read/Status** — display current phase, step, completed tasks, next action
3. **Mark Complete** — tick off a specific task with today's date (called by phase agents)
4. **Phase Gate-Check** — before any phase advance, scan earlier phases for unresolved items
5. **Session-End Sweep** — scan recent conversation, surface drift, batch user prompts

## Mode 1: Create

Triggered at the end of Phase 1 Step 1.5 after Superpowers has written the spec and plan to `docs/superpowers/specs/` and `docs/superpowers/plans/`.

Inputs:
- `[client_root]/client_profile.md` (read)
- `[client_root]/playbook.md` (read)
- `[client_root]/website-brief.md` (read)
- `docs/superpowers/specs/[filename].md` (read)
- `docs/superpowers/plans/[filename].md` (read)

Generate `[client_root]/wordpress/website-project-management.md` using the template in the next section, populating:
- Client name from `client_profile.md`
- Owner names from defaults: Aiya (build), Krystalyn (PM), Jaimee (SEO), Michael (strategy). Confirm with user via AskUserQuestion if unclear.
- Reference paths to the spec and plan files
- Page inventory rows from `seo/sitemap.md` if it exists, otherwise leave empty
- Continuation prompt with `[auto-filled]` placeholder pointing to "Phase 1, Step 1.6 — Confirm Phase 1 closure"

## Mode 2: Read/Status

When called for status display:

1. Read the PM doc
2. Identify the lowest-numbered phase containing `[ ]` items
3. Display:

```
Project: [Client Name]
Current Phase: Phase [N] — [Phase Name]
Current Step: Step [X.Y] — [Step Name]

Completed in current phase: X/Y tasks
[List completed tasks with ✅]
[List outstanding tasks with ⬜]

Next action: [first incomplete task]
Owner: [task owner]

Approval gates outstanding:
[Any phase-end gates with status]
```

## Mode 3: Mark Complete

Called by phase agents (or any skill) after a discrete task completes. Per the plugin's "Mandatory: Project Doc Updates" rule, the calling skill must first ask the user via AskUserQuestion whether to mark off — this skill assumes that confirmation has happened.

Inputs:
- `task_id` (e.g. "5.2.3" or unique task description)
- `date` (defaults to today)
- `notes` (optional)

Action:
1. Locate the matching `- [ ]` line in the PM doc
2. Replace with `- [x] (YYYY-MM-DD) [original task text]`
3. If notes provided, append a dated line to the Notes & Decisions section
4. Update the "Last Updated" field in Overview
5. Recalculate the `[auto-filled]` placeholder in the Continuation Prompt — find the lowest-numbered remaining `[ ]` item, write its phase/step/task name into the prompt
6. Save the file
7. Report: "Marked Step X.Y complete in PM doc."

## Mode 4: Phase Gate-Check

Called before any phase advance. Logic mirrors `lp-project-manager` Step 5:

1. Read the PM doc
2. Scan all phases up to and including the current one
3. Identify any tasks still marked `- [ ]`
4. If incomplete tasks exist, present them to the user:

> **Phase gate-check:** Before we move to Phase [N], these tasks from earlier phases are still open:
>
> - [ ] [Task description] (Phase X, Step X.Y)
> - [ ] [Task description] (Phase Y, Step Y.Z)
>
> For each one, would you like to:
> - **Complete it now** — we do the work before moving on
> - **Mark as done** — if it's actually been completed outside this session
> - **Skip it** — not applicable or deferring (note the reason)
> - **Defer it** — keep it open but proceed anyway (flag as a known gap)

5. Wait for the user to respond for each task
6. Update the PM file accordingly:
   - Mark as done: `- [x] (YYYY-MM-DD)`
   - Skip: `- [~] (YYYY-MM-DD) Skipped — [reason]`
   - Defer: leave as `- [ ]` but add a note in Notes & Decisions

## Mode 5: Session-End Sweep

Called by orchestrators at session end (or on user request). Logic:

1. Scan the conversation for evidence of completed work (file writes, deployments, approvals logged, etc.)
2. Match each piece of evidence to PM doc tasks
3. Identify drift — tasks done by Claude in the conversation that aren't ticked
4. Present a single batched prompt:

> Looks like we completed the following but haven't ticked them off yet:
>
> - [ ] Step X.Y — [task name]
> - [ ] Step Y.Z — [task name]
>
> Mark all complete? (yes / no / let me pick)

5. Apply the user's response

## PM Doc Template

When creating a new PM doc (Mode 1), use this template. Replace placeholder `[Client Name]` etc. with real values.

````markdown
# Website Project Management — [Client Name]

## Overview
- **Client:** [Name]
- **Primary URL:** [URL or "TBD"]
- **Project slug:** [slug]
- **Owners:** Aiya (build), Krystalyn (PM), Jaimee (SEO), Michael (strategy)
- **Last Updated:** [Today's date]
- **Current Phase:** Phase 1 — Client Onboarding & Strategy
- **Current Step:** Step 1.6 — Confirm Phase 1 closure

## Reference Documents
- Campaign Playbook: ../playbook.md
- Website Brief: ../website-brief.md
- Client Profile: ../client_profile.md
- Brand Guidelines (internal): ../design/brand_guidelines.md
- Brand Style Guide (client): ../design/brand_style_guide.pdf
- Design System: ../design/design_system.md
- Block Architecture: wp/blocks.md
- Site Architecture: seo/sitemap.md
- Design Spec (Superpowers): docs/superpowers/specs/[filename].md
- Implementation Plan (Superpowers): docs/superpowers/plans/[filename].md

## Environments

### Local
- **URL:** —
- **WP Admin:** —
- **Local site name:** —
- **Environment:** Local by Flywheel / wp-env / Docker

### LHM Design Staging (Phase 4 prototype)
- **URL:** lhmstaging.net/design/[client]/
- **SSH access:** See credentials at [path or vault reference]

### LHM Site Staging (Phase 5 site)
- **URL:** staging.lhm.com.au/[client]/ (TBD)
- **SSH access:** See credentials at [path or vault reference]

### Production
- **URL:** —
- **DNS provider:** —
- **SSH access:** —

## Page Inventory

| Page | Type | URL Slug | Primary Keyword | Status | WP Post ID |
|------|------|----------|-----------------|--------|------------|

Status values: Brief / Copy-Locked / Built / QA-Passed / Live

## Approval Log

| Date | Phase | Artefact | Sent to Client | Approved | Notes |
|------|-------|----------|----------------|----------|-------|

---

## Phase 1 — Client Onboarding & Strategy

**Owner:** Krystalyn (with Michael for Step 1.2)
**Approval gate:** Playbook + Website Brief client-approved in writing

### Step 1.1 — Collect Client Assets
- [ ] Client logo (PNG or SVG)
- [ ] Brand image library
- [ ] Existing brand guidelines (if available)
- [ ] Current website credentials (if rebuild)
- [ ] 2–4 competitor URLs from client
- [ ] Email Client Questionnaire in preparation for meeting

### Step 1.2 — Strategy Session Call
- [ ] Confirm Fathom on calendar invite
- [ ] ChatGPT open during call
- [ ] Michael runs discovery, Krystalyn captures notes
- [ ] Download ChatGPT transcript
- [ ] Download Fathom transcript

### Step 1.3 — Generate Campaign Playbook
- [ ] Run Campaign Playbook Skill in Claude with both transcripts
- [ ] Review draft for accuracy
- [ ] Send to client (3-business-day turnaround)
- [ ] Incorporate feedback
- [ ] **Client approval confirmed in writing**
- [ ] Save approved playbook to ../playbook.md

### Step 1.4 — Generate Website Brief
- [ ] Run Client Onboarding Skill referencing approved Playbook
- [ ] Review draft against strategy session notes
- [ ] Send to client (3-business-day turnaround)
- [ ] Incorporate feedback
- [ ] **Client approval confirmed in writing**
- [ ] Save approved brief to ../website-brief.md

### Step 1.5 — Generate Spec, Plan & PM Doc (Superpowers)
- [ ] Run Superpowers brainstorming + writing-plans skills
- [ ] Spec saved to docs/superpowers/specs/
- [ ] Plan saved to docs/superpowers/plans/
- [ ] PM doc generated by wp-project-manager (this file)
- [ ] Aiya / web developer reviews spec + plan
- [ ] **Project underway** — proceed to Phase 2

---

## Phase 2 — SEO Architecture & Content Planning

**Owner:** Jaimee
**Approval gate:** Michael internal sign-off on architecture and blog schedule

### Step 2.1 — Keyword Research & Site Architecture
- [ ] Run keyword research using approved Brief and Playbook
- [ ] Identify primary service pages, location pages, supporting pages
- [ ] Confirm number of blog posts in initial build
- [ ] Run TAYA Question Discovery Skill
- [ ] Cross-reference TAYA output with Reddit / niche forums
- [ ] Build blog content schedule (topic, target keyword, publish date)
- [ ] Compile site architecture document (page name, slug, type, primary keyword)
- [ ] Save to seo/sitemap.md, seo/keyword_map.md, seo/blog_schedule.md
- [ ] Send architecture to Michael for sign-off
- [ ] **Michael internal sign-off**

---

## Phase 3 — Web Copy Production

**Owner:** Jaimee
**Approval gate:** Home page client-approved; rest internal-only

### Step 3.1 — Generate Copy Briefs for All Pages
- [ ] Reference approved sitemap from Phase 2
- [ ] Generate copy briefs for all pages (title tag, slug, meta desc outline, H1, sections)
- [ ] Review against Playbook for tone and accuracy
- [ ] Save brief set to seo/page_briefs/

### Step 3.2 — Write Home Page Copy
- [ ] Use home page brief as input
- [ ] Reference Playbook for voice
- [ ] Run page-copywriter (routes through content-writer 8-pass agent)
- [ ] AHPRA compliance review (no outcome claims, guarantees, testimonial language)
- [ ] Internal review by Michael
- [ ] Send to client for approval
- [ ] **Client approval confirmed in writing**
- [ ] Mark home as copy-locked in Page Inventory above

### Step 3.3 — Write Remaining Page Copy (Batches)
For each batch of 3–4 pages:
- [ ] Core service pages first
- [ ] Then location pages
- [ ] Then supporting pages
- [ ] Run page-copywriter per page (routes through content-writer)
- [ ] AHPRA compliance review per page
- [ ] Internal review by Michael per batch
- [ ] Mark each page copy-locked in Page Inventory

---

## Phase 4 — Brand, Design System & Prototype

**Owner:** Aiya
**Approval gate:** Homepage variant client-approved + style guide client-approved (parallel)

### Step 4.1 — Brand Guidelines & Client Style Guide
- [ ] Reference approved Playbook and Website Brief
- [ ] Confirm what brand assets already exist
- [ ] Run Brand Discovery Skill
- [ ] Generate ../design/brand_guidelines.md (internal)
- [ ] Generate ../design/brand_style_guide.pdf (client-shareable)
- [ ] Internal review by Michael
- [ ] Send style guide to client (3-business-day turnaround) — runs in parallel with Steps 4.2–4.5
- [ ] **Client approval of style guide logged when received**

### Step 4.2 — Design System
- [ ] Confirm brand_guidelines.md finalised
- [ ] Run Design System Generator Skill
- [ ] Output: colour tokens, fluid type scale, spacing scale, breakpoints, radius, shadow, component specs
- [ ] Spacing scale uses fluid clamp() values
- [ ] Save to ../design/design_system.md

### Step 4.3 — Block Architecture
- [ ] Confirm sitemap and copy available
- [ ] Run Block Architect Skill
- [ ] Output: native blocks list, custom blocks list, block patterns list
- [ ] Flag any custom blocks to Michael
- [ ] Save to wp/blocks.md

### Step 4.4 — Build Homepage Prototype Variants (Internal)
- [ ] Confirm variant count with Michael (1, 2, or 3)
- [ ] Use approved homepage copy as content input (real copy, no placeholder)
- [ ] Reference brand_guidelines.md, design_system.md, blocks.md
- [ ] Run HTML Prototype Skill
- [ ] Each variant is self-contained: prototype/v1/index.html, v2/, v3/
- [ ] Mobile responsive verified per variant
- [ ] Internal review (Michael, Krystalyn, Aiya)
- [ ] Apply internal feedback
- [ ] Decide which variant(s) go to client

### Step 4.5 — Publish to LHM Staging & Client Approval
- [ ] Upload variants to lhmstaging.net/design/[client]/
- [ ] Multiple variants get separate subfolders /v1/, /v2/, /v3/
- [ ] Verify desktop, tablet, mobile rendering
- [ ] Verify all assets resolve
- [ ] Prepare review email (staging links, 3-day turnaround, specific questions)
- [ ] Send review email
- [ ] Capture feedback, apply refinements
- [ ] Re-upload refined version
- [ ] Roll out remaining template designs (about, service, location, contact)
- [ ] **Homepage direction client-approved in writing**
- [ ] **Style guide approval confirmed (from Step 4.1)**

---

## Phase 5 — WordPress Build

**Owner:** Aiya
**Approval gate:** Milestone 5-page client review (Step 5.7) + final staging walkthrough (Step 5.10)

### Step 5.1 — Local WordPress Instance
- [ ] Confirm Local by Flywheel installed (or document Docker/wp-env fallback)
- [ ] Create local site with project slug
- [ ] Confirm local site loads
- [ ] Record environment details in this PM doc (Environments section)

### Step 5.2 — Theme Scaffold & Install
- [ ] Confirm brand_guidelines.md, design_system.md, blocks.md, prototype available
- [ ] Run Theme Scaffold Skill
- [ ] Install and activate theme on local WP
- [ ] Upload client logo via Site Identity
- [ ] Upload favicon as site icon
- [ ] Run CSS Sync Check Skill — fix any missing classes
- [ ] Confirm header/footer template parts render

### Step 5.3 — Homepage Raw HTML Push (Design Verification)
- [ ] Extract body content from approved homepage prototype
- [ ] Wrap each section in wp:html block
- [ ] Push to WordPress via WP Page Builder Skill (Step 1)
- [ ] Run Visual QA Skill — desktop, tablet, mobile
- [ ] Fix any CSS or layout differences
- [ ] Internal review by Michael — confirm pixel parity

### Step 5.4 — Convert Homepage to Gutenberg Blocks
- [ ] Run WP Page Builder Skill (Step 2, native conversion)
- [ ] Verify each section editable in block editor, no console errors
- [ ] Run Visual QA Skill — confirm parity at all breakpoints
- [ ] Fix any visual regressions
- [ ] Internal review by Michael

### Step 5.5 — Dynamic Menu & Site Identity
- [ ] Reference approved sitemap from Phase 2
- [ ] Create primary menu in WordPress
- [ ] Add menu items for top-level pages
- [ ] Configure sub-menus for service / location hierarchies
- [ ] Assign menu to Primary location
- [ ] Test desktop nav and mobile hamburger
- [ ] Configure footer menu if design includes one

### Step 5.6 — Global Styles & Theme Customisation
- [ ] Confirm colour palette in theme.json settings.color.palette
- [ ] Confirm font families/sizes in settings.typography
- [ ] Verify Site Editor → Styles shows all brand colours as editable tokens
- [ ] Verify font choices appear as editable typography tokens
- [ ] Test colour token change updates site globally; revert
- [ ] Document client edit path: Appearance → Editor → Styles

### Step 5.7 — Milestone Build: 5 Pages in Gutenberg (Client Review)
- [ ] About page
- [ ] Contact page (including contact form)
- [ ] Services hub or parent page
- [ ] One Service detail page
- [ ] One Location page (if applicable)
- [ ] Use approved Phase 3 copy for each
- [ ] Apply SEO metadata per page (title, meta desc, slug)
- [ ] Run Visual QA Skill across all 5 pages
- [ ] Internal review by Michael
- [ ] Share preview with client (use Step 5.10 staging mirror if a live URL is needed)
- [ ] **Client approval to proceed with full build**

### Step 5.8 — Complete Remaining Pages
- [ ] All remaining service pages (priority order from sitemap)
- [ ] All remaining location pages
- [ ] All supporting pages (FAQ, resources, privacy, terms)
- [ ] SEO metadata applied per page (title, meta desc, slug, schema)
- [ ] Images optimised (compress, alt text, file naming)
- [ ] Internal linking per Phase 2 architecture plan
- [ ] Visual QA per page across breakpoints
- [ ] Fix visual regressions
- [ ] Update Page Inventory with built status

### Step 5.9 — Forms, SEO Metadata & Tracking
- [ ] Set up all contact forms — submissions to client's email
- [ ] Test every form end-to-end on local
- [ ] Final Yoast SEO settings site-wide
- [ ] GA4 configured, tracking pageviews
- [ ] GSC property configured (sitemap submission post-launch)
- [ ] XML sitemap generated and reachable
- [ ] robots.txt blocks indexing on staging

### Step 5.10 — Deploy to Staging Website
- [ ] Confirm SSH credentials for LHM staging server
- [ ] Confirm staging path allocated
- [ ] Run WP SSH Deploy Skill
- [ ] Verify staging loads on desktop/mobile
- [ ] Verify all assets resolve on staging URL
- [ ] Test forms end-to-end on staging
- [ ] Confirm robots.txt still blocks indexing
- [ ] Send staging URL to client for final walkthrough
- [ ] Capture and apply final feedback (re-deploy as needed)
- [ ] **Client signed off on staging site**

---

## Phase 6 — QA & Go-Live

**Owner:** Jaimee (complete) + Krystalyn (verify) + Michael (sign-off)
**Approval gate:** Michael go-live sign-off → DNS cutover → client confirmation

### Step 6.1 — Pre-Launch QA
- [ ] **SEO:** All title tags, meta descriptions, slugs match sitemap
- [ ] **SEO:** No duplicate title tags or meta descriptions
- [ ] **SEO:** XML sitemap generated and accessible
- [ ] **SEO:** robots.txt — staging blocks removed
- [ ] **SEO:** Schema markup on relevant pages, validated
- [ ] **Technical:** Mobile, tablet, desktop review per page
- [ ] **Technical:** Page speed tested — flag slow pages
- [ ] **Technical:** All internal links work
- [ ] **Technical:** Forms tested end-to-end
- [ ] **Technical:** SSL active
- [ ] **Technical:** 404 page configured
- [ ] **Content:** All copy matches Phase 3 copy-locked versions
- [ ] **Content:** Images compressed, alt text applied, no placeholders
- [ ] **Content:** AHPRA final check — no outcome claims, guarantees, comparatives
- [ ] **Tracking:** GA4 confirmed tracking pageviews on staging
- [ ] **Tracking:** GSC property configured, sitemap submitted

### Step 6.2 — Michael Sign-Off & Go-Live
- [ ] Share QA checklist with Michael
- [ ] **Michael go-live approval confirmed**
- [ ] Krystalyn notifies client of go-live window
- [ ] Jaimee points domain DNS to live server
- [ ] Confirm site live, all pages resolve
- [ ] Re-test forms on live domain
- [ ] Confirm GA4 tracking on live domain
- [ ] Send go-live confirmation email to client
- [ ] Archive project files to client folder in Google Drive
- [ ] Log project completion in agency project tracker
- [ ] **Project complete**

---

## Notes & Decisions

[Today's date]: Project kicked off. PM doc created via wp-project-manager (Phase 1 Step 1.5).

---

## Continuation Prompt

Copy-paste this into a new Claude Code session to pick up the project:

\```
I'm continuing the [Client Name] WordPress website build. Read these files in order:

1. ../client_profile.md
2. ../playbook.md
3. ../website-brief.md
4. ../design/brand_guidelines.md (if exists)
5. ../design/design_system.md (if exists)
6. website-project-management.md
7. docs/superpowers/specs/[filename].md (if exists)
8. docs/superpowers/plans/[filename].md (if exists)

After reading, tell me which phase and step we're up to based on the PM doc. The next incomplete task is [auto-filled: phase, step, task]. Are you ready to continue with that, or do you want to work on something else?
\```
````

## Output

- Creates: `[client_root]/wordpress/website-project-management.md`
- Modifies the file via Modes 3, 4, 5
- Auto-updates the `[auto-filled]` placeholder in the Continuation Prompt on every change
