# LHM Client Updates Hub - Plugin-Wide Rules

These rules apply to EVERY skill in this plugin, without exception.

## Mandatory: BasicOps field rules

**Never put task detail in the BasicOps `description` field.** All context, briefing detail, links, and "what done looks like" go into the task discussion via `create_message_in_task`. The description stays empty or holds a single line at most. Every write, every client, no exceptions.

Two formatting gotchas that bite every time:

- **Discussion messages take raw HTML.** Do not escape it to entities, because `&lt;p&gt;` renders as literal text in the discussion. Recovery is `delete_message` with the returned id, then repost unescaped.
- **Task titles take a plain `&`,** not `&amp;`, which renders as the literal entity.

Follow-up work belongs as subtasks under the client card (`parentTaskId`), not as standalone tasks in a section. If you mis-parent one, `update_task` with `parentTaskId` re-parents it and preserves the assignee, description, and discussion, so there is no need to delete and recreate.

## Mandatory: Anti-AI Writing Guidelines

Before writing ANY content (emails, task discussion messages, meeting notes, or conversational responses that include written content), you MUST follow the anti-AI writing guidelines stored at:

`${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`

Read this file at the start of every skill execution. These rules apply to:

- The team meeting-wrap email (`post-meeting-review`)
- Client-facing update emails (`client-update-email`)
- BasicOps task discussion messages, including task briefings and the meeting-notes context (`post-meeting-review`). Descriptions hold one line at most and carry no prose, per the field rules above.

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

### Before executing any skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task. If the file is empty or only contains the header, proceed normally.

For `post-meeting-review` this matters more than most, because the entries there cover BasicOps formatting gotchas that will otherwise be repeated on every run.

### When to write a new entry

After completing a skill execution, check whether you discovered something that would save time or prevent mistakes in future runs. Only record entries that are **reusable across sessions**, not one-off client context. Client facts belong in `client_profile.md`.

Record things like:
- **Tool and API failures:** services that block access, auth quirks, broken endpoints, undocumented required fields
- **Data quirks:** unexpected formats, missing fields, inconsistent naming
- **Workflow blockers:** steps that consistently fail or need a workaround
- **Format corrections:** output the user corrected or preferred over the default
- **Anything the user had to tell you twice**

### Entry format

Append to the end of the file, one observation per line, newest last:

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

Cap the file at 50 entries. When it reaches the cap, consolidate duplicates and drop stale entries before appending.

Prefer running `/lhm-learn:learn` over writing entries by hand, so the learning gets sorted into the right file and confirmed with the user first.
