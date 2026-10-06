# Agent handoffs

The orchestrator owns the tracker, scope and scheduling. All subagents inherit project instructions but receive explicit file paths and a bounded page assignment. No worker can approve its own output as independent review.

| Agent | Inputs | Saved output | Acceptance |
|---|---|---|---|
| Research and comparison | Live URL, existing draft, playbook, profile, learnings | Source ledger and old/new positioning comparison | Facts traced to sources; conflicts and gaps identified |
| Page brief | Research, family contract, approved examples | Outline, section/component map, facts, SEO intent, links, media and CTA | Fits the family while answering this page's intent |
| Copywriter | Accepted brief and source pack | Full section-keyed copy plus metadata | No fabricated facts; traceable claims; no unresolved public placeholders |
| Anti-AI editor | Copy, voice, learnings and writing guidelines | Edited copy and change report | Natural specific language; facts preserved |
| Healthcare reviewer | Edited copy, claim sources, official current guidance | Issue list with severity, suggested fixes and source links | No unresolved material compliance/claim issues |
| Astro integrator | Passing copy, template, verified media, repo instructions | Source changes and integration report | Existing patterns reused; build, routes and responsive checks pass |

Reviewer contexts should be fresh: give them the actual source pack and draft rather than the writer's assurance that it passed. The healthcare reviewer must inspect edited copy, not only the original draft. If edits subsequently change clinical meaning, return them to compliance review.

Examples of bounded requests:

- Research: 'Compare this live service page with the selected playbook and existing service references. Save research.md; do not write copy or edit the website.'
- Editor: 'Edit copy.md using this client's voice and writing guidelines. Save editor-review.md and the revised copy. Identify any wording change that affects factual meaning.'
- Integration: 'Integrate these reviewed sections into the discovered Astro pattern. Preserve unrelated changes. Build and inspect the page locally. Publish only to the destination explicitly recorded in project.md.'

Keep artifacts incremental and attributable. Agent completion is not sufficient: the orchestrator checks the saved output and updates the tracker. Use the platform's subagent tools, not user-owned chats, for internal workers. If a worker fails, retain completed artifacts and retry only the failed stage. Never describe sequential self-review as an independent agent review.
