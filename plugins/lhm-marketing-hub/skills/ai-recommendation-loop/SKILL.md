---
name: ai-recommendation-loop
description: Measure and improve a client's visibility in AI business recommendations using repeatable buyer questions, captured answers and citations, verified positioning, website content and third-party evidence. Use when the user mentions 'AI recommendation loop', 'ChatGPT visibility', 'AI visibility baseline', 'get recommended by ChatGPT', 'AI search monitoring', 'recommendation scoreboard' or 'monthly AI visibility review'. Supports any industry, geography and website platform, with authorised staging changes, reviewer email and a deduplicated BasicOps review task.
---

# AI recommendation loop

Turn observed buyer answers into an evidence-led improvement cycle. Work for any verified client, including LHM. Never promise inclusion, rankings, attribution or a revenue return.

## Modes and dependencies

- `baseline`: resolve context, freeze buyer questions, collect actual engine responses, calculate the initial scorecard.
- `diagnose`: inspect supplied responses and source pages; produce a prioritised evidence-backed change brief.
- `implement`: deliver the agreed changes to the registered staging environment, verify them and send the authorised review handoff.
- `review`: repeat the fixed panel, compare comparable runs, reconcile work and select the next bounded actions.
- `schedule`: configure the approved recurring run after checking existing schedules and runtime capabilities.

Read plugin rules and `references/obsidian-context-contract.md`, `references/delivery-artifact-contract.md`, `references/anti-ai-writing-guidelines.json`, `references/seo-departmental-delivery.md` and `references/content-departmental-delivery.md` relative to the plugin root. Read the current SEO agent learning file. Use the templates in [references/run-contract.md](references/run-contract.md) and the workflow checks in [references/acceptance.md](references/acceptance.md).

## 1. Resolve the client and authority

Read the canonical client facts, services, goals, current projects, previous AI runs and website delivery records. Reuse supplied verified context; do not repeat discovery. Resolve business name/aliases, URL, category, buyer, geography, language, offers, proof and competitors. Include regulated-industry requirements when relevant; do not apply healthcare rules to other businesses.

Resolve the registered report destination, canonical state file, website repository/CMS, staging environment, reviewer identity/email, BasicOps project/parent and authorised actions. Keep client-specific paths, IDs and email addresses in the run configuration, never this skill. Record each destination's source record and verify access. Do not substitute the working directory for a client destination.

A request to run this skill permits research and saved internal analysis. Website edits, staging deployment, email sends and task creation require their respective existing authority. Record the authorising message or envelope; honour prior authorisation without asking again. Staging authorisation never authorises production deployment, merge, external profile changes or outreach. A schedule preserves its client's recorded scope; it does not create new authority.

Missing input blocks only the dependent stage. Preserve a concrete draft/change brief and exact resume point. Do not fabricate a destination, reviewer, price, proof, claim, credential or competitor fact.

## 2. Freeze a useful buyer panel

Start with 12 questions and three independent runs per question per engine, unless an agreed budget specifies otherwise. Expand to 30 questions only when the research warrants the cost. Cover recommendation, comparison, alternative, problem-first and branded verification intents. Include the buyer's actual constraints, location and niche; do not insert the client's name into discovery questions. Choose competitors from verified market evidence and observed answers, with the initial selection labelled provisional.

Tag every question as `discovery` or `branded`. Include at least six discovery questions and two branded questions. Record a stable ID, exact wording, intent, buyer scenario and evidence for its relevance. Keep the core panel fixed, including questions we win. Test new questions in a separately reported exploratory panel. Changing wording creates a new panel version; never overwrite history.

## 3. Capture real answers

Use fresh conversations with memory/personalisation off where supported. Record engine, consumer UI or API surface, displayed model (or `unknown`), timestamp, timezone, language, location setting, account/session conditions, search setting and observed search behaviour (`yes`, `no`, `unknown`). Temporary chat reduces history effects; it does not control every source of variation.

Run one question per fresh conversation, three times. Store the exact prompt, full answer, every citation URL, named businesses in answer order and qualifying wording. An API/web-search test is a separate series from the consumer ChatGPT interface. Never relabel this agent's web research as measured ChatGPT, Gemini, Perplexity or Google AI answers. Never infer 'training memory' from a missing search indicator, or claim a specific underlying search index without current official evidence.

