---
name: lhm-context-research-source-handoff
description: Acquire registered campaign evidence through the bounded host route.
---
# Context and Research source handoff
Use only exact per-run registered identifiers. Invoke `/opt/data/profiles/lhm_brain/bin/source-dispatch submit` with `source_policy: all_required`, saved role and exact return point. Never retrieve Drive or Fathom directly inside Hermes. A missing or mismatched receipt is a hard stop: do not claim `context_research.acquire_required_sources` complete.
