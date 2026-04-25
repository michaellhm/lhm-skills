# LHM WordPress Hub - Plugin-Wide Rules

These rules apply to EVERY skill and agent in this plugin, without exception.

## Mandatory: Workflow Detection

Every session in this plugin operates on one of two workflows: **Full Website Build** or **Landing Page Campaign**. Before invoking any skill that produces output, you MUST know which workflow is active.

- If `wordpress/website-project-management.md` exists in the current project, you're in a Full Website Build.
- If `landing-pages/[campaign]/landing-page-project-management.md` exists, you're in a Landing Page Campaign.
- If both exist, ask the user which to work on via `AskUserQuestion`.
- If neither exists, route through `wp-start` to set one up.

Do not mix workflows in a single session.

## Mandatory: Project Doc Updates

Every skill that completes a task that maps to a checkbox in the active project management doc MUST:

1. **Ask before ticking.** Use `AskUserQuestion`: "Happy for me to mark off Step [X.Y] — [task name] in the project management doc?"
2. **If approved, invoke the relevant project manager skill** (`wp-project-manager` for full builds, `lp-project-manager` for landing pages) in "mark complete" mode with the task ID and today's date.
3. **If the task surfaced a decision** (tool choice, scope deviation, client feedback), append a dated line to the project doc's Notes & Decisions section.
4. **Never tick tasks Claude did not perform.** Tasks owned by Krystalyn, Aiya, Jaimee, or Michael (people-only checkboxes) are surfaced by the session-end sweep, not auto-prompted.

The active project manager skill is also responsible for the session-end sweep: scan what was done in the conversation, surface any completions that weren't ticked, ask the user in a single batched prompt round.

## Mandatory: Anti-AI Writing Guidelines

Before writing ANY content (page copy, briefs, design rationale, reports, recommendations, or file outputs), you MUST follow the anti-AI writing guidelines stored at:

`${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/references/anti-ai-writing-guidelines.json`

Read this file at the start of every content-producing skill execution. These rules apply to ALL written output.

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

## Mandatory: Self-Learning Protocol

Every skill in this plugin has a `LEARNED.md` file in its directory. This file is Claude's persistent memory for that specific skill, written by Claude through use.

### Before Executing Any Skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task. If the file is empty or only contains the header, proceed normally.

### When to Write a New Entry

After completing a skill execution, check whether you discovered something that would save time or prevent mistakes in future runs. Only record entries that are **reusable across sessions**, not one-off context.

Record things like:
- **Tool/API failures** — specific services that block access, rate limits, broken endpoints
- **Data quirks** — unexpected formats, missing fields, inconsistent naming conventions
- **Workflow blockers** — steps that consistently fail or need workarounds
- **Format corrections** — output formats the user corrected or preferred over the default
- **Skill interaction issues** — when skills need to be run in a specific order, or when one skill's output doesn't match another's expected input
- **WordPress-specific issues** — theme conflicts, block editor quirks, plugin incompatibilities, REST API gotchas

### Entry Format

One line per entry. Dated. Specific. Actionable.

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

**Good**: `- (2026-02-23) theme.json spacing presets must use clamp() for fluid values. Fixed pixel values break responsive layouts.`
**Good**: `- (2026-02-23) WP REST API returns 401 for custom post types unless 'show_in_rest' is true in registration.`
**Bad**: `- Be careful with WordPress.`
**Bad**: `- Remember to test themes.`

### Maintenance Rules

- **Cap**: Maximum 50 entries per LEARNED.md file
- **Before adding**: Count existing entries. If at or over 50, consolidate first
- **Consolidation**: Merge duplicate/similar entries, drop entries older than 3 months that were never referenced again, remove one-off observations that didn't recur
- **Never delete**: Entries that document persistent limitations or that you've referenced in recent sessions

### Do NOT Record

- Session-specific context (current client name, task details, file paths for this run)
- Information already documented in SKILL.md, client_profile.md, or reference files
- Speculative conclusions from a single observation (wait until a pattern recurs)
- Anything the user explicitly told you not to remember

## Mandatory: 8-Pass Writing Engine

All long-form content (over 300 words or page-level web/blog copy) MUST route through the plugin's `content-writer` agent, which implements the 8-pass writing pipeline defined at `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/references/8-pass-writing-engine.md`.

Skills handle research and context gathering; the content-writer agent handles the writing. Never generate long-form content in a single pass.

Short-output content (ad headlines, meta tags, social posts, banner copy) is exempt — those skills have their own tight constraints.

## Output Structure

All client-level artefacts (cross-project reusable) live at the **client root**:

```
[client_folder]/
  client_profile.md
  playbook.md
  website-brief.md
  clarifications.md
  design/
    brand_guidelines.md
    brand_style_guide.pdf
    design_system.md
```

Workflow-specific artefacts live under their workflow folder:

```
[client_folder]/wordpress/        # full website build
[client_folder]/landing-pages/[campaign]/   # LP campaigns
```

Skills must:
- Read shared artefacts from the client root, never duplicate them into the workflow folder.
- Write workflow-specific artefacts only inside the relevant workflow folder.
- Create directories as needed before writing.
