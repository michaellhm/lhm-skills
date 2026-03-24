---
name: learn
description: "Capture session learnings and update the correct files. Use this when the user says 'learn', 'save what we learned', 'update learnings', 'capture this', 'remember this', 'save this to the profile', 'update the client profile', or invokes /learn. Accepts an optional inline argument (e.g. /learn the GA property is UA-12345). Scans conversation context for skill learnings (LEARNED.md) and client learnings (client_profile.md), presents findings for approval, then writes to the correct files."
---

# Learn — Session Learning Capture

Capture what was learned during a work session and write it to the correct places: skill LEARNED.md files for reusable patterns, and client_profile.md for client-specific facts.

## Workflow

### Step 1: Gather Context

**If the user provided an inline argument** (e.g. `/learn the GA property is UA-12345`), note it as a priority learning to process.

**Regardless of whether an argument was provided**, scan the full conversation context and identify two categories of learnings:

#### A. Skill Learnings (destined for LEARNED.md)
Patterns, gotchas, and workflow improvements that are reusable across sessions and clients. Look for:
- Tool/API failures, workarounds, or unexpected behaviours
- Data quirks or format issues encountered
- Workflow steps that needed adjustment
- Output format preferences the user corrected
- Skill interaction issues (ordering, input/output mismatches)
- Techniques or approaches that worked well (or didn't)

**These must be session-independent** — useful for any future run of that skill, not just this client.

#### B. Client Learnings (destined for client_profile.md)
Specific facts about this client's business, accounts, or configuration. Look for:
- Google Analytics property IDs, GA4 measurement IDs
- Google Ads account IDs, campaign IDs
- Conversion types and conversion values
- Business details (services, locations, staff, specialisations)
- Regulatory or compliance requirements discovered
- Target audience insights confirmed during the session
- Budget information, spend data
- Competitor names or URLs discovered
- Brand preferences, tone of voice corrections
- Technical details (CMS, hosting, domain, DNS)
- Social media accounts or URLs
- Any other factual information about the client

### Step 2: Present Findings

Present your findings to the user in two clear sections:

```
## Skill Learnings (for LEARNED.md)

1. [learning] → likely applies to: [plugin]/[skill-name]
2. [learning] → likely applies to: [plugin]/[skill-name]

## Client Learnings (for client_profile.md)

1. [fact or update]
2. [fact or update]
```

For each skill learning, auto-detect which plugin and skill it most likely applies to by considering:
- Which skills were used or discussed in the conversation
- Which plugin's domain the learning falls under
- If uncertain, flag it for the user to decide

### Step 3: User Confirmation

Use `AskUserQuestion` to ask the user:

**"Which of these learnings should I save?"**

Options:
- **All of them** — Save everything as presented
- **Let me pick** — User selects which ones to keep (present numbered list)
- **None — skip skill learnings** — Only process client learnings
- **None — skip client learnings** — Only process skill learnings

### Step 4: Ask for Additions

After the user confirms, ask:

**"Is there anything else you'd like to add to the client profile?"**

Options:
- **No, that's everything**
- **Yes, let me add something** — User provides additional facts to include

### Step 5: Write Skill Learnings

For each confirmed skill learning:

1. **Confirm the target skill** — If you auto-detected the skill, confirm with the user: "I'll write this to `plugins/[plugin]/skills/[skill]/LEARNED.md` — correct?"
2. **Find the LEARNED.md file** — Search for the file at the expected path. All LHM plugins live under `plugins/` in the skills repo. The path pattern is:
   ```
   plugins/{plugin-name}/skills/{skill-name}/LEARNED.md
   ```
   **Critical:** Always write to the source repo (e.g. `/Users/.../lhm-skills-v3/plugins/`), NOT to the cached/installed version at `~/.claude/plugins/marketplaces/` or `~/.claude/plugins/cache/`. The cache is overwritten on plugin updates and learnings will be lost.
   If the skills repo isn't the current working directory, search for LEARNED.md files using Glob: `**/plugins/*/skills/*/LEARNED.md`
3. **Read the existing LEARNED.md** to check current entries and count
4. **If at or over 50 entries**, consolidate first (merge duplicates, drop stale entries)
5. **Append the new entry** in the correct format:
   ```
   - (YYYY-MM-DD) Specific observation or rule. Not vague advice.
   ```
6. **Use the Edit tool** to add the entry after the last existing entry (or after the HTML comment if empty)

### Step 6: Write Client Learnings

For each confirmed client learning:

1. **Find client_profile.md** — Search in the current working directory first. If not found, use Glob to search: `**/client_profile.md`
2. **Read the existing client_profile.md** to understand its current structure and content
3. **Determine where each learning fits**:
   - If an existing section covers this topic, update or enrich that section
   - If no section exists, add an appropriate new section
   - Common sections to look for or create:
     - `## Google Analytics` — GA4 property, measurement ID, key events
     - `## Advertising` — Google Ads ID, budget, platforms
     - `## Conversions` — conversion types, values, tracking details
     - `## Technical` — CMS, hosting, domain info
     - `## Social Media` — platform accounts and URLs
     - `## Notes` — catch-all for other facts
4. **Never overwrite existing correct data** — only add new information or correct known errors
5. **Use the Edit tool** to make targeted updates to the relevant sections
6. **If client_profile.md doesn't exist**, inform the user and suggest running the client-onboarding skill first. Do not create client_profile.md from scratch in this skill.

### Step 7: Confirm Completion

Summarise what was written and where:

```
Done. Here's what I saved:

**Skill learnings:**
- [learning summary] → plugins/[plugin]/skills/[skill]/LEARNED.md

**Client profile updates:**
- Added [section/field] to client_profile.md
```

## Rules

- **One learning per LEARNED.md entry** — don't combine multiple observations into one line
- **Date every entry** using today's date in `(YYYY-MM-DD)` format
- **Be specific and actionable** — "GSC API returns 403 for unverified properties" not "be careful with APIs"
- **Don't duplicate** — check existing entries before adding
- **Skill learnings must be client-independent** — if it only applies to this specific client, it's a client learning
- **Client learnings must be factual** — don't record opinions or speculative conclusions
- **Always read before writing** — never modify a file you haven't read first
- **Confirm the target skill with the user** before writing to any LEARNED.md
