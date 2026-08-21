---
name: website-delivery-qa
description: "Verify Prototype, Astro or WordPress delivery against its dispatch envelope, artefact, approval boundary and completion test."
---

# Website Delivery QA

Independently verify the named Lead and required `start-*` entry skill, source and artefact readback, correct specialist skill, mutation boundary, relevant checks, and any publication's observed commit, branch and URL. Do not repair during QA.

Return exactly one verdict: `pass`, `correction_required`, `waiting_approval`, or `blocked`, with evidence. Missing entry-skill evidence is `correction_required`; unavailable destination or permission is `blocked`; prepared but unapproved publishing is `waiting_approval`.
