---
name: website-delivery-qa
description: "Verify Prototype, Astro or WordPress delivery against its dispatch envelope, artefact, approval boundary and completion test. Use for website handback QA or final completion QA after site-launch-qa and Jaimee’s review."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Website Delivery QA

Independently verify the named Lead and required `start-*` entry skill, source and artefact readback, correct specialist skill, mutation boundary, relevant checks, and any publication's observed commit, branch and URL. Do not repair during QA.

Return exactly one verdict: `pass`, `correction_required`, `waiting_approval`, or `blocked`, with evidence. Missing entry-skill evidence is `correction_required`; unavailable destination or permission is `blocked`; prepared but unapproved publishing is `waiting_approval`.

## Completed-site handback

For a finished website, apply [Website completion QA](../../references/website-completion-qa.md). Verify the combined `site-launch-qa` report includes source-linked approved client requests, browser evidence, Jaimee’s actual real-device results, performance and GTM/GA4/event/GSC evidence, required production rechecks and fix/retest disposition. Use the declared scope for an intermediate prototype/build handback; do not require live-site evidence for that stage or label an intermediate pass as project completion.

Missing required results or pending manual checks are `correction_required`; unavailable required source/account/device access is `blocked`. Failed mandatory checks need correction or documented authorised acceptance. Do not convert a prepared checklist, simulated phone viewport or published GTM snippet into a completed human or tracking test. Link the verified report in the handback; no repair, publication or automatic message is authorised by this review.
