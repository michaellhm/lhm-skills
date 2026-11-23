# Client writing guide and evidence

`how-to-write.md` is the compact instruction file future writers read. Use these sections, adapting depth to the available evidence:

- Identity, guide revision, inspected head and comparison baseline; exact paths to profile/campaign/sitemap and evidence pack.
- Source coverage: route, source paths, approved revision/approver/evidence, current-match status. Explain excluded/pending pages.
- Positioning in plain language; distinguish strategy from proved clinical claims.
- How to write: tone, vocabulary, opening approach, service/condition differences, paragraph/FAQ/CTA conventions; short source-linked examples.
- Client edit lessons: stable ID, scope, status (`confirmed instruction`, `observed pattern`, `proposed`, `superseded`), before/after or quote, date/commit/path, implication and exceptions.
- Page/service facts: exact scope, source/date and recheck triggers. Do not generalise a fee, clinician, referral or clinic correction across services.
- Presentation/media and functionality preferences, separate from writing rules.
- Avoid/retain examples and unresolved conflicts, including risky wording awaiting review.
- Next-writer checklist: required context, guide revision/rule IDs, factual checks, explicit template and accepted sitemap mapping, existing editorial/clinical checks.
- Refresh log and cursor: added/changed/superseded lessons; repeated runs deduplicate evidence. List actual scope, not an unqualified "all edits" claim.

Detailed raw diffs and corpus can live in the evidence pack instead of bloating the guide. Do not copy credentials, patient submissions or private staff information into either output. Quote only the short passages needed for the lesson.

## Optional Git collector

Prepare a JSON manifest from verified approval evidence. Each page must have `route`, `approved_revision`, `approval_evidence` and a nonempty list of repo-relative textual `sources`. Each supplied approved revision must identify the content the client actually reviewed; do not set HEAD simply to make the check pass. Map dynamic routes to their individual data files plus renderer, not every source file in the repo.

```json
{"pages":[{"route":"/services/example/","approved_revision":"<verified Git SHA>","approval_evidence":"<review event/link and approver>","sources":["src/data/services/example.json","src/pages/services/[slug].astro"]}]}
```

Invoke with a previously inspected baseline and known client identities:

```sh
python3 scripts/collect_evidence.py --repo /verified/site --manifest /private/run/pages.json \
  --since <comparison-sha> --head <head-sha> --client-email client@example.org \
  --output /private/run/evidence.json
```

The collector resolves revisions, requires a clean tracked worktree, rejects path escapes and public outputs, checks baseline ancestry, compares source blobs against their approved revision, and saves untruncated text/diffs. Candidate author matches are evidence to inspect, not authenticated client intent. It covers only manifest paths: client-requested agency edits, review discussions and asset changes require separate inspection and must be included in the final coverage statement. It does not fetch/clone, post to GitHub or modify approvals. Missing Git objects or files are errors, not successful partial capture.
