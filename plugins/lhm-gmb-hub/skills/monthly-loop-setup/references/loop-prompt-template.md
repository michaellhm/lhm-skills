# Monthly GMB loop — scheduled task prompt template

Fill in every `{{PLACEHOLDER}}` and paste the result as the `prompt` argument to `create_scheduled_task`. Delete whole sections marked OPTIONAL if they don't apply to this client (no site repo, no NotebookLM notebook).

---

You are running the monthly GMB (Google Business Profile) optimisation cycle for the client **{{CLIENT_NAME}}**. This is a recurring task — no memory of any prior chat exists, so follow these instructions exactly and read the referenced files fresh each run.

## 0. Orientation
- Working directory root: `{{CLIENT_FOLDER}}`
- Project management file (the source of truth for what's done/pending): `gmb/GMBProjectManagement.md`
- {{OPTIONAL: SITE REPO LINE}} Website repo: `{{SITE_REPO_PATH}}` (git repo, remote `origin` = `{{SITE_REPO_REMOTE}}`, default branch `{{SITE_REPO_DEFAULT_BRANCH}}`)
- {{OPTIONAL: NOTEBOOKLM LINE}} If you get stuck, hit an ambiguous decision, or need background on how this GMB process/infrastructure was built, consult the NotebookLM notebook FIRST before guessing: {{NOTEBOOKLM_URL}} (use the `notebooklm` MCP tools — `ask_question` etc.)
- Use the `lhm-gmb-hub` plugin skills/agents for all GMB-specific work (start with the `lhm-gmb-hub:gmb-orchestrator` agent — it detects the current phase from the PM doc and routes to the right phase agent: onboarding-agent for Month 0, service-optimizer-agent for Month 1, content-expansion-agent for Month 2, link-building-agent for Month 3). Also use `lhm-marketing-hub` skills where they're a better fit for a specific sub-task than the GMB-hub equivalent.

## 1. Read state
- Read `gmb/GMBProjectManagement.md` in full. Identify the current phase (Month 0/1/2/3) and which checklist items are unchecked.
- {{OPTIONAL: SITE REPO BLOCK}} Check the site repo's git status/log to understand what's already been done there. If `{{SITE_REPO_DEFAULT_BRANCH}}` has significant pre-existing uncommitted/untracked work that looks unrelated to this run, do NOT commit, discard, or otherwise touch it — note it in your Telegram update and the PM doc, and skip straight to any non-site tasks (GBP profile, citations, link building, diagnostics, reporting) instead. Only proceed with site-repo work once `{{SITE_REPO_DEFAULT_BRANCH}}` is clean.

## 2. Do the work
- Work through the current phase's unchecked checklist items in `GMBProjectManagement.md`, running the relevant `lhm-gmb-hub` skills/agents for each (e.g. `gbp-post-generator`, `citation-audit`, `entity-mapper`, `site-architecture-mapper`, `service-priority-selector`, `service-page-writer`, `technical-page-audit`, `run-local-diagnostic`, `faq-content-builder`, `neighbourhood-overlay-writer`, `link-gap-finder`, `local-authority-finder`, `pr-brief-generator`, `monthly-cycle-report`, etc. — pick whichever match the outstanding items).
- {{OPTIONAL: SITE REPO STAGING BLOCK}} **Site-editing staging workflow**: if `{{SITE_REPO_DEFAULT_BRANCH}}` is clean (see above), before making any site edits: `git checkout {{SITE_REPO_DEFAULT_BRANCH}} && git pull` then create/checkout a branch named `gmb-cycle-YYYY-MM` (year-month of this run) off latest `{{SITE_REPO_DEFAULT_BRANCH}}`. Make all site content/code changes on this branch only. Commit with clear messages. Push the branch to `origin`. Do NOT merge into `{{SITE_REPO_DEFAULT_BRANCH}}` and do NOT open a PR unless explicitly asked — a human merges the branch manually after review.
- GBP profile changes (categories, services, description, posts, Q&A, photos) and any other live/client-facing publishing action: complete the drafting/prep work, but if the action is irreversible or client-visible (e.g. actually publishing to the live Google Business Profile, or anything requiring the client's own login), stop short of executing it, prepare everything ready to go, and flag clearly what's ready and waiting.

## 3. Update the project management file
- After each task (or attempted task) this run, edit `gmb/GMBProjectManagement.md`:
  - Tick off `[ ]` → `[x]` for completed checklist items, with the date.
  - Add a short dated note under a "Notes & Watch-Items" or "Monthly Loop Log" section for anything relevant: what was done, what's blocked, what's waiting on the client/human, links to any new files produced.
  - If you moved into a new Month/phase, update the `Current Phase` field at the top.
  - This file must always reflect the true current state after your run — do not leave it stale.

## 4. Create a BasicOps follow-up task
Use the `basicops` MCP tools.
- Project: `{{BASICOPS_PROJECT_ID}}` (`*Client Flow`), Section: `{{BASICOPS_SECTION_ID}}` (`Delivery`)
- Create the main task via `create_task`: title `{{CLIENT_NAME}} - [Month Year] GMB` (e.g. "{{CLIENT_NAME}} - August GMB"), no description, assignee `{{BASICOPS_DEFAULT_ASSIGNEE_ID}}` (assigning triggers a real notification — don't rely on @mentions for this, see below).
- Post the run summary as a **discussion message** on that task via `create_message_in_task` (NOT in the `description` field) — HTML content covering: current phase/progress, what was completed this run with paths to any new files, what's blocked, what's ready for review, next steps. You can prefix with `CC: @Name @Name` for readability, but this is plain text, not a confirmed real mention — it will NOT reliably notify anyone. Rely on the `assignee` field for actual notifications until real mention syntax is confirmed.
- For each concrete follow-up action, create a **sub-task** (`parentTaskId` = main task ID) with a specific, assignable title (e.g. "Citation Audit - Execute Fixes", not "Citations"). Post the specific instructions for that sub-task as a **discussion message** on the sub-task (not its description) — be concrete: exact directories/URLs/files to touch, exact before/after values, not vague summaries.

## 5. Telegram update (every run, always)
Send a message to **{{TELEGRAM_CHAT_NAME}}** via the Zapier Telegram connector (`execute_zapier_write_action`, tool `telegram_send_message`). Resolve the chat_id dynamically each run: call `list_enabled_zapier_actions` with `tool_name: "telegram_send_message"`, `enum_property: "chat_id"`, `enum_search: "{{TELEGRAM_CHAT_NAME}}"` to get the current chat_id, then send. If the lookup returns no matches, note this clearly in the email report (step 6) instead of failing silently — someone needs to send a message in that chat to "wake up" the bot's visibility into it.
Content: a quick, human-readable summary (a few short bullet points) of what you worked on, anything you got stuck on or have questions about, and anything ready for human review/merge/publish. Keep it tight.

## 6. Email report (every run, always, after Telegram)
Send a fuller summary via Mailgun (`execute_zapier_write_action`, `selected_api: "MailgunCLIAPI"`, `action: "createEmail"`). Confirm the action is actually present via `list_enabled_zapier_actions` first — if it's missing or the connector needs re-auth, note that clearly instead of silently skipping the email.
- `from`: `GMB Optimisation Loop <gmb-reports@{{MAILGUN_DOMAIN}}>`
- `to`: `{{MAILGUN_RECIPIENTS}}`
- `subject`: `{{CLIENT_NAME}} — GMB Monthly Loop — [Month Year]`
- Body: current phase/progress, what was completed this run with links/paths to any new files, what's blocked or needs a decision, a direct link to the BasicOps task created in step 4, and next steps for next month.

## 7. Constraints (always follow)
- Never enter credentials, passwords, or payment details anywhere.
- Never merge to the default branch, never push directly to it, never publish anything live-facing (GBP live changes, client-facing emails, publishing blog posts) without this being an explicit unattended-safe action already described above — when in doubt, prepare and flag rather than execute.
- If something is genuinely blocking (repo not clean, a tool/integration down, missing data), still complete steps 3–6 (update the PM doc, create the BasicOps task, send Telegram, send email) reporting the blocker — never fail silently.
