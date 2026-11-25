# LHM Astro Hub — design

Status: draft for Michael's review. Nothing built.
Date: 2026-11-25
Source: brainstorming session with Michael, 25 November 2026.

## Why

LHM has moved off WordPress and builds client websites in Astro now. The Astro pieces are scattered across `lhm-wordpress-hub` and `lhm-marketing-hub`, mixed in with about 30 WordPress skills. Michael wants one plugin that runs the whole Astro website process from start to finish.

The new thing being sold is the **client brain**: a set of linked Obsidian-style notes in the client's GitHub repo. It describes the business (services, staff, who they serve, brand, how they like copy written). It's written mainly for AI to read. The client opens one project in their AI app (ChatGPT/Codex, Claude or Gemini) pointed at the repo, and the AI knows their business and their site. The brain replaces the old campaign playbook doc.

The brain gets smarter over time. Every approved client edit to the site is read, and new facts and writing preferences go back into the brain. Every later round of content uses those rules, so clients have to make fewer edits each round.

## Goals

- One self-contained plugin, `lhm-astro-hub`, that holds every skill the Astro process needs.
- A single entry point (`start-astro`) that works out which stage a client is at and runs the next step.
- The process:
  1. **Sitemap.** Plan the pages. Each page carries its keywords and target market, so the copy brief can be built straight from it.
  2. **Prototype.** Plain HTML, designed with UI UX Pro Max, pushed to the shared prototype repo.
  3. **Astro build.** Build the site and deploy it to the client's Cloudflare account, with a form (GoHighLevel or Cloudflare D1).
  4. **Build the brain.** From the Fathom calls, the approved prototype copy and the UI UX Pro Max style guide.
  5. **Content round 1.** Pick the pages and template, write them, push them, update the client's project file and email the client to run their review.
  6. **Client review.** The client edits and approves in their AI app, ticking pages off in the project file.
  7. **Update content brain.** Read the approved changes and update the brain.
  8. **More content rounds.** Repeat steps 5 to 7.
- QA, SEO best practice and Astro best practice checks built into the steps.
- A client repo with `README.md`, `brain/`, `skills/` and `site/`, where the README lets any AI set the client up on Mac or Windows.

## Non-goals

- No CMS. Decap CMS is not carried over. Clients edit through their AI app and GitHub.
- No changes to `lhm-wordpress-hub` or `lhm-marketing-hub` in this project. They keep their copies. Michael will clean them up separately later.
- No WordPress support in the new plugin.
- No sales or prospect sitemap mode (the impressions-to-leads widget). That stays in the marketing hub.

## Anti-goals (would make this a failure even if it works)

- **A complicated client setup.** Michael was explicit: "really, really simple". If the README or the client skills need a technical person to get going, it has failed.
- **Branch ceremony the staging phase doesn't need.** While the site is in staging, everything (LHM's content rounds and the client's edits) pushes straight to `main`.
- **A brain that drifts from the truth.** It must not hold facts nobody approved, and it must not be copied by hand into a second place, like the internal vault.
- **Invented facts.** No made-up claims, prices, staff or results in the brain or the copy.

## Approaches considered

- **A. Self-contained Astro plugin (chosen).** Copy every skill the process uses into the new plugin and adapt each one. It's one install, and everything is in one place. The cost is roughly 10 to 15 skills existing twice for now. Michael accepted that, because the marketing and WordPress hubs will be cleaned up later.
- **B. Astro plugin owns the process but reuses marketing hub skills by name.** No duplicates, but it depends on the marketing hub being installed. Not chosen.
- **C. Turn `lhm-wordpress-hub` into the Astro hub.** Dropped. It breaks anything still pointing at WordPress skills, and Michael asked for a new plugin.

## The client repo

One GitHub repo per client:

