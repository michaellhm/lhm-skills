---
name: client-data-collection
description: "Sets up the Data Collection step of new web client onboarding — creates the client's Drive folder and credentials tracking sheet, files the BasicOps Data Gathering task with the standard access checklist (including Cloudflare), drafts the data-gathering email, and sets up a weekly automated follow-up so nothing gets missed. Use this when the user says 'start client onboarding', 'new client data gathering', 'set up new client folder', 'collect client access', 'chase client for credentials', 'data gathering for [client]', or is starting a new web client right after Michael's welcome email has gone out. Phase 0 of the web project onboarding flow — runs before client-context-intake."
---

# Client Data Collection

Automates Step 2 (Data Collection) of the team's client onboarding flow for new web project clients: the Drive folder, the credentials tracking sheet, the BasicOps checklist task, the data-gathering email, and the weekly follow-up that chases outstanding items until everything is in.

Design rationale and decisions: `${CLAUDE_PLUGIN_ROOT}/../../docs/brainstorms/2026-07-23-client-data-collection-brainstorm.md`

## Scope

Only Step 2 of the team's 6-step flow (Welcome → **Data Collection** → Cloudflare → Digital Audit → Project Plan → Strategy Session). Michael's welcome email, actual Cloudflare account signup/DNS, the digital audit, project plan, and strategy session are separate work and out of scope here.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/client-data-collection/LEARNED.md` if it exists and apply any relevant entries.

Confirm Michael's welcome email has already gone out to the client — this skill is the first thing Kristalyn does after that, starting the data-gathering thread.

## Tool Access

BasicOps, Google Drive, and Gmail are used as MCP connectors. Their tool names are connection-specific (not fixed across sessions), so **use `ToolSearch` to locate them by capability** rather than assuming exact tool names — e.g. search "create_task project management" for BasicOps, "create_file drive folder" for Drive, "create_draft gmail" for Gmail. The `scheduled-tasks` MCP server name is fixed and can be referenced directly (`create_scheduled_task`, `delete_scheduled_task`).

## Step 1: Identify the Client

Ask (if not already known): business name, primary contact name and email.

Before creating anything, search Drive for an existing folder under `Campaigns/` matching the client's name to avoid duplicating a prior setup.

## Step 2: Create the Drive Folder and Credentials Tracking Sheet

1. Find the `Campaigns` folder under `My Drive > Local Health Marketing` by searching for a folder titled `Campaigns` — don't hardcode its ID, confirm it live.
2. Create a new folder inside it, named after the client's domain (matching existing convention, e.g. `ClientName.com.au`).
3. Inside that new folder, create a spreadsheet titled `[Client Name] - Access & Credentials Tracker` with one row per checklist item:

   | Item | Status | Value / Notes | Date Received |
   |---|---|---|---|
   | Logo | Not Started | | |
   | Staff Images | Not Started | | |
   | Clinic Images | Not Started | | |
   | Google My Business Access | Not Started | | |
   | Google Search Console Access | Not Started | | |
   | Google Analytics Access | Not Started | | |
   | Google Ads Access | Not Started | | |
   | CMS Access | Not Started | | |
   | Domain Host Access | Not Started | | |
   | Website Host Access / cPanel | Not Started | | |
   | Cloudflare Access | Not Started | | |

This sheet is separate from the existing `LHM Master List - Campaign Profile Access` (the cross-client master list at the `Campaigns` root) — leave that file untouched.

## Step 3: Create the BasicOps Data Gathering Task

1. Locate the `*Web Projects` project and its `Onboarding & Briefing` section by title — confirm live rather than hardcoding (as of 2026-07-23 these were project id `68635`, section id `107719`, but IDs can change).
2. Create a task titled `Data Gathering — [Client Name]` in that project/section, assigned to Kristalyn, with the Drive folder linked (`driveFolder` field).
3. Add one subtask per checklist item above (same list as the tracking sheet), each starting unchecked.

This BasicOps checklist — not the tracking sheet — is the source of truth the weekly follow-up checks against for completion.

## Step 4: Draft the Data Gathering Email

Before writing, read the anti-AI writing guidelines at `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/references/anti-ai-writing-guidelines.json` (mandatory for all written output per this plugin's `CLAUDE.md`). This email is short and transactional — well under 300 words — so it's exempt from the 8-pass writing engine, but still follow the anti-AI quick-reference rules (no em dashes, vary sentence/paragraph structure, no cliché pairings).

Draft — never send — an email in Gmail to the client's primary contact (cc Kristalyn) covering:

- A short intro referencing Michael's welcome email
- The checklist items needed: Logo, Staff Images, Clinic Images, Google My Business Access, Google Search Console Access, Google Analytics Access, Google Ads Access, CMS Access, Domain Host Access, Website Host Access/cPanel, and **Cloudflare Access** — ask whether they already have an account; if yes, request admin access for `michael@localhealthmarketing.com.au`; if not, note the team will help set one up later (that part stays manual)
- A link to the **Essential Logins** form for credentials. **Ask the user first whether that form has been updated with the Cloudflare item yet.** If not confirmed, ask for Cloudflare access directly in the email body instead of relying on the form.
- A link to the client's **BrieflyFlow** task for the website-goals questionnaire. Remind the user this link is public and expires weekly — confirm it's freshly generated in BrieflyFlow before sending, or regenerate it first.
- A link to the trimmed intake form, only if one exists for this client — don't link the old, redundant version if a trimmed one hasn't been prepared.

Show the drafted email to the user for review before moving on. Do not treat "drafted" as "sent."

## Step 5: Set Up the Weekly Follow-Up

Ask the user to confirm or adjust the schedule (default: every Monday, 9am, Asia/Manila).

Create a scheduled task via `create_scheduled_task`:

- `taskId`: `<client-slug>-data-gathering-followup`
- `description`: "Weekly check on [Client]'s Data Gathering checklist — drafts a follow-up email for outstanding items, or shuts itself off once complete"
- `cronExpression`: from the confirmed schedule
- `notifyOnCompletion`: true
- `prompt`: a fully self-contained prompt (runs with no memory of this conversation) instructing the future run to:
  1. Look up the BasicOps `Data Gathering — [Client Name]` task and list its subtasks
  2. If every subtask is complete: notify the user it's done, and delete this scheduled task via `delete_scheduled_task` on its own `taskId` — no further follow-ups needed
  3. If any are still outstanding: draft (never send) a follow-up email in Gmail to the client listing only the outstanding items, and notify the user a draft is ready for review

## Step 6: Report Back

Tell the user:

- The Drive folder and tracking sheet links
- The BasicOps task link
- That the data-gathering email draft is waiting in Gmail for review
- The weekly follow-up schedule, and that it self-cancels once the checklist is complete
- Recommend running a live test of the follow-up prompt now (via the Agent tool) rather than waiting for the first scheduled run, so any lookup or tool issues surface immediately

## Out of Scope (Stays Manual)

- Michael's welcome email (already sent before this skill runs)
- Actual Cloudflare account creation, DNS pointing, and adding `michael@localhealthmarketing.com.au` as admin — Claude cannot create third-party accounts; this skill only makes sure the *ask* for existing access happens and doesn't get missed
- Digital Audit, Project Plan, and Client Strategy Session steps — separate, not yet designed

## Rules

- Never overwrite an existing client's Drive folder or BasicOps task — check first
- Never auto-send email — draft only, always for review
- Facts only in the email — no invented client details
- If the `*Web Projects` / `Onboarding & Briefing` lookup fails (renamed, moved, or missing), ask the user rather than guessing a different location
