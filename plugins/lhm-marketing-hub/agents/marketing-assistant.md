---
name: marketing-assistant
description: "Legacy entry point — routes to the start agent. Use /lhm-marketing-hub:start instead."
---

This agent has been replaced by the `start` agent.

Please use `/lhm-marketing-hub:start` to begin a marketing session.

Routing you to start now — read `${CLAUDE_PLUGIN_ROOT}/agents/start.md` and follow its instructions.

## Skill Catalog

`playbook-strategy-session` — Prepare and coach theme-led client strategy calls for campaign playbooks.

`prospect-sitemap-opportunity` — Proposed sitemap and interactive opportunity model for a prospect website pitch.

`client-sitemap-plan` — Phased website content plan for an existing client, same architecture without the sales widget.
`homepage-prototype` — Homepage concept prototype built from the proposed sitemap and live site, with personas brief and anti-AI design rules.

`google-ads-delivery-qa` — Verify bounded Google Ads evidence, implementation artefacts, approval boundaries and completion before the Lead advances.

`google-ads-implementation` — Apply approved Google Ads changes from a BasicOps task through AdPulse (Chrome fallback for PMax signals and conversion settings), verify, log to BasicOps, and triage AdPulse Insights/Optimize.

`start-seo` — Start or resume the reusable staged SEO department from a governed production envelope.

`seo-page-brief` — Turn accepted SEO research into a bounded, implementation-ready page brief package.

`seo-delivery-qa` — Independently verify SEO scope, evidence, artefact delivery, approval boundaries and completion before the Lead advances.
`website-content-agent` — Client website content orchestration: source comparison, user-selected reference templates, sitemap keyword/H1 mapping, briefs, copy, independent editing and healthcare review, Astro integration, client approvals, feedback learning and canonical project handback.

`lhm-page-rollout` — Build a batch of LHM website pages end to end (research, brief, copy, FAQ and schema, internal links, images, staging build, verification and review email). Staging only.

`run-hermes-task` — Include the named Claude Lead, required skills/connectors and verified startup capability receipt; the Lead invokes skills in the same conversation. Route a direct personal TED work request centrally to Claude for Google Ads and research/writing/planning, or Codex for other website/code/Workspace; retain the session, resume feedback, preserve drafts on explicit terminal provider handoff and return results to BasicOps without a separate TED plan. Resolve client aliases and source pointers from refreshed shared Obsidian context, including task Discussion briefs. Reuse named client/provider VPS workspaces recorded in the shared Obsidian workspace registry. Return verified Drive deliverable links through shared file delivery before a success handback; post existing-chat links early when the provider mapping is known; preserve existing pilot chats and scoped delivery/publishing permissions.

`hermes-production-plan` — Match an existing BasicOps outcome to its Obsidian AI Operations SOP, prepare the execution plan for Ted, and provide plain-English task status and CTO blocker reporting.

`basicops-task-manager` — Write short, plain-English task briefs for the LHM team; apply task routing, approvals and verification.

`drive-artifact-delivery` — Deliver approved production files to the registered client Google Drive folder with exact metadata and content readback.

`lhm-system-ops:lhm-skill-maintainer` — Govern an authorised LHM skill change through canonical source edits, validation, feature-branch PR delivery, approved deployment and live verification.

`lhm-wordpress-hub:wp-rest-operator` — Inspect and implement registered WordPress or LeadScale content changes through the REST API with snapshots, publish separation and readback verification.

`pre-client-meeting` — Sweep wraps, client replies, boards, Obsidian and implementation evidence into short meeting speaking bullets: progress, next work, decisions and campaign wins/watch-outs; finalise the shared Google Doc and calendar link after host feedback.

`meeting-to-action` — Scope-check explicit LHM commitments and delivery dependencies before interactive meeting task reconciliation, outcome delegation and guided execution of Michael’s retained actions, with a final BasicOps/Obsidian/Drive close-out prompt.
`post-meeting-review` — Josephine captures one meeting card with the full email and proposed actions in Discussion; Michael reviews and delegates through meeting-to-action.

`weekly-web-project-brief` — Lily’s Monday HTML website portfolio: 07:00 Melbourne preparation for 08:00 delivery, project health, client-grouped actions, visible clarification notes and a verified shared Obsidian snapshot. One-off fixes stay out of the snapshot. Failure supervision distinguishes current-week evidence from retained service state.

`lhm-content-engine:weekly-social-carousel` — Build a privacy-safe editorial backlog from Fathom and current developments, rank ideas by audience frequency and value, then turn selected topics into reviewed LHM HTML and PNG carousel packages.

