---
name: playbook-strategy-session
description: Prepare and coach theme-led client onboarding interviews from a sales-call transcript and existing client context, gathering source material for website copy and an LHM Master Campaign & Sales Playbook. Use when the user says "prepare the client interview", "use Marlon's sales call", "onboarding interview", "strategy session", "business brain", "website content interview", or "sentence preference exercise". Produces tailored questions, a ten-sentence yes/no/unsure table, a meeting pack and a live-coach prompt; can prepare authorised Obsidian context without running the sales handover.
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Playbook Strategy Session

Prepare a natural, theme-led conversation rather than a fixed questionnaire. Let broad invitations surface stories, language and beliefs; use focused prompts only to fill material gaps.

## Required companion

Use `campaign-playbook-generator` after the meeting to create the finished Master Campaign & Sales Playbook. This skill owns preparation, live coaching and transcript handoff; it does not replace the generator.

## Workflow

### 1. Resolve the client and sources

Identify the canonical client name before writing. Read available sources completely:

- canonical Obsidian client overview, profile, goals and current projects;
- onboarding, sales handover and previous meeting records;
- Google Drive client folder, intake responses, research and working files;
- proposed sitemap, website brief and keyword research when relevant;
- existing campaign playbook, if present; and
- meeting transcripts or ChatGPT exports supplied by the user.

Prefer Obsidian for durable client context and Drive for working files and deliverables. Treat site research and one-sided meeting notes as provisional. Record conflicts and missing information instead of resolving them by assumption.

If the user supplies no exact Drive URL, search by the canonical client name and concise file-title keywords. Do not require every source category to exist.

For sales-transcript-led preparation, read [sales-call-to-interview.md](references/sales-call-to-interview.md). Extract what the client actually said, tailor the standard flow and produce the sentence exercise. Try the connected recording tools for supplied meeting links; if access fails, use a supplied summary/transcript and label the source. Read a supplied full transcript rather than relying only on its summary. Do not block useful preparation if only a summary is available; label its limits.

When the user also requests client setup, deduplicate and create/enrich canonical Obsidian context through the Project Hub context/onboarding route, using the vault conventions and client template. Keep this a bounded context setup, not the full onboarding execution. Save an evidence-based profile, goals and current stage; link it from the overview and client index. Separate reported facts, website claims, preferences, future ideas and gaps. Record owners only when evidenced. Profile creation requires the setup request or applicable workflow authority; ordinary meeting preparation alone does not authorise new canonical records. If the user defers the sales handover until after the interview, explicitly record that boundary: no handover, billing/access actions, BasicOps mutations or completed onboarding gates are implied. Work-folder creation likewise needs authority and verified parent/deduplication; never guess an existing mapping.

### 2. Build a coverage map

Map known evidence against:

1. founder and business story;
2. mission, vision, values and North Star;
3. brand personality, voice, preferred and avoided language;
4. ideal, secondary and unsuitable audiences;
5. customer emotions, fears, needs and objections;
6. services, priorities, capacity and delivery model;
7. differentiators, proof and feedback themes;
8. enquiry journey, sales philosophy and scripts;
9. pricing, funding and booking pathways;
10. marketing, website and content direction;
11. regulatory guardrails; and
12. contradictions, decisions and remaining gaps.

Classify each area as `known`, `provisional`, `partial`, `contradicted` or `missing`. Do not ask the client to repeat high-confidence facts unless their confirmation or interpretation matters.

### 3. Design themes

Create themes around coherent conversations, not template sections or a fixed question count. Usually use five to eight themes, but let the client and known gaps determine the number.

For each theme include:

- a plain-English purpose;
- one broad, natural invitation;
- two or three neutral example answers or territories;
- an uncapped optional prompt bank;
- what to listen for; and
- known facts that should not be re-asked.

Examples clarify the type and depth of answer sought. They must not prescribe an answer, put words in the client's mouth or introduce unsupported client facts.

For website/onboarding interviews, use this default sequence, tailored to the evidence:

1. story, purpose and future;
2. philosophy: common problems, beliefs and misconceptions;
3. people the client helps best;
4. how they help, what is distinctive and concrete stories;
5. becoming a patient/customer;
6. voice and website, including ten mixed sentence preferences; and
7. provisional positioning angle, success and read-back.

