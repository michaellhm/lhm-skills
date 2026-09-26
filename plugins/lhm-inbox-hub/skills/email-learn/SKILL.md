---
name: email-learn
description: Close the learning loop on email drafts. Compares what triage drafted with what Michael actually sent, logs the differences, and proposes updates to the voice profile and routing rules. Use when the user says 'what did I change in my emails', 'email learnings', 'update the voice profile', 'learn from my sent mail', or as the last step of the morning routine after a day of sending. Proposes edits; writes them only on approval or when the session is unattended and the change is additive.
---

# Email learn

The system gets better only if this runs. Corrections are the signal; a draft sent unchanged is also a signal.

## Step 1: Match drafts to sent mail

Read `inbox-log/drafts.jsonl` (and `session.jsonl` if present) for the last 3 days. For each draft, fetch the thread and find the message Michael sent on it after the draft was created. Three outcomes:

- Sent as drafted (or trivially edited: punctuation, one word): log `unchanged`.
- Sent with edits: capture both texts, log `edited`.
- Not sent, draft still there or deleted: log `unsent`.

Also pull `in:sent newer_than:1d` and flag any sent email with no matching draft; those are emails Michael wrote cold, and they are voice evidence too.

## Step 2: Diff the edits

For each `edited` pair, describe the change in one line, in categories: opener, close, length (shorter/longer, by how much), register (warmer/more formal), removed phrase, added phrase, fact corrected, structure (bullets added/removed), ask reworded. Be literal. "Cut from 180 to 70 words, dropped the second paragraph of context" is useful. "Made it punchier" is not.

Append to `inbox-log/corrections.md`: date, recipient, audience, category, one-line diff, and the two texts collapsed under a details block.

## Step 3: Look for patterns

Read the whole corrections log. A pattern is three or more corrections in the same category for the same audience, or the same phrase removed twice. For each pattern, write a candidate rule in the voice-profile style ("Partner replies: cap at 60 words unless Michael is briefing a build").

Routing signals count too: a thread triage sent to Josephine that Michael answered himself, or a Tier 1 thread Michael forwarded to Kristalyn without replying, becomes a candidate routing override.

## Step 4: Propose

Output: the unchanged/edited/unsent counts, the new corrections in one line each, and the candidate rules with the evidence threads. Ask which to apply.

If Michael approves, or if this is an unattended run and the rule is purely additive (a new line under "Learned adjustments" in voice-profile.md, or "Learned overrides" in routing.md), append it with the date and evidence. Never rewrite an existing rule unattended; put a contradiction in the proposal instead.

When `lhm-learn:learn` is available, hand the approved rules to it so they land in LEARNED.md and the client profile as well. When the Obsidian routing file exists, append routing overrides there, not only in the bundled copy.

## Step 5: Weekly

On the first run each week, add a three-line summary to the corrections log: drafts made, percent sent unchanged, top correction category. This is what the weekly skill review reads.
