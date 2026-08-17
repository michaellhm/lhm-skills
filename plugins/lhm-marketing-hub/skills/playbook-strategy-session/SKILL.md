---
name: playbook-strategy-session
description: Prepare and coach theme-led client strategy sessions that gather authentic source material for an LHM Master Campaign & Sales Playbook. Use when the user asks to prepare, plan, run, facilitate or create a prompt for a campaign-playbook meeting, founder interview, business-brain session, strategy call or voice-mode client conversation. Reads existing client context first, produces a tailored meeting pack and a ready-to-paste ChatGPT/Hermes meeting-coach prompt, and can process the completed transcript into a source brief for the campaign-playbook generator.
---

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

Prefer themes such as story and purpose; values and experience; people understood best; services, priorities and capacity; differentiation and trust; the client journey; and website, brand and success. Adapt, merge, split or rename them to fit the client.

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

Use [meeting-pack-template.md](references/meeting-pack-template.md). Tailor every section to the client and current evidence. Save it in the canonical client meeting folder when available.

Include purpose, known context, contradictions or confirmations, opening frame, themed conversation flow, time priorities, live-coach behaviour and sources.

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
6. report `complete`, `partial` and `missing` coverage; and
7. produce a clean source brief for `campaign-playbook-generator`.

Never fabricate an answer to make coverage look complete.

## Quality checks

- The meeting feels conversational rather than interrogative.
- Themes invite stories and reflection, not yes/no answers.
- Examples are neutral and clearly illustrative.
- Questions already answered with high confidence are removed.
- Founder voice, customer psychology, differentiators and sales philosophy receive enough depth.
- Operational access requests are deferred.
- Industry compliance is recognised without sanitising internal source material.
- The resulting transcript can populate the major playbook sections.
- Every source and provisional assumption is traceable.

## Handoff

Return links to the meeting pack and meeting-coach prompt. Explain the test sequence:

1. upload the pack and supporting context to ChatGPT/Hermes;
2. paste the coach prompt;
3. enter voice mode and say `Start the meeting`;
4. conduct the themes; and
5. say `End the session`, then pass the source brief to `campaign-playbook-generator`.
