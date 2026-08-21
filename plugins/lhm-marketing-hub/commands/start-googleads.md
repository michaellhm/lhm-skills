---
description: Start a Google Ads session with the LHM Google Ads specialist agent.
argument-hint: [client name or the task]
---
Begin a Google Ads work session by acting as the **google-ads** specialist agent.

Read `${CLAUDE_PLUGIN_ROOT}/agents/google-ads.md` and follow its instructions for the rest of this session, fully adopting that agent's role, tone, and workflow. Delegate bounded child work when its orchestration contract requires it.

This command is the canonical departmental entrypoint. For a monthly or last-30-days review, the
Google Ads Lead must run `google-ads-monthly-review` first, receive its zone-led action register, then
classify authority and dispatch eligible specialist skills sequentially. Do not enter through a
downstream action skill or reuse an earlier action register unless the arguments explicitly request
a resume.

Optional context from me: $ARGUMENTS
