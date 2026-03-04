---
name: update-csv
description: "Update the content pipeline CSV with slug, meta fields, Google Doc URL, and new status after article processing. Use this when the user mentions 'update CSV', 'update the spreadsheet', 'mark as drafted', 'update tracking', or 'CSV status update'. Writes back to the source CSV file, updating the processed row with generated metadata and status."
---

# Update CSV

Updates the content pipeline CSV file with the generated slug, meta title, meta description, Google Doc URL, and new status for a processed article row. This is the final step in the per-article pipeline.

## When to Use This Skill

- After a Google Doc has been published (or after a compliance halt)
- Called by the run-batch orchestrator as step 6 per article
- When the user needs to update the tracking CSV with results

## Input

```json
{
  "csv_path": "",
  "row_identifier": {
    "client_name": "",
    "topic": "",
    "primary_keyword": ""
  },
  "updates": {
    "slug": "",
    "meta_title": "",
    "meta_description": "",
    "google_doc_url": "",
    "status": "Drafted | Needs Review"
  }
}
```

The `row_identifier` is used to find the correct row. Match on `Client Name` + `Topic` + `Primary Keyword` combination for uniqueness.

## Instructions

### 1. Pre-Flight Check

Read `${CLAUDE_PLUGIN_ROOT}/skills/update-csv/LEARNED.md` and apply any relevant entries.

Verify:
- CSV file exists at the specified path
- The row identifier matches exactly one row in the CSV
- All update fields are present

### 2. Read the CSV

Read the entire CSV file. Parse it preserving:
- All existing columns and their order
- All existing data in non-target rows
- Header row exactly as-is

### 3. Locate the Target Row

Find the row where:
- `Client Name` matches `row_identifier.client_name` (case-insensitive)
- `Topic` matches `row_identifier.topic` (case-insensitive)
- `Primary Keyword` matches `row_identifier.primary_keyword` (case-insensitive)

If no match found, return error. If multiple matches found, return error (data integrity issue).

### 4. Update the Row

Update these columns in the matched row:

| Column | Value | Notes |
|--------|-------|-------|
| Slug | `updates.slug` | Add column if it doesn't exist |
| Meta Title | `updates.meta_title` | Add column if it doesn't exist |
| Meta Description | `updates.meta_description` | Add column if it doesn't exist |
| Google Doc URL | `updates.google_doc_url` | Add column if it doesn't exist. Empty string if compliance halt. |
| Status | `updates.status` | "Drafted" for success, "Needs Review" for compliance halt |

### 5. Write Back

Write the updated CSV back to the same file path. Preserve:
- Original column order (new columns appended at end)
- All other rows unchanged
- Proper CSV escaping (quote fields containing commas, newlines, or quotes)
- UTF-8 encoding
- No trailing newline issues

### 6. Verify the Write

Re-read the CSV after writing to confirm:
- The target row has the updated values
- No other rows were modified
- Total row count is unchanged
- No data corruption

## Output

```json
{
  "success": true,
  "csv_path": "",
  "row_updated": {
    "client_name": "",
    "topic": "",
    "new_status": "",
    "slug": "",
    "google_doc_url": ""
  }
}
```

## Error Output

```json
{
  "error": true,
  "reason": "",
  "csv_path": "",
  "row_identifier": {}
}
```

Possible error reasons:
- `csv_not_found` - file doesn't exist at path
- `row_not_found` - no matching row for the identifier
- `multiple_matches` - more than one row matches (data integrity issue)
- `write_failed` - could not write back to CSV
- `verification_failed` - post-write verification found issues

## Validation Checkpoints

- [ ] CSV file exists and is readable
- [ ] Exactly one row matches the identifier
- [ ] All update fields written correctly
- [ ] No other rows modified
- [ ] Total row count unchanged after write
- [ ] CSV is properly escaped and encoded
- [ ] Post-write verification passes

## Related Skills

- **publish-google-doc** - provides the Google Doc URL updated here
- **run-batch** - orchestrates this skill as the final step per article
