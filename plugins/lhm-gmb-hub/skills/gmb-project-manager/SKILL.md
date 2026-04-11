---
name: gmb-project-manager
description: "Read, create, or update the GMBProjectManagement.md file for a client. Use this when the user mentions 'GMB status', 'where are we at with GMB', 'update GMB project', 'update rankings', 'GMB progress', 'what's left to do', 'mark as done', or wants to check or modify the project tracking document. Also used internally by all agents after completing tasks."
---

# GMB Project Manager

Manages the per-client `GMBProjectManagement.md` file which tracks the full state of a client's GMB optimisation: current cycle, phase, task completion, focus keywords, and ranking history.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gmb-project-manager/LEARNED.md`
2. Identify the client (ask if not clear from context)
3. Locate the client folder

## Workflow

### 1. Check If Project Doc Exists

Look for `[client_folder]/gmb/GMBProjectManagement.md`.

**If it does NOT exist:** Create the `gmb/` directory and a new `GMBProjectManagement.md` using the template below. Populate the Overview section from `client_profile.md`. Set Current Phase to "Month 0 — Onboarding". Ask the user for the 7 focus keywords (or suggest them based on the client profile).

**If it DOES exist:** Read it and proceed to step 2.

### 2. Present Status Summary

Display a concise summary:

```
Client: [Name]
Current Phase: [Phase]
Cycle: [N] ([date range])

Completed: X/Y tasks in current phase
[List completed tasks with ✅]
[List outstanding tasks with ⬜]

Suggested next: [Next incomplete task]
```

### 3. Handle User Request

The user may want to:

**View status** — Display the summary above. No changes needed.

**Update rankings** — Use `AskUserQuestion` to ask:
- "Would you like to supply the latest rankings manually, or should I pull them from GSC/Local Falcon?"
- If manual: ask for each keyword's current position and Top3% metric
- If auto-pull: attempt to use GSC MCP and Local Falcon MCP. Fall back to manual if unavailable.
- Update the ranking history table in the project doc

**Mark tasks complete** — Mark specific tasks as `[x]` with today's date. Expand sub-tasks if needed (e.g. list each service page individually).

**Add notes** — Append to the Notes & Decisions section with today's date.

**Start new cycle** — Append a new `## 3-Month Cycle N` section with fresh Month 0-3 tasks. The re-cycle Month 0 is lighter (only diagnostic + service selection, not full GBP optimisation).

**Check exit criteria** — Review all tasks in the current phase. Report which are complete and which are outstanding. Only mark exit criteria as met if ALL tasks are done.

### 4. Save Changes

Write the updated `GMBProjectManagement.md` back to the client folder. Confirm to the user what was changed.

## GMBProjectManagement.md Template

When creating a new project doc, use this structure:

```markdown
# GMB Project Management — [Client Name]

## Overview
- **Client:** [Name]
- **Primary Location:** [Address]
- **Primary Modality:** [e.g. Physiotherapy]
- **Last Updated:** [Today's date]

## Focus Keywords & Ranking History

| Keyword | Cycle 1 M0 | Cycle 1 M1 | Cycle 1 M2 | Cycle 1 M3 |
|---------|-----------|-----------|-----------|-----------|
| [Keyword 1] | — | — | — | — |
| [Keyword 2] | — | — | — | — |
| [Keyword 3] | — | — | — | — |
| [Keyword 4] | — | — | — | — |
| [Keyword 5] | — | — | — | — |
| [Keyword 6] | — | — | — | — |
| [Keyword 7] | — | — | — | — |

---

## 3-Month Cycle 1 — [Start Month Year] to [End Month Year]

### Cycle Focus
- **Priority Services:** (to be determined during Month 0)
- **Selection Reasoning:** —
- **Approved by:** —
- **Diagnostic Direction:** —
- **Threshold:** —

### Month 0 — Onboarding ([Month Year])

#### Tasks
- [ ] Run baseline diagnostic
- [ ] Competitor audit (3 competitors)
- [ ] GBP categories optimised (up to 10)
- [ ] GBP services listed (30+)
- [ ] 750-char business description written
- [ ] All GBP profile fields completed
- [ ] 52 weekly GBP posts generated
- [ ] Citation audit completed
- [ ] Entity mapping completed
- [ ] Site architecture mapped
- [ ] **Exit criteria met**

### Month 1 — Service Pages ([Month Year])

#### Tasks
- [ ] Homepage consistency signal audit
- [ ] Service page: [Service 1]
- [ ] Service page: [Service 2]
- [ ] Service page: [Service 3]
- [ ] Technical audit: all service pages
- [ ] Pages submitted to GSC
- [ ] Month 1 report generated
- [ ] **Exit criteria met**

### Month 2 — Content Expansion ([Month Year])

#### Tasks
- [ ] Diagnostic re-run (compare to baseline)
- [ ] Content direction decided (FAQ vs overlay vs mixed)
- [ ] Supporting content for [Service 1] (X pages)
- [ ] Supporting content for [Service 2] (X pages)
- [ ] Supporting content for [Service 3] (X pages)
- [ ] Month 2 report generated
- [ ] **Exit criteria met**

### Month 3 — Link Building ([Month Year])

#### Tasks
- [ ] Link gap audit completed
- [ ] "Not AI slop" links: [Service 1] page
- [ ] "Not AI slop" links: [Service 2] page
- [ ] "Not AI slop" links: [Service 3] page
- [ ] Local authority opportunities identified
- [ ] Chamber of Commerce outreach (target: 2-5)
- [ ] Sponsorship outreach (target: 2-4)
- [ ] PR brief generated (if applicable)
- [ ] Month 3 / full cycle report generated
- [ ] **Exit criteria met**

---

## Notes & Decisions
```

## Output

- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Creates the file and `gmb/` directory if they don't exist