```
<client>/
  README.md     written for an AI: set the client up on Mac or Windows,
                in ChatGPT (Codex), Claude or Gemini. Short and simple.
  brain/
    Overview.md        start here; links to every other note
    Profile.md         mission, vision, values, founder story, positioning (the marketing core)
    Project.md         the client's page checklist: written, awaiting review, approved, by round
    Services.md
    Staff.md
    What We Do.md
    Who We Serve.md
    Brand.md           the UI UX Pro Max style guide (colours, type, components, do/don't)
    Content Rules.md   how this client wants copy written (learned from their edits)
    Change Log.md      every analysed client change: date, what changed, what we learned
  skills/              the client's built-in AI skills (start, review, share, finish)
  site/                the Astro website (Cloudflare builds from this folder)
```

Decided:
- **One repo holds both the brain and the site**, so the client's AI project needs one GitHub connection. Cloudflare Pages deploys from the `site/` root directory.
- **The brand style guide lives in `brain/`**, not in the prototype's `assets/` folder.
- **The brain is for AI first.** Notes use plain Markdown with YAML frontmatter and `[[wikilinks]]` so they also open cleanly in Obsidian.
- **Relationship to the internal LHM Knowledge vault.** `20 Clients/<client>/` keeps LHM-only material (projects, commercials, internal notes the client shouldn't see) plus a link to the client's brain repo. Business facts live only in the brain. Nothing is mirrored between them.
- **The prototype stays in the shared `lhm-prototype` repo** (`github.com/michaellhm/lhm-prototype`, one folder per client), as today.

Because the style guide is written at the prototype stage, the client repo (with an empty `brain/`) is created when the project starts, not after the build.

## The stages and the skills that run them

Each skill below is copied into `plugins/lhm-astro-hub/skills/` from where it lives today, then adapted. "New" means there is nothing to copy.

### Agents
- **`astro-lead`**: the one agent the team pulls in ("where are we with this client, what's next?"). It reads three things:
  - the LHM-internal project management file in the LHM Knowledge vault (`20 Clients/<client>/project-management/` and `Current Projects.md`, found through the existing client routing contract)
  - the client repo
  - `brain/Project.md`

  From those it says which stage the client is at and what comes next, then runs the right skill. After each stage it updates the internal project file with what was done, what's next and any blockers. Where the internal file and the repo disagree, it shows the conflict rather than picking one. It is built on the existing `astro-lead` and `website-build-orchestrator` (WordPress hub), with the WordPress routing removed.
- **`content`**: copied from the marketing hub. `astro-lead` hands every page-writing job to it, so writing keeps the Content Lead's brief → write → QA discipline.
- No other agents. Everything else is a skill that `astro-lead` calls.

### 0. Start and repo setup
- `start-astro`: the single entry (a command that loads `astro-lead`). Reads where the client is (sitemap, prototype, build, brain, content round), says what's next and runs it. It stops at the approval points listed below. Built on the existing `start-astro` and `astro-lead` (WordPress hub).
- `client-repo-setup`: creates the client repo with `README.md`, `brain/`, `skills/` and `site/`. Built from `repo-init` (WordPress hub) plus the install part of `client-review-release`.

### 1. Sitemap
- `astro-sitemap`: copied from `client-sitemap-plan` (marketing hub), including both scripts. Each page gains these fields:
  - `primary_keyword`
  - `secondary_keywords` (list)
  - `audience` (who the page is for)
  - `intent` (informational, commercial or transactional)

  These are the fields the Content Lead brief already asks for, so a brief can be built from the sitemap without asking again. Keyword data comes from the same research the skill already does (Keywords Everywhere / `keyword-research`, copied in).

### 2. Prototype
- `astro-prototype`: copied from `html-prototype` and `start-prototype` (WordPress hub).
  - UI UX Pro Max is **required**, not optional. Run its design-system step first, and record what was adopted, overridden or rejected (the current `html-prototype` LEARNED.md already describes this).
  - Output is plain HTML with separate `assets/css`, `assets/js` and `assets/images`. No inline CSS or JS.
  - Pushed to `lhm-prototype/<client>/`.
  - The style guide UI UX Pro Max produces is written to the client repo as `brain/Brand.md`.
  - Approval point: the client approves the prototype, including its copy.

### 3. Astro build
- `astro-build`: copied from the WordPress hub, together with `references/astro-build-standard.md`, which is the "Astro best practice" source.
  - Builds into `site/` and deploys to the client's Cloudflare account.
  - No Decap CMS step.
- `astro-form`: copied from `contact-form-submissions`, which covers D1, Turnstile, email alerts, the thank-you page and the admin view. During the build it asks whether the client has a GoHighLevel account.
  - If yes, the form sends submissions to GoHighLevel. **This part is new**: nothing in the repo connects to GoHighLevel today.
  - If no, the form uses the existing D1 path.
- QA: `site-launch-qa` (Astro checklist) and `website-delivery-qa`, copied.

### 4. Build the brain
- `build-brain` (new). Reads:
  - the client's Fathom calls (Fathom connector)
  - the approved prototype copy
  - `brain/Brand.md`
  - the internal vault overview, for confirmed facts

  Writes the brain notes. The extraction categories come from `campaign-playbook-generator` (founder story, mission, services, audience, voice and so on), split across the notes instead of one long doc. Mission, vision, values, founder story and positioning go in `Profile.md`. Gaps are marked as gaps, never filled in. `Content Rules.md` starts with voice notes from the calls. `Change Log.md` starts with a "brain created" entry.

### 5. Content rounds
- `content-rollout` (new, built from `lhm-page-rollout` with the LHM-specific repo facts removed). A round runs like this:
  1. **Ask what to write.** Which pages should this round cover? Which template should they use? The template is a prototype page LHM has already made, such as a service overview page or a condition page.
  2. **Propose the round.** For example: "8 pages in this order, using the condition template." Then ask: "Would you like me to make the first page as a mock-up for you to approve, or batch the lot?"
  3. **If mock-up first:** write and build page 1, wait for approval, then do the rest. **If batch:** do them all.
  4. **For each page:**
     - Build the brief from the sitemap entry, the brain and `Content Rules.md`.
     - Write it through the Content Lead flow: brief → writing skill (8-pass for page copy) → independent QA (`content-quality-auditor`).
     - Build it, push to `main` and check every URL once Cloudflare finishes deploying.
  5. **Hand the round to the client.**
     - Update `brain/Project.md` so these pages show as "awaiting client review" under this round.
     - Draft the client email (`client-update-email`): what's ready, the preview links, and the copyable prompt to open the project and run `review-website`.

  Copied in for this: the `content` agent, `seo-page-brief`, `seo-content-writer`, `copywriting`, `content-quality-auditor`, `seo-delivery-qa` (the "SEO best practice" check), `references/content-departmental-delivery.md`, `8-pass-writing-engine.md` and `anti-ai-writing-guidelines.json`.

  **Every writer reads `brain/Content Rules.md` before writing.**
- `client-update-email`: copied from the project hub. Drafts the client email for each round: what's ready, the preview links and what to check. Sending needs Michael's or the team's say-so, as today.

### 6. Client review
- `client-review-release`: copied from the unmerged branch `feat/client-review-release`, dated 15 October 2026 and never merged to `main`. It installs four client skills into the client repo:
  - `start-website`
  - `review-website`
  - `share-preview`
  - `finish-review`

  It also installs the client README and an approval register. In the new layout those skills go in `skills/`, and the README becomes the repo's main `README.md`. The toolkit's human checklist (`CLIENT-REVIEW.md`) becomes `brain/Project.md`. The machine register (`client-review.json`) stays in `.lhm-review/` and is what actually records approvals, so a ticked box can't be faked by editing the Markdown.
- Flow:
  1. The client opens their AI project and runs `start-website` or `review-website`.
  2. It reads `brain/Project.md` and walks the client through each page awaiting review.
  3. The client edits with their AI and approves pages, which get ticked off in `Project.md`.
  4. `share-preview` and `finish-review` commit and push to `main`. There are no review branches during staging.
  5. `finish-review` drafts a short email to LHM.

### 7. Update content brain
- `update-content-brain` (new). Runs after the client has pushed their review. It reads the **client's own commits** on `main` since the last processed commit recorded in `Change Log.md`. It identifies them by the client's GitHub account, as opposed to LHM's. Then it sorts each change:
  - **Facts** (new staff member, changed price, dropped service) → update the matching note (`Staff.md`, `Services.md` and so on).
  - **Writing preferences** (always cuts the second paragraph, never uses "holistic") → add or strengthen a rule in `Content Rules.md`. Each rule carries how many times it was seen and a link to the change that showed it.
  - **Every run** → a `Change Log.md` entry: date, commit, what changed, what the brain learned.

  It shows the proposed brain changes before writing them, and commits to the client repo.

## Constraints

- **"ChatGPT" means the Codex side of ChatGPT.** Plain ChatGPT web chat cannot open or edit a repo. The README and skills must work in Codex, Claude (Claude Code / desktop) and Gemini (Gemini CLI). The existing client toolkit covers Codex and Claude Code, so Gemini is new.
- **Plugin housekeeping, per the repo CLAUDE.md:**
  - Add `lhm-astro-hub` to `.claude-plugin/marketplace.json` and give it its own `plugin.json`, starting at `1.0.0`.
  - Update the README skill counts and catalogue.
  - Add the new skills to the marketing assistant's catalogue.
  - The version validator finds plugins automatically. Update the plugin list in CLAUDE.md, which is already out of date.
- **Script parity.** The copied sitemap scripts are meant to change, so they are **not** added to the `PARITY_GROUPS` in `validate-script-parity.py`.
- **Existing rules carry over.** The client file routing contract (`obsidian-context-contract.md`), no invented facts, Australian/AHPRA copy rules, and approval before any push to a client's live branch, sending email or deploying to production.

## Calls made after the builder check (Claude's, for Michael to check)

- **Everything goes to `main` during staging** (Michael's decision). Content rounds and client edits push straight to `main`. There are no round or review branches.
- **The brain only learns from the client** (Michael's decision). It reads only commits made by the client's GitHub account, so LHM's own copy is never learned as a client preference. The Change Log records the last commit it processed.
- **Project.md lives in the brain** (Michael suggested it). The JSON register in `.lhm-review/` stays as the real approval record behind it (my call, carried over from the existing toolkit).
- **Not decided yet:** what changes once the site goes live on the client's real domain. Pushing client edits straight to `main` would then mean straight to the live site. That's out of scope for this build. Flag it before the first client launches.
- **Gaps in the brain during a content round.** Use the brief's fallback wording on the page and list the gap in the client email as a question, the same as `lhm-page-rollout` does today. Never invent the fact. Inside the brain itself, gaps stay marked as gaps.
- **What to take from `feat/client-review-release`.** Only the `client-review-release/` skill folder and its references. The QA skills are copied from `main`.
- **GoHighLevel setup is LHM's job.** LHM answers "does the client have GoHighLevel?" during the build and does the setup. The client never does a setup step.
- **Which copy wins where there are duplicates.** `client-update-email` comes from `lhm-project-hub`. `anti-ai-writing-guidelines.json` and the 8-pass engine come from `lhm-marketing-hub`. `astro-build-standard.md` goes into the new plugin's `references/`.

## Left to the builder

- Exact frontmatter fields for each brain note, and the template text.
- How `start-astro` detects the current stage (files present, a state file, or both).
- How the GoHighLevel connection works: webhook versus API, and where the client's key is stored. Never in the repo.
- The order skills are copied in, and how each copied skill is trimmed of WordPress and LHM-site-specific references.
- Tests for the copied scripts (sitemap generator, review register) and for the brain diff sorting.

## Approval points (where the process stops for a human)

1. Sitemap approved.
2. Prototype approved by the client.
3. Deploy to the client's Cloudflare production.
4. Brain draft approved before the first commit.
5. Each content round's page list and template. Then either the first-page mock-up or "batch the lot".
6. Each client email before sending.
7. Each `update-content-brain` proposal before it's written.
