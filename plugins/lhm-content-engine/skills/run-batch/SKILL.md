---
name: run-batch
description: "Orchestrate the full content pipeline for all approved rows in a CSV. Use this when the user mentions 'run batch', 'process all articles', 'run the pipeline', 'batch content', 'process CSV', 'start the batch', or 'run content engine'. Iterates through each Approved row, chains all skills (generate-outline, write-blog, generate-social-posts, quality-controller, publish-google-doc, update-csv) with structured JSON handoff, isolates each article execution, and logs results per article."
---

# Run Batch Orchestrator

Orchestrates the full content pipeline for all approved rows in the input CSV. For each row with Status = Approved, chains through all skills in sequence with structured JSON handoff. Isolates each article's execution to prevent cross-contamination.

## When to Use This Skill

- Processing multiple articles from a content CSV
- Running the full pipeline end-to-end
- When the user wants to batch-process all approved content

## Input

```json
{
  "csv_path": "",
  "client_folder_root": "/clients/",
  "google_drive_folder_id": ""
}
```

## Instructions

### 1. Pre-Flight Check

Read `${CLAUDE_PLUGIN_ROOT}/skills/run-batch/LEARNED.md` and apply any relevant entries.

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

Verify:
- CSV file exists and is readable
- CSV has all required columns: Client Name, Topic, Primary Keyword, Secondary Keywords, ICP, Intent, Word Count, Internal Links, Brief Filename, Status
- At least one row has Status = Approved
- Client folder root exists

### 2. Filter Approved Rows

Parse the CSV and collect only rows where `Status` = `Approved` (case-insensitive match).

Present a summary to the user before processing:

```
Found {N} approved articles to process:
1. {Client Name} — {Topic} ({Word Count} words)
2. {Client Name} — {Topic} ({Word Count} words)
...

Proceed with batch processing?
```

Use `AskUserQuestion` to confirm. Do not proceed without user approval.

### 3. Validate Client Folders

For each unique client in the approved rows, verify their client folder exists and contains all required files:

- `/clients/{client-name}/articles/client-background.md`
- `/clients/{client-name}/articles/brand-voice.md`
- `/clients/{client-name}/articles/compliance.md`
- `/clients/{client-name}/articles/published-articles.json`
- `/clients/{client-name}/articles/services.json`

Also verify each row's `Brief Filename` exists at `/clients/{client-name}/articles/briefs/{brief-filename}`.

If any file is missing, report all missing files before starting. Do not start processing until all files are confirmed.

### 4. Process Each Article (Isolated Execution)

For each approved row, execute the full pipeline in sequence. **Each article is fully isolated** — do not carry state between articles. Reset context between rows.

#### Step 1: Generate Outline
Load: `${CLAUDE_PLUGIN_ROOT}/skills/generate-outline/SKILL.md`

Input:
```json
{
  "csv_row": { /* current row data */ },
  "client_folder": "/clients/{client-name}/articles/"
}
```

If the outline returns an error (e.g., duplicate topic), log it and skip to the next row.

#### Step 2: Write Blog
Load: `${CLAUDE_PLUGIN_ROOT}/skills/write-blog/SKILL.md`

Input:
```json
{
  "outline": { /* output from step 1 */ },
  "csv_row": { /* current row data */ },
  "client_folder": "/clients/{client-name}/articles/"
}
```

#### Step 3: Generate Social Posts
Load: `${CLAUDE_PLUGIN_ROOT}/skills/generate-social-posts/SKILL.md`

Input:
```json
{
  "blog_markdown": "/* from step 2 */",
  "primary_keyword": "/* from CSV row */",
  "slug": "/* from step 1 outline */",
  "client_name": "/* from CSV row */",
  "client_folder": "/clients/{client-name}/articles/"
}
```

#### Step 4: Quality Controller
Load: `${CLAUDE_PLUGIN_ROOT}/skills/quality-controller/SKILL.md`

Input:
```json
{
  "blog_markdown": "/* from step 2 */",
  "social_posts": [ /* from step 3 */ ],
  "faq_schema_json_ld": { /* from step 2 */ },
  "client_folder": "/clients/{client-name}/articles/"
}
```

**Decision point**: Check `compliance_confidence` in the output.

- If `high` or `medium`: proceed to step 5
- If `low`: skip step 5, go directly to step 6 with Status = "Needs Review"

#### Step 5: Publish Google Doc
Load: `${CLAUDE_PLUGIN_ROOT}/skills/publish-google-doc/SKILL.md`

Input:
```json
{
  "blog_final": "/* from step 4 */",
  "social_final": [ /* from step 4 */ ],
  "faq_schema_final": { /* from step 4 */ },
  "slug": "/* from step 1 */",
  "meta_title": "/* from step 1 */",
  "meta_description": "/* from step 1 */",
  "primary_keyword": "/* from CSV row */",
  "client_name": "/* from CSV row */",
  "google_drive_folder_id": "/* from orchestrator input */"
}
```

#### Step 6: Update CSV
Load: `${CLAUDE_PLUGIN_ROOT}/skills/update-csv/SKILL.md`

Input:
```json
{
  "csv_path": "/* from orchestrator input */",
  "row_identifier": {
    "client_name": "/* from CSV row */",
    "topic": "/* from CSV row */",
    "primary_keyword": "/* from CSV row */"
  },
  "updates": {
    "slug": "/* from step 1 */",
    "meta_title": "/* from step 1 */",
    "meta_description": "/* from step 1 */",
    "google_doc_url": "/* from step 5, or empty if skipped */",
    "status": "Drafted | Needs Review"
  }
}
```

### 5. Log Processing Results

Maintain a running log during batch processing. After all articles are processed, present the full log:

```
BATCH PROCESSING COMPLETE
========================

Processed: {N} articles
Drafted:   {N} (published to Google Docs)
Needs Review: {N} (compliance concerns)
Skipped:   {N} (errors)

Article Results:
1. ✅ {Client} — {Topic} → Drafted | Doc: {URL}
2. ⚠️ {Client} — {Topic} → Needs Review | Reason: {compliance notes}
3. ❌ {Client} — {Topic} → Skipped | Reason: {error reason}
...
```

### 6. Isolation Rules

These rules are non-negotiable:

- **No shared state**: each article starts with a clean context. Do not reference content from a previous article.
- **No cross-contamination**: keywords, outlines, and content from article A must not leak into article B.
- **Independent errors**: if article A fails, article B must still process normally.
- **Sequential CSV updates**: update the CSV after each article completes, not in a batch at the end. This prevents data loss if processing is interrupted.

## Output

The final output is the batch log (displayed to the user) plus the updated CSV file. No additional JSON output is needed from the orchestrator itself.

## Validation Checkpoints

- [ ] CSV exists with all required columns
- [ ] Only Approved rows are processed
- [ ] User confirmed the batch before processing started
- [ ] All client folders and files verified before first article
- [ ] Each article processed in full isolation
- [ ] Compliance halt correctly applied when confidence = low
- [ ] CSV updated after each article (not batched at end)
- [ ] Final log accurately reflects all processing results
- [ ] No cross-contamination between articles

## Related Skills

- **generate-outline** — step 1 per article
- **write-blog** — step 2 per article
- **generate-social-posts** — step 3 per article
- **quality-controller** — step 4 per article
- **publish-google-doc** — step 5 per article (if compliance passes)
- **update-csv** — step 6 per article