`google-ads-monthly-review` — Evidence-led account review, report highlights and Lily’s Monday review-card digest.

`lhm-gmb-hub:monthly-cycle-report` — Goal-led monthly SEO investigation, consolidated multi-location work plan, phase close-out, meeting/task reconciliation and AI coaching pack. Portfolio Monday scheduling uses GMB `monthly-loop-setup` with a dedicated CLI-only analytics, delivery and independent-QA runtime plus a card-first Lily/Mailgun HTML digest.

`analytics-tracking` — Investigate website, GTM, GA4 and Ads event sources; prepare success-only enquiry tracking, validate GTM imports and verify attribution and duplicate conversion checks.

### Client knowledge and work routing

Client-facing skills read and update shared LHM Knowledge client records; deliverables use verified Claude Workspace/Current Clients folders. `client-meeting-email`, `post-meeting-review`, `client-update` and `drive-artifact-delivery` distinguish these roots, preserve meeting approval gates and report canonical-record writeback gaps. Local, Cowork and Hermes runs must use verified platform-specific roots rather than a current-directory fallback.

`staff-weekly-flow` — Use the current People profile’s responsibilities, authority, handoffs and working preferences when recommending priorities; visibly verify the current Monday brief and save its source receipt, use authorised email fallback when needed, reconcile every agreed task and existing weekly card, offer immediate authorised unblock communications, and use one decision or the requested small batch at a time. Role-specific Monday coaching from the current shared web brief: Michael’s decisions, Kristalyn’s reviews/client follow-ups, Aiya’s last-week closure and realistic commitments; save voluntarily chosen commitments and dated results in shared Obsidian, review last week supportively, save settled project updates incrementally to canonical client records, verify authorised BasicOps changes through the task manager, reconcile destination gaps and finish with a Tuesday web meeting document. Michael’s business review is separate.

`lhm-knowledge-hub:lhm-weekly-flow` — Separate founder/business weekly review with strategic outcomes and private reflection; use staff-weekly-flow independently for Michael’s and the team’s chosen work commitments and daily selection.

`lhm-knowledge-hub:lhm-daily-flow` — Daily full task/reply and email-thread pre-sweep, prepared responses, team blockers first, portable prompts with verified agent/skill routing and per-task Learn for two or three chosen tasks before email work, email filing, reviewed 5/10-day Waiting On follow-ups and end-of-day Learn for client context and interaction preferences. Reports unsaved checkpoint deltas and bounds app access without bypassing denials.

## AI recommendation visibility

- `ai-recommendation-loop` — Generic buyer-question baseline, diagnosis, authorised staging changes and review handoff, monthly recommendation scoreboard. Route to the SEO Lead.


Monday coordination uses a separate receipt-gated board reconciliation after the read-only website report. It posts deduplicated project summaries; Kristalyn owns shared-board accuracy, and Staff Weekly Flow confirms personal weekly commitments.

### Agency loops (`lhm-loops-hub`)

- `website-project-loop` — Monday website board review after verified report delivery/archive; receipt-backed summary comments. Explicit checklist completion stays in `website-project-cockpit`.

### Website completion QA (`lhm-wordpress-hub`)

- `site-launch-qa` — Combined coached completion QA: client requests, full-site SEO, sitemap/robots repair and GSC verification, Jaimee’s phone review, tracking evidence, fixes and retests.
- `visual-qa` — Browser screenshots and design/responsive checks plus guided phone checks feeding the combined report.
- `website-delivery-qa` — Verify the delivery workflow and evidence; require completed human, client-request and tracking checks for final-site handback.

### Client website review releases (`lhm-wordpress-hub`)

- `client-review-release` — Install portable client review skills, scan new/changed/pending pages, propose release questions for operator approval, preserve explicit client approvals and prepare staged GitHub-access, local-setup and review emails with verified sharing routes.

Approved Claude implementation handoff: exact human approval plus task/source context reaches a connected Remote Control conversation; TED forwards it without an extra plan gate. Native tool approval remains with Claude. Existing draft-only receipts are not silently upgraded.

`lhm-cto` — Investigate capability incidents, then hand the findings and original outcome to one Intervention task with a linked paired Codex repair chat; retain Michael’s merge and deployment authority.

`lhm-system-ops:hermes-site-workspace` — Set up or resume one website checkout on Hermes, lock it across Claude/Codex and publish through scoped GitHub App access according to build/live mode.
