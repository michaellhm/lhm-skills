---
name: website-content-agent
description: Orchestrate client website content batches from existing-site research and campaign positioning through page briefs, copywriting, independent anti-AI editing, healthcare advertising review and Astro integration. Use for 'website content agent', 'roll out Meet Us or What We Do', 'client copy review', 'content approval tracker' or 'learn from client website feedback'.
---

# Website Content Agent

Run a client website's content programme with persistent page status and client feedback. Discover the client's implementation instead of assuming LHM's own site paths. Support setup, batch production, client review, learning capture and resume modes. Follow the user's requested mode and scope; setup does not start writing pages automatically.

## Establish project context

Read [client routing](../../references/obsidian-context-contract.md), the repository instructions and Git status. Resolve the website repo, client knowledge folder and working folder. Load the campaign playbook, client profile, selected sitemap/navigation, project decisions and existing approved pages. Preserve unrelated local edits. Record the discovered paths and commands in `docs/website-content/project.md`; never bake client paths into this skill.

Before writing, read [project state](references/project-state.md). Initialise missing records without overwriting existing feedback. Inventory every selected sitemap destination, deduplicate shared routes and distinguish existing pages, missing pages and updates. Existing content is not evidence of client approval. Preserve user-approved work and record unknown approval as unknown.

Read learnings before every batch. Inspect the rendered reference pages and source components to establish one template contract per page family. Services, audiences, conditions and company pages may use different contracts. A menu grouping does not determine a page's template: an expanded-discipline link may target a condition hub. Record required sections, optional modules, media rules, content data shape, booking destination, links, metadata and schema. Structure should be consistent; copy should address each page's actual subject.

Confirm only material unknowns: batch scope, reference template or publication destination. Continue independent inventory/research while awaiting answers. Respect previously granted authorisation. Default to local output when publication destination is unresolved; do not infer permission to merge or deploy from a request to write copy.

## Orchestrate the batch

Read [agent handoffs](references/agent-handoffs.md). Use separate subagents for the research/comparison, brief, copy, anti-AI edit, healthcare review and integration stages when delegation is available. Writers and reviewers produce artifacts, not concurrent website edits. One integration agent owns repo mutations. Parallelise independent pages only within available capacity, keeping each page's dependent stages sequential. If delegation is unavailable, perform stages separately and disclose that independent review was not performed.

Save per-page outputs under `docs/website-content/pages/<page-key>/`: `research.md`, `brief.md`, `copy.md`, `editor-review.md`, `compliance-review.md`, `integration.md`. Update state after each completed stage. Send each agent the relevant template contract, source pack, client learnings and current artifact rather than relying on conversation history.

1. Compare the current live page, existing new-site copy and campaign direction. Verify live pages rather than trusting saved URLs. Record retain/change/remove decisions with sources, factual gaps and conflicts. The playbook supplies positioning, not clinical evidence or permission to repeat risky claims.
2. Produce the brief from the family contract. Include goal, search intent, outline, substantiated facts, permitted claims, media/practitioner mapping and confirmed links. Preserve useful existing copy; do not rewrite a completed page merely because it is in the batch.
3. Write copy from the accepted brief. Read the applicable `page-copywriter` or `seo-content-writer` skill when available and the bundled [anti-AI guidelines](../../references/anti-ai-writing-guidelines.json). Do not invent staff credentials, locations, service availability, testimonials, prices, evidence or outcomes. Missing facts belong in internal notes; use truthful bounded copy or defer the affected section.
4. A fresh editor applies the writing guidelines and client voice while preserving factual meaning. Return edits and rationale. No formulaic word count or identical prose across pages.
5. For healthcare advertising, a separate reviewer verifies current official AHPRA/National Board guidance and relevant evidence. Assess titles and credentials, clinical testimonials, misleading claims, unreasonable outcome expectations and unnecessary treatment encouragement. Adding 'may help' does not substantiate a claim. Apply profession-specific rules where relevant; do not imply every allied-health profession is AHPRA-registered. Return issues, sources and publishability status, not a legal certification.
6. Return failures to the writer, then recheck changed text with the relevant reviewer. Do not integrate unresolved material claims. After two unsuccessful correction cycles, document the precise blocker and continue unaffected pages.
7. Integrate passing drafts using the existing Astro renderer/content schema. Follow current site booking routes and URL conventions. Use real verified practitioner media only where relevant; never infer a practitioner treats a condition from a video title. Do not manufacture a video play button when no playable media exists.
8. Build and run relevant existing checks. Inspect desktop/mobile rendering, image loading, headings, internal links and booking navigation. Existing planned 404s outside the batch are recorded separately; new pages and their required links must resolve. Validate visible metadata/schema claims as well as body copy.

A checked draft is not client approved. Publication to an authorised review prototype is allowed before client approval when explicitly requested, while client status stays pending. Detect whether pushing main auto-deploys a prototype or production; record destination and effect before publishing. Push only within authorised scope, verify the remote SHA, deployment result and rendered new URLs. Report queued/failed deployment accurately. Do not send review email or messages without explicit user authorisation.

## Client review and learning

Read [project state](references/project-state.md) for approval and `/learn` semantics. Ask the client to review a specific page revision. Save feedback and proposed edits, run relevant writing/compliance checks again and invalidate approval when reviewed content changes. Capture general preferences separately from page-specific factual corrections. Client approval of wording does not override compliance findings.

Keep private learning records outside public assets and route generation. This skill does not provision a client portal, authentication or client ChatGPT access. Build a separate authenticated review interface only when requested; expose each client's own drafts and feedback, not internal notes or credentials. Learning updates stay client-local unless the user explicitly requests a shared skill change.

## Complete or resume

Read the tracker and artifacts before resuming; verify repo/deployment state instead of assuming prior agent output landed. Update `action-plan.md` with completed pages, next batch, blockers and exact resume instruction. Report drafts, client approvals, integrated pages and deployed pages separately. For a new chat, hand off project record paths and the next task; do not create the chat unless asked.

## Return the batch to project coordination

After every batch, return exact page revisions and review URLs, draft/checked/client-approved/integrated/deployed states, verified checks, feedback and client learnings, blockers, next batch and next review owner. Save confirmed client facts and durable decisions in shared Obsidian under the client routing contract; retain repository production trackers without treating them as the shared client brain. Prepare a concise handback for the existing BasicOps execution task through basicops-task-manager when authorised; otherwise return it ready for posting. Do not mark the website complete from a finished content batch or post client messages without authority. Kristalyn retains project/board coordination; Aiya's production work does not automatically transfer client communication ownership.
