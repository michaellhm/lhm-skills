---
name: client-context-intake
description: "Extract structured facts from client call notes, Fathom transcripts, meeting recordings, or uploaded documents. Use this when the user says 'process call notes', 'extract client info', 'intake from transcript', 'add client context', 'process Fathom notes', 'client discovery', or 'client onboarding'. Outputs facts only — no marketing copy. Phase 1 of the website build."
---

# Client Context Intake

Extract structured facts from raw client input (call transcripts, meeting notes, uploaded documents) and organize them into the canonical client profile files. **Facts only — no interpretation, no marketing copy.**

## Before Starting

1. Check if `/client/client_profile.md` already exists and has content
   - If yes: read it, note what's already captured, only fill gaps
   - If no: create it from the template in `${CLAUDE_PLUGIN_ROOT}/references/folder-structure.md`

2. Ask the user for source material using the `AskUserQuestion` tool:
   - "What source material do you have?" (options: "Call transcript / Fathom notes", "Meeting notes", "Uploaded documents", "I'll answer questions directly")

## Step 1: Process Source Material

If files are provided:
- Read every file completely — do not skim
- Extract facts into categories (see below)
- Note contradictions or ambiguities as questions for `/client/clarifications.md`
- **Do not infer** — if something isn't stated, don't guess

If answering questions directly:
- Use the `AskUserQuestion` tool to walk through each category
- Ask only for what's missing from existing files

## Step 2: Extract Into Categories

Organize extracted facts into these files:

### `/client/client_profile.md`

Update the YAML frontmatter and fill these sections:

- **Business Overview** — What the business does, how long they've operated, founding story
- **Target Audience** — Who they serve, demographics, psychographics, pain points
- **Services / Offerings** — What they sell or provide, pricing if mentioned
- **Locations / Service Areas** — Physical locations, service radius, markets served
- **Goals & Objectives** — What they want from the website, business goals
- **Competitors** — Named competitors, what they do differently
- **Unique Value Proposition** — What makes them different (in the client's words)
- **Tone & Voice** — How they describe themselves, language patterns from transcripts

### `/client/services.md`

One section per service/offering:

```markdown
## [Service Name]

**Description**: [What it is, in the client's words]
**Target Audience**: [Who this is for]
**Key Benefits**: [Why someone would choose this]
**Price Point**: [If mentioned]
**Differentiator**: [What makes this unique]
```

### `/client/locations.md`

One section per location or service area:

```markdown
## [Location Name]

**Address**: [If physical]
**Service Area**: [Radius or suburbs/regions served]
**Specific Details**: [Opening hours, local specialties, team]
```

### `/client/constraints.md`

Capture any mentioned constraints:
- Budget limits
- Timeline / deadlines
- Technical requirements or existing systems
- Compliance / regulatory requirements (e.g. AHPRA, NDIS, legal disclaimers)
- Existing assets to incorporate (logo, photos, copy)

### `/client/clarifications.md`

Log anything unclear or contradictory:

```markdown
| Date | Question | Answer | Source |
|------|----------|--------|--------|
| 2026-02-15 | Is the Bondi clinic open Saturdays? | [Pending] | Transcript p.3 — conflicting info |
```

## Step 3: Cross-Plugin Integration

If the marketing hub is available, the Campaign Playbook Generator can provide deeper brand/messaging extraction. Note this for the user but don't run it automatically:

> "If you'd like a full brand playbook (messaging frameworks, tone guidelines, competitive positioning), I can also run the Campaign Playbook Generator from the marketing hub. Want me to do that?"

Reference path: `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/skills/campaign-playbook-generator/SKILL.md`

## Step 4: Summary & Approval

After processing, present a summary:

1. List all files created or updated
2. Show key facts extracted per category (bullet points, not full files)
3. List any open questions logged in `clarifications.md`
4. State the item count: "Extracted X facts across Y files"

Use the `AskUserQuestion` tool to ask:

> "Client intake is complete. Review the files and let me know if anything needs correction. Ready to proceed to **Phase 2: SEO Architecture & Content Planning**?"

## Rules

- **Facts only** — no marketing copy, no creative writing, no embellishment
- **Client's words** — use their language, not marketing language
- **Never overwrite** — if a file has existing content, merge new facts in
- **Flag ambiguity** — if something is unclear, log it as a question rather than guessing
- **No placeholders** — only write sections you have real data for
