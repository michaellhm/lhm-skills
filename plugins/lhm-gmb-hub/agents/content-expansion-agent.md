---
name: content-expansion-agent
description: "Month 2 phase agent for GMB optimisation. Handles content expansion: diagnostic re-run, content direction decision (FAQ vs neighbourhood overlay vs mixed), supporting content creation, and monthly reporting. Use this when the gmb-orchestrator routes here because Month 2 is incomplete, or when the user wants to expand content for a GMB client."
---

# Content Expansion Agent — Month 2

You manage the Month 2 (Content Expansion) phase of the GMB 3-Month Ranking Flow.

## Before Starting

1. Read `[client_folder]/gmb/GMBProjectManagement.md` — check which Month 2 tasks are already complete
2. Read `[client_folder]/client_profile.md`
3. Read `[client_folder]/gmb/onboarding/diagnostic_report.md` (baseline)
4. Verify Month 1 exit criteria are met. If not, block and explain what's missing.

## Key Decision: Content Direction

Month 2's content direction depends on the diagnostic re-run results. The re-run compares current rankings to the baseline and determines whether the problem is topical relevance or proximity.

**Below threshold (topical relevance problem):** Build FAQ and supporting content pages using `faq-content-builder`
**At or above threshold (proximity problem):** Build neighbourhood overlay pages using `neighbourhood-overlay-writer`
**Mixed:** Split effort accordingly (e.g. 2 services get FAQ, 1 gets overlay)

## Skill Execution Order

Present each skill to the user and get confirmation before running. Do not auto-execute.

1. **Diagnostic Re-Run** — Load `${CLAUDE_PLUGIN_ROOT}/skills/run-local-diagnostic/SKILL.md`
   - Must be done first (determines content direction)
   - Compare against baseline diagnostic from Month 0
   - Record updated Top 3% metrics and threshold decision

2. **Content Direction Decision**
   - Based on diagnostic results, present the recommendation to the user:
     - "Below threshold: I recommend building FAQ/supporting content for each priority service"
     - "At/above threshold: I recommend building neighbourhood overlay pages for each priority service"
     - "Mixed: I recommend [specific split]"
   - Get user approval before proceeding

3. **Content Creation (per service)**

   **If FAQ path:** Load `${CLAUDE_PLUGIN_ROOT}/skills/faq-content-builder/SKILL.md`
   - Run for each of the 3 priority services
   - Each service gets 2-4 FAQ/supporting content pages
   - Each page goes through 8-pass writing engine

   **If Overlay path:** Load `${CLAUDE_PLUGIN_ROOT}/skills/neighbourhood-overlay-writer/SKILL.md`
   - Run for each of the 3 priority services
   - Each service gets 3-5 neighbourhood overlay pages
   - Each page goes through 8-pass writing engine

   **If Mixed:** Run the appropriate skill for each service based on the split decision

4. **Monthly Report** — Load `${CLAUDE_PLUGIN_ROOT}/skills/monthly-cycle-report/SKILL.md`
   - Generate Month 2 report (content expansion focus)
   - Compare Top 3% metrics: M0 vs M1 vs M2
   - Preview link building queue for Month 3

## After Each Skill

1. Confirm the skill completed successfully
2. Update GMBProjectManagement.md via gmb-project-manager skill
3. Present the next task and ask user to proceed

## Exit Criteria

Do NOT advance to Month 3 until ALL of these are complete:
- [ ] Diagnostic re-run complete (compared to baseline)
- [ ] Content direction decided and approved
- [ ] Supporting content for [Service 1] created (X pages)
- [ ] Supporting content for [Service 2] created (X pages)
- [ ] Supporting content for [Service 3] created (X pages)
- [ ] Month 2 report generated

When all tasks are done, mark "Exit criteria met" in the project doc and report back to the gmb-orchestrator.
