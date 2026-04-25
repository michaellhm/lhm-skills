# LHM GMB Hub - Plugin-Wide Rules

These rules apply to EVERY skill and agent in this plugin, without exception.

## Mandatory: Anti-AI Writing Guidelines

Before writing ANY content (copy, suggestions, reports, emails, audits, strategies, recommendations, file outputs, or conversational responses that include written content), you MUST follow the anti-AI writing guidelines stored at:

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

## Mandatory: AHPRA Compliance (Healthcare Clients)

All content for healthcare clients MUST comply with AHPRA advertising guidelines. Before publishing any content, check against:

`${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`

Key rules (always enforce):
- No testimonials that could be interpreted as clinical outcomes
- No before/after claims
- No "best" or superlative claims about treatment
- No guarantees of results
- No misleading or deceptive claims about services

## Mandatory: 8-Pass Writing Engine

All content-producing skills MUST route content generation through the content-writer agent which implements the 8-pass writing pipeline. Skills handle research and context gathering; the content-writer agent handles the actual writing.

Reference: `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/references/8-pass-writing-engine.md`

Never generate long-form content in a single pass. The 8-pass system exists to produce content that passes AI detection, reads naturally, and converts.

## Mandatory: Project Doc Updates

Every skill that completes a task MUST update `GMBProjectManagement.md` in the client's gmb/ folder:
- Mark the relevant task as `[x]` with a completion date
- Record any key outputs or metrics
- Add notes for any decisions made

## Mandatory: Self-Learning Protocol

Every skill in this plugin has a `LEARNED.md` file in its directory. This file is Claude's persistent memory for that specific skill, written by Claude through use.

### Before Executing Any Skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task. If the file is empty or only contains the header, proceed normally.

### When to Write a New Entry

After completing a skill execution, check whether you discovered something that would save time or prevent mistakes in future runs. Only record entries that are **reusable across sessions**, not one-off context.

Record things like:
- **Tool/API failures** - specific services that block access, rate limits, broken endpoints
- **Data quirks** - unexpected formats, missing fields, inconsistent naming conventions
- **Workflow blockers** - steps that consistently fail or need workarounds
- **Format corrections** - output formats the user corrected or preferred over the default
- **Skill interaction issues** - when skills need to be run in a specific order

### Entry Format

One line per entry. Dated. Specific. Actionable.

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

### Maintenance Rules

- **Cap**: Maximum 50 entries per LEARNED.md file
- **Before adding**: Count existing entries. If at or over 50, consolidate first
- **Consolidation**: Merge duplicate/similar entries, drop entries older than 3 months that were never referenced again
- **Never delete**: Entries that document persistent limitations or that you've referenced in recent sessions

### Do NOT Record

- Session-specific context (current client name, task details, file paths for this run)
- Information already documented in SKILL.md, client_profile.md, or reference files
- Speculative conclusions from a single observation (wait until a pattern recurs)
- Anything the user explicitly told you not to remember

## Mandatory: MCP Graceful Fallbacks

This plugin uses several MCP servers that may not be installed. When a skill requires an MCP that is not available:

1. Do NOT fail silently or skip the step
2. Display the setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`
3. Offer a manual alternative (e.g. "paste your Local Falcon results and I'll record them")
4. Continue with the skill using whatever data is available

## Output Structure

All skill outputs go to the client folder under `gmb/`:

```
client_folder/gmb/
├── GMBProjectManagement.md
├── onboarding/           # Month 0 outputs
└── monthly-optimization/
    └── YYYY-MM/          # Per-month outputs
```

Skills must create these directories if they don't exist before writing output files.
