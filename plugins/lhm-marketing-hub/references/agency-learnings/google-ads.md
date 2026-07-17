# Agency Learnings — Google Ads

<!-- Auto-maintained. Entries added by Claude after sessions via the self-improvement protocol. Max 50 entries. Oldest unused entries pruned after 3 months. -->

<!-- Format: - (YYYY-MM-DD) [Niche if applicable] Specific, actionable observation. -->

- (2026-07-17) AdPulse MCP exposes raw `pacing`/`kpiPercentage` per budget, not a pre-computed zone color. Always pull these directly (see `references/adpulse-integration.md`) instead of hand-calculating pacing/performance from Google Ads numbers — AdPulse's configured KPI can differ from the client's stated target CPA (e.g. cost-per-conversion-vs-previous-period instead of a flat $ target).
- (2026-07-17) The zone matrix has no defined cell for Under-pacing (<90%) + Poor performance. Treat it as Red-severity, not Yellow — Yellow would wrongly recommend scaling budget into a funnel that isn't converting. See `references/adpulse-integration.md`.
- (2026-07-17) BasicOps monthly-review tasks: put the full report as a **discussion message** (`create_message_in_task`), not in the task `description` field. Keep the description to one line pointing at the discussion + the saved report file. The user corrected this explicitly after the first run.
- (2026-07-17) For a 4-avatar second-opinion panel (digital marketing expert / clinic owner / media buyer / Perry Marshall), route each avatar through a genuinely different model via the OpenRouter MCP `send-message` tool (e.g. one GPT model, one Gemini model, one Grok model). "Manus" has no callable API/model on OpenRouter — substitute a distinct-lineage model (e.g. DeepSeek) for that persona and disclose the substitution in the report rather than silently dropping it or reusing another already-used model.
