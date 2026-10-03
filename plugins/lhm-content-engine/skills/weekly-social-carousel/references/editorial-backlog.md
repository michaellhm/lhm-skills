# Editorial backlog

## Purpose

The backlog keeps useful ideas from disappearing when they are not selected in the week they surface. It separates source discovery from carousel production so Michael can review, reprioritise and request specific posts later.

## Files

For LHM Social, maintain:

- `planning/editorial-backlog.md`: safe human review file
- `planning/editorial-backlog.private.json`: private provenance and deduplication data

The Markdown file is never a transcript index. Do not include people, clinic names, locations, meeting titles, private figures, direct quotes, Fathom URLs or recording IDs. Those belong only in the private JSON record.

## Candidate workflow

1. Extract every safe, distinct idea from the authorised source period.
2. Merge candidates that express the same audience problem. Increase the recurrence evidence instead of creating duplicates.
3. Assign a stable ID such as `LHM-IDEA-001`.
4. Score the candidate using the editorial strategy's six criteria.
5. Write or update the Markdown review row.
6. Store private provenance against the same ID in the private JSON file.
7. Select posts from all `ready` entries, including carry-over ideas from earlier weeks.
8. After production, mark the entry `published` and add its package slug.

## Markdown format

Start the file with a short legend, followed by this table:

```markdown
| ID | Idea | Lane | Frequency | Value | Freshness | Total | Status | Why it matters |
|---|---|---|---:|---:|---:|---:|---|---|
| LHM-IDEA-001 | Simplify online booking choices | practical-shortcut | 4 | 4 | 3 | 22/24 | ready | Too many choices can interrupt a high-intent booking. |
```

Use these statuses:

- `ready`: clears the quality floor and can be selected
- `review`: promising, but Michael should choose the angle or more research is needed
- `hold-low-frequency`: useful but too uncommon for automatic weekly selection
- `selected`: chosen for the current production batch
- `published`: package created; include the slug in the idea text or notes

Unsafe candidates are discarded and never added to the Markdown file.

## Private JSON format

```json
{
  "schema_version": "1.0",
  "updated_at": "ISO-8601",
  "ideas": {
    "LHM-IDEA-001": {
      "source_type": "fathom | first-party-web | last30days",
      "sources": [
        {"url": "private source URL", "recording_id": 123, "timestamp_seconds": 456}
      ],
      "dedupe_key": "simplify-online-booking-choices",
      "recurrence_count": 2,
      "notes": "Private verification notes."
    }
  }
}
```

The private file supports provenance and recurrence scoring. It is not a public content artefact and must never enter the site build, slide ZIPs or social uploads.
