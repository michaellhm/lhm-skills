# Brain update output and evidence

The brain update writes into the existing brain notes. It does not create a separate writing guide. `brain/Content Rules.md` carries the writing lessons; scoped facts go to the matching note.

## brain/Content Rules.md

Keep the scaffold headings (Tone and voice, Words to use, Words to avoid, Formatting preferences, Compliance) and add these sections, adapting depth to the evidence:

- **Source coverage:** route, source paths, approved revision, approver and evidence, current-match status. Explain excluded and pending pages.
- **Client edit lessons:** one entry per rule with a stable ID, scope, status (`confirmed instruction`, `observed pattern`, `proposed`, `superseded`), before/after or quote, date, commit SHA and path, implication and exceptions. Rule IDs are never reused or renumbered.
- **Presentation and functionality preferences:** layout, media, booking and form behaviour, kept separate from writing rules, with the same ID, scope, status and SHA evidence.
- **Avoid and retain examples, and unresolved conflicts**, including risky wording awaiting healthcare review.
- **Next-writer checklist:** required context, brain revision and rule IDs, factual checks, explicit template and accepted sitemap mapping, existing editorial and clinical checks.

Positioning and strategy stay in `Profile.md`; do not restate them in the rules.

## Scoped facts

Service availability, practitioner names and roles, prices, funding, hours and clinical sign-offs go in the matching note (`Services.md`, `Staff.md`, `What We Do.md`, `Who We Serve.md`, `Profile.md`) with exact scope. Add the source commit SHA and date to that note's `sources`. Do not generalise a fee, clinician, referral or clinic correction across services. Distinguish dated facts from evergreen writing style.

## brain/Change Log.md

Each run adds one entry under Entries: date, head SHA, comparison baseline, rules and facts added, changed or superseded, pages and client commits inspected, exclusions and gaps. The final line is the cursor, `<!-- last-processed: <sha> -->`, maintained only through `scripts/brain_cursor.py`. Repeat runs at the same head add no duplicate lessons and list actual scope, not an unqualified "all edits" claim.

## Evidence pack

Detailed raw diffs and corpus live in the registered client work root under `brain-updates/<run-id>/`, not in the client repo. Record head SHA, baseline, approved route and source hashes, exact inspected commits, exclusions and unresolved gaps. Do not copy credentials, patient submissions or private staff information into the brain or the pack. Quote only the short passages needed for a lesson.

## Optional Git collector

Prepare a JSON manifest from verified approval evidence. The review register stores each approval (person, evidence, timestamp, approved fingerprint) but no Git SHA, so the operator resolves each `approved_revision` from the approval commit and records it; a page with no verifiable revision is a gap and stays out of the manifest. Each page must have `route`, `approved_revision`, `approval_evidence` and a nonempty list of repo-relative textual `sources`. Each supplied approved revision must identify the content the client actually reviewed; do not set HEAD simply to make the check pass. Map dynamic routes to their individual data files plus renderer, not every source file in the repo.

```json
{"pages":[{"route":"/services/example/","approved_revision":"<verified Git SHA>","approval_evidence":"<review event/link and approver>","sources":["site/src/data/services/example.json","site/src/pages/services/[slug].astro"]}]}
```

Invoke with a previously inspected baseline and known client identities:

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/skills/update-content-brain/scripts/collect_evidence.py --repo CLIENT_REPO --manifest /work-root/brain-updates/RUN_ID/pages.json \
  --since <comparison-sha> --head <head-sha> --client-email client@example.org \
  --output /work-root/brain-updates/RUN_ID/evidence.json
```

The collector resolves revisions, requires a clean tracked worktree, rejects path escapes and any `--output` inside `--repo`, checks baseline ancestry, compares source blobs against their approved revision, and saves untruncated text/diffs. Candidate author matches are evidence to inspect, not authenticated client intent. It covers only manifest paths: client-requested agency edits, review discussions and asset changes require separate inspection and must be included in the final coverage statement. It does not fetch/clone, post to GitHub or modify approvals. Missing Git objects or files are errors, not successful partial capture.
