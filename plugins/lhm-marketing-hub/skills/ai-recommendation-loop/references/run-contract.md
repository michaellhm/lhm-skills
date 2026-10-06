# Run configuration and evidence contract

Store runtime client data only in the client's verified destinations. This is a template, not a live configuration. Resolve every required field from a verified record or authorised user instruction.

```yaml
client: {id: null, name: null, aliases: [], website: null, category: null}
buyer: {scenario: null, geography: null, language: null}
mode: baseline
run_id: null
panel: {version: null, core_questions: [], exploratory_questions: [], repetitions: 3}
collection: {engine: null, surface: null, model: unknown, search_setting: null, location: null}
delivery_destinations: {google_drive: null, knowledge_state: null}
website: {repository_or_cms: null, staging_branch: null, staging_url: null, rollback_reference: null}
reviewer: {identity: null, email: null, basicops_project: null, basicops_parent: null}
authority: {analysis: null, staging: null, email: null, task: null, production: null, outreach: null}
schedule: {runtime: null, timezone: null, cadence: null, id: null, collection_budget: null}
```

## Evidence files

Within the registered client deliverable destination use `ai-recommendation-loop/YYYY-MM/<run-id>/` unless that destination specifies another layout. Save configuration, question panel, raw response files, observations, scorecard, diagnosis, accepted brief references and change/review log. Read back each required artefact. Canonical state links to these files and records the next stage; avoid duplicating private raw evidence in public Git repositories.

Question fields: `question_id`, `panel_version`, `exact_prompt`, `intent`, `cohort` (discovery/branded), `buyer_scenario`, `relevance_evidence`.

Observation fields: `run_id`, `question_id`, `repeat`, `captured_at`, `timezone`, `engine`, `surface`, `model`, `language`, `location`, `session_conditions`, `search_setting`, `search_observed`, `status` (valid/failed/missing), `raw_answer_reference`, `businesses`, `citations`, `provenance`.

Each business observation: `canonical_name`, `answer_alias`, `mentioned`, `recommended`, `accuracy` (accurate/inaccurate/unknown), `accuracy_evidence`, `position` (positive integer or null for unordered), `qualification_excerpt`. Each citation: exact URL, resolved domain, page type, client-owned boolean, access/verification result. Unknown accuracy never counts as verified accurate.

## Metric definitions

Calculate separately per engine/surface/model/panel and discovery/branded cohort, then by intent. Let N be valid runs in that group. If N is zero, output unavailable, never zero percent. A valid response that names no businesses is a valid negative. Missing/failed calls are excluded from N and reported as coverage loss. Flag any question with fewer than three valid repetitions.

- Mention rate = runs naming the client / N.
- Recommendation rate = runs explicitly offering the client as a suitable option / N. A bare mention, negative assessment or branded verification statement is not a recommendation.
- Accurate recommendation rate = runs recommending the client with verified accurate material facts / N. Also show the number with unknown accuracy.
- Misdescription rate = runs with material verified client errors / N; show count and incorrect statements.
- Mean position = mean recorded client positions among ranked mentions only; report ranked count, unordered count and absences separately.
- Site citation rate = runs citing at least one client-owned URL / N. Multiple URLs in one run still count once.
- Competitor share of mentions = runs mentioning a given business / sum of run-business mention counts for the fixed tracked business set. Deduplicate each business within a run. State the tracked set; distinguish this from mention rate. If the set changes, recalculate both periods for a common set or mark non-comparable.
- Cited-domain frequency = valid runs citing that domain, deduplicated within each run. Preserve every URL in raw evidence.

For deltas preserve numerator/denominator, coverage, panel and conditions in both periods. Do not silently compare a partial current panel against a complete prior panel. Use the common complete question set as a labelled secondary analysis or report the comparison unavailable. No statistical significance claim from three repeats.

## Change and handoff record

For every action record source observation, verified gap, hypothesis/confidence, current URL/revision, proposed change, accepted brief/copy, owner, authority, status, dependencies and test. After staging include candidate SHA/revision, deployment ID, observed URLs, verification results and rollback. Record review task ID/URL, email message ID/state, notified revision, reviewer decision and approved release revision. Capture production URL, verified release time and index/exposure evidence before relating work to future visibility.

Review email template: subject `[Client] website changes ready to check`; body introduces the batch, links each verified staging page, explains changes and checks, lists unresolved decisions, links the review task if verified, and asks the reviewer to check and explicitly approve the named revision for release. Adapt to the client's established tone and authorised recipient.

BasicOps review payload: outcome-based title, verified owner/destination, due date unset unless authorised, brief Discussion with page links, rationale, candidate revision, evidence, acceptance checklist, production approval pending and next handoff. Apply the shared task manager's metadata and AI attribution rules.

Monthly summary: measurement coverage; discovery and branded scorecards; per-intent and competitor changes; cited sources; production changes since last run; observed errors; hypotheses/confidence; qualified lead evidence; selected next actions; pending reviewer decision; verified artefact links.

## Scorecard calculator

Use the bundled standard-library calculator after observations are classified and evidence saved:

```sh
python3 scripts/scorecard.py /absolute/path/observations.json --output /absolute/path/scorecard.json
```

Run from this skill directory or use the absolute script path. The input envelope contains `client_name` (canonical spelling), `tracked_businesses` (canonical names), `repetitions`, `questions` and `observations`. Each question requires `question_id`, `cohort` and `intent`. Each observation requires every series field from the evidence contract plus `panel_version`, `question_id`, `repeat`, `status`, `raw_answer_reference`, `businesses` and `citations`. Use explicit string `unknown` for unobserved series settings. Aliases must be resolved against the verified client/competitor fact set before calculation. Business entries require `canonical_name`, boolean `mentioned`/`recommended`, `accuracy`, evidence when accuracy is classified, and nullable `position`. Citation entries require an absolute `url` and verified boolean `client_owned`.

The calculator validates evidence references, classifications and duplicate runs, separates branded/discovery and per-intent results, preserves partial coverage, and separates changed collection conditions. It does not fetch answers, verify facts, classify recommendations or calculate causal/monthly deltas. Those require the captured evidence and comparison protocol. With no observations, it returns no measured groups; report baseline uncollected. Keep the input beside the output for audit.

Run behavioural metric regressions with `python3 -m unittest discover -s tests -v` from this skill directory. Test fixtures are synthetic and must never enter client baseline results.