Use an available supported connector, browser or authorised evaluation service. If collection cannot run, return `waiting_on_capability` with a ready question panel and results table. User-pasted full answers are acceptable; record provenance. Empty rows and failed requests are missing observations, never negative results. Do not fabricate answers or recommendations. Keep raw responses as evidence and exclude sensitive client/customer data.

## 4. Calculate the scorecard

Apply the definitions in the run contract and use its bundled `scripts/scorecard.py` calculator after evidence classification. Separate discovery from branded results and each engine/surface/model/panel. Report total expected, valid and failed runs, dates and per-question coverage. Three repetitions are an initial directional baseline, not statistical certainty.

Report mention rate, explicit recommendation rate, accurate recommendation rate, misdescription count, mean position when named, citation rate for the client's site, competitor share of mentions and cited-domain frequency. Treat unordered names as unordered; do not invent rank. Verification of a named brand is not an unsolicited recommendation. Keep source citation and business recommendation distinct.

Compare only equivalent panels and conditions. Report model/surface/setting changes as breaks in the series, and changed sample coverage as a limitation. Never pool engines to conceal losses. Preserve both counts and denominators; percentage-point changes use comparable rates.

## 5. Diagnose observable gaps

For each proposed action link the question/run, answer excerpt, cited page and verified site/profile evidence. Classify as observed fact, hypothesis or missing evidence. A citation is a useful lead, not proof of trust weighting or the reason for exclusion. Never state that a competitor won for a particular reason unless that reasoning was explicit in the captured answer; even then label it the answer's stated rationale.

Assess positioning/factual accuracy, answer coverage, proof/pricing clarity, source presence and technical access. Verify official crawler guidance at execution time. Distinguish OAI-SearchBot search access, ChatGPT-User user-triggered access and GPTBot training access. Search access does not require enabling training. A robots.txt rule is not proof that a CDN admits the bot; inspect verified settings/logs when available and report unknowns.

Check relevant indexing, canonical URLs, sitemap, initial rendered content and production bot access. Inspect existing schema against visible facts and applicable schema rules. No special AI schema or llms.txt is a guaranteed visibility lever. FAQ/rating markup must meet current platform eligibility and never invent review aggregates. Keep staging protected from indexing; crawler improvements are proposed for production release, not public staging exposure.

Produce a verified fact set and a specific, supportable positioning statement. Keep facts consistent across channels; adapt length and wording to each channel. Unapproved strategic positioning remains a proposal. Select a small batch by evidence, buyer value, effort and dependency. Read full page content, including service/condition subsections, before declaring an answer gap. Improve existing pages before proposing duplicates. Prices, comparisons and FAQs are conditional on buyer evidence, not compulsory page types. Use verified professional credentials and titles, including in comparison pages. No arbitrary word counts or keyword stuffing.

## 6. Prepare content and third-party work

Create an accepted content brief with targeted questions, factual sources, proof, current page, intended change and success check. Route customer-facing final words through the Content Lead and its writing/QA process. Only `implementation_ready_copy` with factual, brand, compliance and channel checks goes to development. No unselected suggestions, placeholders or unsupported claims may appear on staging pages.

Use `geo-content-optimizer`, `seo-page-brief`, `schema-markup`, `content-gap-analysis` and appropriate WordPress/Astro capabilities as needed. Reuse the existing departmental sequence; read the selected capability before dispatch. Do not apply LHM-specific rollout branches, slugs, prices or rules to another website. Resolve the client's own implementation route.

Rank third-party opportunities by observed citations, buyer relevance, feasibility and editorial independence. Competitor sources not cited can be exploratory targets, labelled as such. Check source pages before drafting inclusion pitches. Review requests must be genuine, ungated and compliant with current platform rules. Community participation requires affiliation disclosure and useful answers. Do not fabricate reviews, pay for undisclosed endorsements or create fake community histories. External profile writes, outreach, review requests and community posts require separately recorded authority; draft them when absent.

## 7. Implement to staging and verify

When staging changes are authorised, carry them through without another routine confirmation. Read website repository instructions and Git status, preserve unrelated work, resolve the staging branch/registered server and retain the pre-change commit or CMS backup. Inspect pending website work and existing deployments to avoid conflicting changes. Keep the batch bounded to diagnosed gaps and agreed scope.

Use the registered platform's build, link, accessibility and relevant content/schema checks. Review factual accuracy and screenshots for affected layouts. Push/deploy to the registered staging destination using existing authenticated tooling. Wait for the specific candidate commit's successful deployment, then fetch affected pages, links and images; verify rendered changes and staging access/indexing protection. A push is not a successful deployment. On failure preserve evidence, fix within scope or return the exact blocker. Never send broken staging links as ready for review.

