# LHM Project Hub - Plugin-Wide Rules

These rules apply to every skill and agent in this plugin.

## Mandatory: Obsidian-First Client Context

Before client-specific work, read and follow `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. Resolve legacy context filenames only inside the canonical Obsidian client root. Never create blank or parallel client context in a working directory; route missing canonical context through its owning Project Hub workflow.

## Mandatory: Delivery Artefact and Handoff Contract

Before recording, routing or handing off material work, read and follow `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md`. Require the producing specialist to return its verified canonical artefact reference. Record and link that handoff in Obsidian and BasicOps; do not recreate the deliverable or mark a required unverified artefact complete.

## BasicOps

Route every BasicOps mutation through `lhm-project-hub:basicops-task-manager`. Keep actionable context, dependencies, completion conditions and next handoff in Discussion. Use Description only for approved machine-readable metadata and useful working URLs.
