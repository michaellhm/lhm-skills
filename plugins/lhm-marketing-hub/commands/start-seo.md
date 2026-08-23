---
description: Start or resume a staged SEO department run with the reusable LHM SEO Lead.
argument-hint: [client, goal, bounded task, or production envelope]
---
Begin or resume an SEO department run through the installed `start-seo` skill, with the **seo** agent acting as the Lead role.

Read `${CLAUDE_PLUGIN_ROOT}/skills/start-seo/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/references/seo-departmental-delivery.md`, `${CLAUDE_PLUGIN_ROOT}/agents/seo.md` and `${CLAUDE_PLUGIN_ROOT}/references/agent-orchestration-contract.md` in full. Follow the `start-seo` entry contract and Lead loop for the rest of this session. Preserve supplied parent and department goals, select only the first dependency-ready action, dispatch one bounded specialist stage, and require acceptance plus durable checkpoint readback before advancing. Never turn the request into one combined research/brief/write/QA prompt.

Optional context from me: $ARGUMENTS
