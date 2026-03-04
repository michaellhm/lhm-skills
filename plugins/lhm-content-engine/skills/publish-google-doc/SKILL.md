---
name: publish-google-doc
description: "Create a formatted Google Doc containing the final blog article and social posts for client review. Use this when the user mentions 'publish to Google Doc', 'create Google Doc', 'push to docs', 'format for review', or 'Google Doc draft'. Creates a structured document with meta fields, blog content, and social posts for review and approval. Returns the Google Doc URL."
---

# Publish Google Doc

Creates a formatted Google Doc containing the final blog article, social posts, meta fields, and all relevant details for client review and approval. Only called when the quality controller returns a compliance confidence of high or medium.

## When to Use This Skill

- After content passes the quality controller with high or medium compliance confidence
- Called by the run-batch orchestrator as step 5 per article
- When the user wants to push finished content to Google Docs for review

## Input

```json
{
  "blog_final": "",
  "social_final": [
    { "label": "01", "content": "" },
    { "label": "02", "content": "" },
    { "label": "03", "content": "" }
  ],
  "faq_schema_final": {},
  "slug": "",
  "meta_title": "",
  "meta_description": "",
  "primary_keyword": "",
  "client_name": "",
  "google_drive_folder_id": ""
}
```

## Instructions

### 1. Pre-Flight Check

Read `${CLAUDE_PLUGIN_ROOT}/skills/publish-google-doc/LEARNED.md` and apply any relevant entries.

Verify all required input fields are present and non-empty. If any field is missing, return an error JSON.

### 2. Create the Google Doc

Use the Google Docs API (via available tools or scripts) to create a new document.

**Document title format**:
```
{Client Name} | {Primary Keyword} | Draft
```

**Document structure** (in this exact order):

```
PRIMARY KEYWORD: {primary_keyword}
SLUG: {slug}
META TITLE: {meta_title}
META DESCRIPTION: {meta_description}

---

{Full blog article content - converted from markdown to Google Doc formatting}

---

SOCIAL POSTS FOR REVIEW AND APPROVAL

Post #01
{social post 01 content}

Post #02
{social post 02 content}

Post #03
{social post 03 content}

---

FAQ SCHEMA (JSON-LD)
{faq_schema_final formatted as code block}
```

### 3. Formatting Rules

- H1 in the blog content maps to Heading 1 in Google Docs
- H2 maps to Heading 2
- H3 maps to Heading 3
- Bold markdown maps to bold text
- Bullet lists map to bulleted lists
- Internal links remain as clickable hyperlinks
- Social posts should be clearly separated with horizontal rules
- Meta fields section at the top should use a monospace or distinct format for clarity

### 4. Place in Correct Folder

Move or create the document in the specified Google Drive folder using the `google_drive_folder_id`.

If the folder ID is invalid or inaccessible, return an error with the folder ID for debugging.

### 5. Return the URL

Extract and return the Google Doc URL for tracking and CSV update.

## Output

```json
{
  "google_doc_url": "",
  "google_doc_id": "",
  "document_title": ""
}
```

## Error Output

```json
{
  "error": true,
  "reason": "",
  "google_drive_folder_id": ""
}
```

## Implementation Notes

This skill requires Google API access. The implementation approach depends on available tooling:

**Option A: Google Apps Script** - if the client has a Google Apps Script endpoint set up, call it with the document content as a payload.

**Option B: Google Docs API via service account** - if a service account is configured, use the Docs API directly to create and format the document.

**Option C: Manual fallback** - if no API access is available, save the content as a formatted Markdown file to the client's output folder and instruct the user to manually create the Google Doc. Return the local file path instead of a Google Doc URL.

The orchestrator should handle whichever output format this skill returns.

## Validation Checkpoints

- [ ] All input fields present and non-empty
- [ ] Document title follows the naming format
- [ ] Meta fields section is complete and at the top
- [ ] Blog content is properly formatted (headings, bold, lists, links)
- [ ] All 3 social posts are included with clear separation
- [ ] FAQ schema is included as a code block
- [ ] Document is in the correct Google Drive folder
- [ ] Google Doc URL is returned and accessible

## Related Skills

- **quality-controller** - produces the final content consumed here
- **update-csv** - receives the Google Doc URL from this skill
- **run-batch** - orchestrates this skill as step 5 per article