Separate understanding the problem/beliefs from explaining the actual approach. Ask why someone would choose this provider and how they explain alternatives or complementary modalities without assuming superiority. Derive the angle from answers, then test it with the client. Do not substitute generic sales explanations for clinical/business evidence. Map each theme to the website sections it will inform. See the reference for invitations, timing and the sentence-table format. Adapt, merge or split themes when the business or user's requested sequence warrants it.

### 4. Separate strategy from administration

Keep access collection, credentials, billing setup and routine asset requests out of the strategic conversation. Capture them as follow-up actions.

Website and operational decisions may remain when they require founder judgement: priorities, capacity, audience hierarchy, sitemap direction, conversion path, brand feeling, approval path and success definition.

### 5. Apply industry guardrails

Detect the applicable regulatory framework. For Australian healthcare:

- distinguish internal stories and feedback themes from public advertising;
- flag clinical testimonials, outcome guarantees, cure claims and misleading claims;
- preserve authentic internal language while identifying language that requires compliant external phrasing; and
- do not turn compliance review into the main meeting unless relevant claims arise.

### 6. Create the meeting pack

Use [meeting-pack-template.md](references/meeting-pack-template.md). Tailor every section to the client and current evidence. Save the pack and coach prompt under the verified work root in `playbook-strategy-session/YYYY-MM/`; keep only a concise preparation-status/source/link note in Obsidian. Do not put full deliverables into the knowledge vault.

Include purpose, known context, sales-call continuations with timestamps where available, contradictions or confirmations, opening frame, themed conversation flow, website-content coverage, ten-sentence table, time priorities, live-coach behaviour and sources. Keep delivery promises needing reconciliation with the accepted proposal in a separate internal list; a sales assertion is not verified functionality, approved scope or a ranking guarantee.

### 7. Create the meeting-coach prompt

Use [meeting-coach-prompt.md](references/meeting-coach-prompt.md). Replace placeholders and tailor commands, compliance notes and output requirements. Save it beside the meeting pack.

The coach must introduce one theme at a time; provide a broad invitation and neutral examples; stop while the user records; preserve exact language and stories; ask at most one follow-up at a time; move on when coverage is sufficient; support voice commands; and maintain a private coverage map.

Do not make the coach draft the final playbook during the live meeting unless requested.

### 8. Process the completed session

When given the transcript or captured answers:

1. preserve speaker attribution where possible;
2. extract exact quotes and characteristic phrases;
3. organise findings by theme and playbook coverage area;
4. record decisions, contradictions and unresolved gaps;
5. separate administrative actions from strategic follow-ups;
6. report `complete`, `partial` and `missing` coverage, including website sections;
7. preserve sentence ratings, reasons and exact replacement wording; and
8. produce a clean source brief for `campaign-playbook-generator`, with problem-to-approach examples and a provisional positioning synthesis for confirmation.

Never fabricate an answer to make coverage look complete.

## Quality checks

- The meeting feels conversational rather than interrogative.
- Main themes invite stories and reflection; the deliberate yes/no/unsure sentence exercise is the exception.
- Examples are neutral and clearly illustrative.
- Questions already answered with high confidence are removed.
- Founder voice, customer psychology, differentiators and sales philosophy receive enough depth.
- Operational access requests are deferred.
- Industry compliance is recognised without sanitising internal source material.
- The resulting transcript can populate the major playbook sections.
- Every source and provisional assumption is traceable.
- The ten sentence probes include real contrasts without revealing predicted answers; tone approval is separate from clinical/factual approval.
- Source-client details, private planning and credentials are absent from reusable skill examples.
- Context setup and deferred handover are reported separately; preparation never marks the interview completed.

## Handoff

Return links to the meeting pack and meeting-coach prompt. Explain the test sequence:

1. upload the pack and supporting context to ChatGPT/Hermes;
2. paste the coach prompt;
3. enter voice mode and say `Start the meeting`;
4. conduct the themes; and
5. say `End the session`, then pass the source brief to `campaign-playbook-generator`.
