# lhm-inbox-hub

Michael's inbox system as a plugin. Five skills, five shared reference files, and a ChatGPT mirror.

## What it does

Entry point: `/lhm-inbox-hub:start-email` (optionally with a time budget, "triage", "tidy", or "reply to <thread>"). The `inbox` agent shows a four-line state summary and routes to a skill.

| Skill | Trigger | Job |
|---|---|---|
| inbox-triage | "triage my inbox", morning schedule | Classify, label, create BasicOps tasks, draft replies, walk this week's Obsidian tasks, write the brief |
| email-drafts | "draft a reply to", "email X about" | One Michael-voice draft, saved in Gmail |
| email-session | "I've got 30 minutes for email" | Work the brief's Reply-today list one item at a time |
| inbox-tidy | "tidy my inbox", monthly | Inventory stale labelled threads, apply approved Done/archive |
| email-learn | "email learnings", after sending | Diff drafts against sent mail, log corrections, propose rule updates |

Nothing in this plugin sends email, trashes, or deletes. See `references/safety-rules.md`.

## The files that learn

- `references/voice-profile.md`: how Michael writes, built from 42 of his own emails. "Learned adjustments" at the bottom grows via email-learn.
- `references/routing.md`: tiers, active clients, warm list, Josephine's boundary. Canonical copy should live in Obsidian at `LHM/Operations/email-routing.md`; this is the seed and fallback. "Learned overrides" at the bottom grows via email-learn.
- `references/brief-format.md`: the contract between triage and whatever reads the brief.
- `references/labels.md`: what each Gmail label means and which the skills may set.

## Runtime logs

`inbox-log/` next to the plugin (or `Inbox Briefs/log/` in the vault): `drafts.jsonl`, `session.jsonl`, `corrections.md`. email-learn reads these; the weekly skill review reads corrections.md.

## Phase 1 (now): run in ChatGPT

This plugin format cannot be installed into ChatGPT. `chatgpt/` holds the mirror: project instructions and two scheduled-task prompts. Upload the five reference files to the ChatGPT project. The plugin repo stays canonical; when a rule changes, edit it here and re-upload.

## Phase 2 (later): Hermes runs triage

Once the routing and voice files stop changing week to week, schedule inbox-triage and email-learn on Hermes. The brief lands in Obsidian; ChatGPT or the email-session skill reads it. Jev (TypeSafe) can replace the classification step in inbox-triage Step 2 once the tier schema is stable; it returns typed decisions with confidence, which is exactly what Step 2 produces.

## Connectors needed

Gmail (search, read, label, drafts). BasicOps (search, create task, comment). Obsidian vault access via a connected folder for the weekly flow note, client profiles, and the brief output. Optional: `lhm-project-hub:basicops-task-manager` as the BasicOps write boundary and `lhm-learn:learn` for pushing approved rules into LEARNED.md.
