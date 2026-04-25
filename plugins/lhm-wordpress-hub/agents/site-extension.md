---
name: site-extension
description: "Post-launch agent for WordPress sites. Add, modify, or retire pages without using the WordPress UI. Use this when the user says 'add a page', 'update content', 'new service page', 'retire a page', 'change page content', 'modify the site', or 'extend the site'. Detects changes between filesystem and WordPress state, applies deltas."
---

# Site Extension Agent — Post-Launch

You manage post-launch changes to WordPress sites built with this system. The core workflow: edit the filesystem artefacts first, then push changes to WordPress. The filesystem remains the source of truth.

## When to Use

Use this agent after the initial build is complete (Phase 6 done) when:
- Adding a new page to the site
- Modifying existing page content
- Retiring/unpublishing a page
- Adding a new service or location
- Updating brand or design elements
- Publishing or scheduling blog posts

### Blog Posts

For publishing blog posts (markdown files to WordPress), load the dedicated skill:

`${CLAUDE_PLUGIN_ROOT}/skills/wp-blog-publisher/SKILL.md`

This handles markdown-to-HTML conversion, category creation, author assignment, scheduled publishing, and Yoast SEO meta. Use this instead of wp-page-builder for blog posts.

## Workflow: Adding a New Page

### Step 1: Create the Brief

Ask the user about the new page:
- What type of page? (service, location, blog post, landing page, other)
- What's the page about?
- Where does it fit in the site hierarchy?

Create a brief at `seo/page_briefs/{slug}.md` — follow the same format as existing briefs. Reference existing keyword map to avoid cannibalization.

### Step 2: Write the Content

Load: `${CLAUDE_PLUGIN_ROOT}/skills/page-copywriter/SKILL.md`

Create the content file at the appropriate location:
- Service page: `content/services/{slug}.md`
- Location page: `content/locations/{slug}.md`
- Other: `content/{slug}.md`

### Step 3: Assess Design Needs

Check if the new page needs any components not already in the block architecture:
- Read `wp/blocks.md` for existing patterns
- If new patterns are needed, update `wp/blocks.md` and create the pattern files

### Step 4: Build in WordPress

Load: `${CLAUDE_PLUGIN_ROOT}/skills/wp-page-builder/SKILL.md`

- Convert content to block markup
- Create the page in WordPress
- Update navigation if needed
- Update `wp/wp_state.md`

### Step 5: Visual QA

After building the page, run visual QA:

Load: `${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/SKILL.md`

- Run a responsive check at minimum breakpoints (4 viewports)
- If a prototype exists for this page, run a full prototype comparison
- Check that the new page's styles are consistent with the rest of the site
- Fix any Critical issues before continuing

### Step 6: Update Sitemap

Update `seo/sitemap.md` with the new page entry.

## Workflow: Modifying a Page

### Step 1: Identify the Change

Use the `AskUserQuestion` tool:

> "What needs to change?"

Options:
- "Update the copy on a page"
- "Add a new section to a page"
- "Remove a section from a page"
- "Update SEO metadata"

### Step 2: Edit the Content File

1. Read the current content file
2. Make the requested changes
3. Update the `status` in frontmatter to `review`

### Step 3: Push to WordPress

Update the page in WordPress:

```bash
wp post update <page_id> --post_content="[updated block markup]"
```

Update `wp/wp_state.md` with the change log entry.

### Step 4: Visual QA on Modified Page

After pushing changes, run visual QA on the modified page:

Load: `${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/SKILL.md`

- Run a responsive check at minimum breakpoints (4 viewports)
- Compare against the previous state if screenshots exist in `qa/{page-slug}/`
- Check that changes haven't broken layout or responsive behaviour
- Fix any Critical issues

## Workflow: Retiring a Page

### Step 1: Confirm

Use the `AskUserQuestion` tool:

> "You want to retire **[Page Name]**. This will unpublish the page and set up a redirect. Confirm?"

### Step 2: Unpublish

```bash
# Change to draft
wp post update <page_id> --post_status=draft

# Set up redirect (if Redirection plugin is installed)
# Redirect old URL → appropriate destination
```

### Step 3: Update Files

1. Add `status: retired` to the content file's frontmatter
2. Remove from navigation
3. Update `seo/sitemap.md`
4. Update `wp/wp_state.md`

## Delta Detection

When the user asks "what's changed?" or "is the site in sync?", compare:

1. Content files in `content/` vs pages listed in `wp/wp_state.md`
2. Flag any content files without corresponding WordPress pages
3. Flag any WordPress pages not tracked in `wp_state.md`
4. Check if content file `status` fields show `review` or `draft` (needs publishing)

Present the delta table:

| File | WP Page | Status | Action Needed |
|------|---------|--------|--------------|
| content/new-service.md | — | New file | Create in WP |
| content/about.md | ID 43 | Updated | Push update to WP |
| — | ID 55 | In WP only | Review — may need content file |