Persist change log: old/new reference, rationale, targeted questions, copy acceptance, commit/revision, deployment ID, verified staging URLs, checks, rollback and release status. Keep states distinct: built, pushed, staged_verified, review_pending, approved, production_verified. Production requires explicit release authority and verification. Staging changes are not exposure to AI engines and must not be credited with visibility improvement before production release.

## 8. Reviewer email and BasicOps handoff

After staging verification, use the recorded authorised recipient and an available authenticated email connector to send one review email. Include clickable staging links, plain-English changes and reasons, checks passed, remaining decisions, rollback summary and the specific review request. State that production release is pending. Verify the returned sent message ID; distinguish draft, sent and failed. If sending fails, save the exact email and record `notification_pending`; do not pretend a draft was sent.

When review-task creation is authorised, read `lhm-project-hub:basicops-task-manager` and use its identity, naming, description, discussion and verified routing contract. Search for an equivalent open review task before creating one. Reuse/update one reviewer task per client/batch; link an existing website cockpit when applicable. Discussion carries the human brief, staging links, evidence, completion condition and next handoff. Do not invent a due date or create a checklist task tree. Read back the task and return its actual URL. Use a stable private dedupe key per client/batch/review. If task creation fails, preserve the payload and report that separately from email/deployment results.

Record reviewer feedback against the reviewed revision. Apply authorised staging corrections, reverify and update the same review task. A task status or email reply without explicit release approval does not authorise production. Prevent duplicate notifications on resumed runs: record sent IDs, task IDs and notified revision; send again only for a new reviewable revision or meaningful change.

## 9. Monthly review and business outcome

Repeat the fixed panel, reconcile production changes and third-party work with exact dates, and identify evidence consistent with improvement. Attribution is a hypothesis with confidence and alternative explanations (model changes, retrieval variation, competitors and indexing delay). Never assign revenue value to one percentage point of mention rate without an independently justified measurement model.

Report AI referral sessions, self-reported discovery and qualified leads when available, with their attribution limits. Do not treat branded traffic as proof of AI discovery. Propose a discovery-source field only when appropriate to the client's measurement setup and existing authority. Decide continue, adjust, pause or investigate for each active work item; keep fixed-panel questions regardless of success. Record next actions, owner and milestone.

## 10. Scheduling

Recommended cadence: monthly fixed-panel measurement, quarterly positioning/content/source review, and a weekly readiness check only while implementation/deployment/review is pending. No weekly full-panel testing by default. Initial pilot: baseline before changes and checks at roughly 30, 60 and 90 days. Report indexing/exposure time since production release.

For Codex, use `automation_update` and inspect existing `$CODEX_HOME/automations/*/automation.toml` before creating a duplicate. Use a thread heartbeat unless the user explicitly wants standalone jobs. Other runtimes use their supported scheduler and recorded profile, never a made-up cron or automation directive. Resolve client, state path, panel/version, engine collection route, budget, timezone, cadence and authority first. Do not describe a saved schedule as a verified unattended collector.

If the user asks whether scheduling is sensible, recommend the cadence; that question alone is not authorisation to activate recurring mutation or sends. When asked to set it up, preserve confirmed scope and configure the schedule. Missing baseline/collection access means the first run establishes the baseline or returns a specific capability request; never produce simulated trends.

Each recurring run reads the state, resumes only dependency-ready authorised work, respects pending approval, saves/readbacks evidence and avoids repeating notifications/tasks. Stay quiet when unchanged or non-actionable. Notify on a meaningful result, verified staging batch, failure or required human action. Pending review does not grant release approval and does not trigger reminders unless reminders were authorised. Record scheduler ID, next run and timezone; explain whether collection and implementation are ready.

## Handback

Return canonical state (`completed`, `needs_context`, `needs_approval`, `waiting_on_capability`, `failed`), mode, coverage, verified artefact references, scorecard limits, actions shipped, commit/deploy evidence, review task URL, email state/ID, schedule state/ID, approval needed, next owner and exact resume point. Apply the plugin's delivery-contract projection. A prepared baseline is not collected; staged changes are not released; a configured schedule is not a completed measurement run.

## Official technical references

Recheck at execution time: [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots) and [Google AI features guidance](https://developers.google.com/search/docs/appearance/ai-features). These support technical access and content guidance, not promises of recommendation inclusion.
