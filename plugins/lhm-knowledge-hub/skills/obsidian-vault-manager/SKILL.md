---
name: obsidian-vault-manager
description: Create, edit, organise, search, link, archive, or otherwise maintain Markdown notes in an Obsidian vault. Use for any request involving Obsidian notes, the Local Health Marketing knowledge base, vault structure, note templates, properties, internal links, goals, ideas, clients, projects, meetings, knowledge, or SOPs.
---

# Obsidian Vault Manager

Maintain an Obsidian vault as a coherent knowledge base and business operating system. Work directly with Markdown files; an MCP is not required when the vault is locally accessible.

## Use the official Obsidian CLI when available

1. Detect `obsidian` with `command -v obsidian`. On macOS, also check `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli`.
2. The official CLI requires Obsidian 1.12.7+ and a running Obsidian app. If it is unavailable, unregistered or the app is closed, fall back to direct Markdown and `rg` without blocking ordinary vault work.
3. Target the LHM vault explicitly as the first parameter: `obsidian vault="Local Health Marketing" <command>`.
4. Prefer the CLI for graph-aware and app-aware reads:
   - `search:context query="..."`
   - `backlinks path="..." format=json`
   - `links path="..."`
   - `unresolved`, `orphans`, and `deadends`
   - `tasks todo verbose`
   - `properties`, `property:read`, and `outline`
5. Use `obsidian help <command>` as the current command reference.
6. Continue to use careful file patches for multi-section edits where exact diffs and preservation matter. Use CLI `create`, `append`, `move`, `rename`, task and property commands when their atomic behaviour is safer or link-aware.
7. Never use CLI `delete permanent`, history restore, plugin installation, Sync mutation, or arbitrary `eval` unless explicitly requested and appropriately confirmed.

## Preserve authorship

- Do not present agent-generated prose as Michael's private reflection or stated belief.
- Preserve Michael's first-person language when he supplied it.
- Label inferred synthesis as agent analysis when authorship could otherwise be ambiguous.
- Agent-maintained operational notes, indexes and extracted decisions must remain grounded in linked sources.

## Locate the vault

1. Identify the vault root by finding the nearest directory containing `.obsidian`.
2. For Local Health Marketing, prefer `/Users/michaelcolman/Documents/Obsidian/Local Health Marketing/Local Health Marketing` when accessible.
3. Treat the directory containing `.obsidian`, not its parent, as the vault root.
4. Read `_System/Vault Conventions.md` completely before making structural or content changes. Follow it as the source of truth.

## Inspect before changing

1. Search filenames and note content for existing related material.
2. Read each target note completely before editing it.
3. Check relevant index notes and templates.
4. Determine whether the request belongs in an existing note, a new note, the inbox, or an archive.
5. Preserve unrelated user content and existing Obsidian configuration.

## Create notes

1. Use the relevant note in `80 Templates` as the starting schema when one exists.
2. Choose the folder based on the note's purpose, not merely words in its title.
3. Use a specific, human-readable filename. Name meetings `YYYY-MM-DD — Subject`.
4. Add `type`, `created`, and `updated` properties using `YYYY-MM-DD` dates.
5. Use a controlled status appropriate to the note type.
6. Link the note to at least one relevant goal, client, project, index, or related knowledge note.
7. Add the new note to a relevant index when an automatic query will not make it discoverable.

## Update notes

1. Merge new information into the most relevant existing sections.
2. Preserve useful wording, properties, links, headings, and authorial intent.
3. Avoid duplicating facts across notes; keep one canonical source and link to it.
4. Update the `updated` property after a material content change.
5. Record decisions and resulting actions explicitly when processing meeting or project information.
6. Maintain links when renaming or moving a note. Search for incoming Markdown or wiki links and repair them where necessary.

## Organise information

- Put unprocessed capture in `01 Inbox`.
- Put measurable company outcomes in `10 Goals`.
- Give each client a folder and same-named overview note in `20 Clients`.
- Put time-bound work with a defined outcome in `30 Projects`.
- Put opportunities under evaluation in `40 Ideas`.
- Put dated discussion records in `50 Meetings`.
- Put durable reference material in `60 Knowledge`.
- Put repeatable procedures in `70 SOPs`.
- Keep canonical templates in `80 Templates`.
- Move inactive material to `90 Archive` while preserving links.
- Keep governance material in `_System`.

## Handle ambiguity safely

- Prefer the smallest reversible change that fulfils the request.
- Put uncertain captures in the inbox and flag what remains unclear.
- Do not delete notes or overwrite substantial content unless explicitly requested.
- Do not introduce new folders, properties, tags, or status vocabularies casually. Update `_System/Vault Conventions.md` when a structural convention is intentionally changed.
- Ask only when a missing decision would materially alter the vault or risk losing information.

## Verify

1. Confirm edited files remain valid Markdown with valid YAML frontmatter.
2. Check that new links point to the intended note names.
3. Search for accidental duplicate notes or broken references introduced by the change.
4. When the CLI is available, run `unresolved` and inspect backlinks for renamed or moved notes.
5. Summarise what was created, updated, moved, or archived using clickable absolute file links.
