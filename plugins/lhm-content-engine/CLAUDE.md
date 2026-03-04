# LHM Content Engine - Plugin-Wide Rules

These rules apply to EVERY skill and agent in this plugin, without exception.

## Mandatory: Anti-AI Writing Guidelines

Before writing ANY content (blog articles, social posts, outlines, meta descriptions, reports, recommendations, or file outputs), you MUST follow the anti-AI writing guidelines stored at:

`${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`

Read this file at the start of every skill execution. These rules apply to ALL written output.

### Quick Reference (always enforce these):

1. **Break the Rule of 3** - Don't organize ideas in triplets. Vary structural patterns.
2. **Avoid contrast framing** - Reduce "while X, Y" and "although X, Y" constructions.
3. **Eliminate poetic shift phrases** - No "in a world where," "in an era of," "in a landscape defined by."
4. **Use varied paragraph structures** - Don't default to odd-numbered structures (5, 7, 9 paragraphs).
5. **Limit hypophora** - Don't pose questions and immediately answer them.
6. **Moderate adverb usage** - Avoid "-ly" adverbs (significantly, dramatically, effectively). Use stronger verbs.
7. **Avoid marketing cliche pairings** - No "seamless integration," "robust solution," "game-changing innovation."
8. **Use natural transitions** - No "Let's explore," "Let's dive into," "Now, let's turn to."
9. **End paragraphs naturally** - No vague emotional insights or forced inspirational statements.
10. **No em dashes** - Never use em dashes. Use commas, periods, or parentheses instead.

### Overall principle

Write with an authentic voice. Use specific examples, concrete details, and natural phrasing. Occasional imperfection is better than polished-but-robotic output.

## Mandatory: Allied Health Compliance

All content produced by this plugin is for allied health clinics (physiotherapy, chiropractic, podiatry, osteopathy, exercise physiology, etc.). Strict compliance rules:

- **No exaggerated recovery claims** - never promise outcomes, timelines, or cure rates
- **No diagnostic language** - use "may help," "commonly associated with," not definitive medical statements
- **No testimonial-style claims** - avoid "patients love" or "100% success rate"
- **Evidence-based framing** - reference research or clinical guidelines where appropriate
- **AHPRA-aware** - content must not breach AHPRA advertising guidelines for registered practitioners

## Mandatory: Structured JSON Handoff

All skills in this plugin communicate via structured JSON objects. No free-text chaining between skills. Every skill declares its INPUT and OUTPUT schema. The orchestrator passes JSON outputs from one skill as JSON inputs to the next.

## Mandatory: Self-Learning Protocol

Every skill in this plugin has a `LEARNED.md` file in its directory. This file is Claude's persistent memory for that specific skill, written by Claude through use.

### Before Executing Any Skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task. If the file is empty or only contains the header, proceed normally.

### When to Write a New Entry

After completing a skill execution, check whether you discovered something that would save time or prevent mistakes in future runs. Only record entries that are **reusable across sessions**, not one-off context.

Record things like:
- **Tool/API failures** - specific services that block access, rate limits, broken endpoints
- **Data quirks** - unexpected CSV formats, missing fields, inconsistent client folder structures
- **Workflow blockers** - steps that consistently fail or need workarounds
- **Format corrections** - output formats the user corrected or preferred over the default
- **Skill interaction issues** - when skills need to be run in a specific order, or when one skill's output doesn't match another's expected input
- **Compliance patterns** - recurring AHPRA or compliance issues that apply across clients

### Entry Format

One line per entry. Dated. Specific. Actionable.

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

### Maintenance Rules

- **Cap**: Maximum 50 entries per LEARNED.md file
- **Before adding**: Count existing entries. If at or over 50, consolidate first
- **Consolidation**: Merge duplicate/similar entries, drop entries older than 3 months that were never referenced again, remove one-off observations that didn't recur
- **Never delete**: Entries that document persistent limitations or that you've referenced in recent sessions

### Do NOT Record

- Session-specific context (current client name, task details, file paths for this run)
- Information already documented in SKILL.md, client context files, or reference files
- Speculative conclusions from a single observation (wait until a pattern recurs)
- Anything the user explicitly told you not to remember

## Client Folder Structure

All client content lives under: `/clients/{client-name}/articles/`

Required files per client:
- `client-background.md` - business overview, services, locations, team
- `brand-voice.md` - tone, style, vocabulary preferences
- `compliance.md` - client-specific compliance rules beyond AHPRA defaults
- `anti-ai-writing.json` - client-specific anti-AI overrides (or use plugin default)
- `published-articles.json` - array of previously published article slugs and topics
- `services.json` - structured list of services offered
- `briefs/{brief-file}.md` - individual article briefs

## Non-Negotiable Rules

1. No blind browsing - deterministic file reads only
2. No hallucinated internal links - only use links confirmed in client context
3. No exaggerated recovery or medical claims
4. No repetitive AI phrasing - enforce anti-AI guidelines on every output
5. Structured JSON outputs between skills only - no free-text chaining
6. Isolate each article execution - no cross-contamination between rows in batch processing
7. Do not fabricate metrics, client data, or file contents
