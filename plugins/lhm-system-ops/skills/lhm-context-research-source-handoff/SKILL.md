---
name: lhm-context-research-source-handoff
description: Acquire every required allowlisted source and produce a verified evidence package.
---

# Context and Research durable handoff

Follow `../../references/source-production-contract.md`. At
`context_research.acquire_required_sources`, invoke only the bounded Claude research route for the
manifest's exact allowlisted Google Drive file and Fathom transcript declarations. Require an
identifier-bound retrieval receipt and content digest for every source.

If retrieval is unavailable, persist the parent and a typed capability blocker and route it to CTO.
Do not draft, complete, silently omit a source, accept conversational identifiers or expose connector
credentials to Hermes. Build the evidence package only after every `all_required` receipt validates,
then dispatch Head of Production with the package digest and unchanged parent identity.
