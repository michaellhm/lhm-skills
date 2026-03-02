---
name: lp-deploy-3
description: "Deploy all remaining landing pages (ad groups 2, 3, etc.) to WordPress after the primary page has been set up. Use this when the user says 'deploy the rest', 'deploy remaining pages', 'lp-deploy-3', 'add the other landing pages', 'build the remaining ad group pages', or 'deploy all pages'. Requires lp-deploy-1 (and ideally lp-deploy-2) to have run on the primary page."
---

# LP Deploy 3 — Deploy Remaining Landing Pages

Build and push every remaining ad group's landing page to WordPress. Each page follows the same deployment pattern as deploy-1 (HTML push) and optionally deploy-2 (block conversion), but the process is batched since the subsite is already configured and the CSS is already in the theme.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-deploy-3/LEARNED.md`
2. Read `lp/lp_state.md` — identify:
   - Subsite URL and container name
   - Which ad groups have prototypes ready
   - Which pages are already deployed (status "HTML Live" or "Blocks Live")
   - The Post ID of the first deployed page (for CSS reference)
3. Check that `/lp/prototype/` has HTML files for each remaining ad group

If any ad group is missing a prototype, stop and ask the user to run lp-prototype for that group first.

**Prefer the client's `wp/wp-cli.sh` helper** over raw `docker exec` commands. It auto-installs WP-CLI and passes the correct `--url` flag. Container name is `wp-wordpress-1`. The healthcare-theme CSS file is `assets/css/custom-components.css` (not `custom.css`). Theme files can be edited directly via the client's `wp/healthcare-theme` symlink to the central canonical copy.

## Step 1: Confirm Deployment Scope

Use the `AskUserQuestion` tool:

> "Here are the remaining ad groups ready to deploy:
>
> [list each ad group with prototype path]
>
> Should I deploy all of them, or start with specific ones?"

Options:
- "Deploy all remaining pages"
- "Deploy [specific ad groups]"
- "Deploy as HTML only (I'll convert blocks separately)"

Default to HTML-only deployment. Block conversion per page can run after each HTML push is approved.

## kses and Content Placement Warnings

`wp_update_post()` strips `<iframe>` tags via kses sanitisation. When batch-deploying pages with Google Maps embeds or video iframes, use `$wpdb->update()` + `clean_post_cache()` instead. See `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for the pattern.

When inserting content into service cards or group blocks via string replacement, place new blocks BEFORE the closing `</div>`, not between `</div>` and `<!-- /wp:group -->`. The `</div>` closes the rendered DOM element.

## Step 2: Verify CSS is Already Present

Since deploy-1 already pushed the prototype CSS to the theme, the remaining pages should render correctly without any additional CSS changes. However, if the remaining ad groups have unique sections not in the primary page prototype, extract and append any new CSS rules before creating those pages.

Check for new classes in each remaining prototype that don't exist in the theme's custom.css.

## Step 3: Deploy Each Remaining Page

For each remaining ad group, run the following sequence. This mirrors deploy-1 steps 2-8 but without the subsite setup.

### 3a. Extract and Slice Content

Read `/lp/prototype/[SLUG]/index.html`. Extract everything between the `<header>` and `<footer>` tags. Wrap each `<section>` in `<!-- wp:html -->` blocks:

```html
<!-- wp:html -->
<section class="[SECTION_CLASS]">
  [section content]
</section>
<!-- /wp:html -->
```

Save to `/lp/deploy/[SLUG]-content.html`.

### 3b. Create the Page

```bash
# Copy content file into container
docker cp lp/deploy/[SLUG]-content.html $CONTAINER:/tmp/[SLUG]-content.html

# Create page
PAGE_ID=$(docker exec $CONTAINER wp --allow-root post create \
  --post_type=page \
  --post_title="[AD GROUP] [SERVICE] | [CLINIC_NAME]" \
  --post_name="[SLUG]" \
  --post_status=publish \
  --post_content="$(docker exec $CONTAINER cat /tmp/[SLUG]-content.html)" \
  --url=[SUBSITE_URL] \
  --porcelain)

echo "[AD GROUP] page created: $PAGE_ID"
```

### 3c. Link Location Data

```bash
docker exec $CONTAINER wp --allow-root post meta update $PAGE_ID \
  _healthcare_location_id [LOCATION_CPT_ID] \
  --url=[SUBSITE_URL]
```

### 3d. Verify Frontend

Open `[SUBSITE_URL][SLUG]/` and confirm:
- All sections are visible
- Colours and typography match the prototype
- No layout breakage from missing CSS

Record each page in the state file immediately after verification (not in a batch at the end).

## Step 4: Build a Page Index (Optional but Recommended)

Create a simple HTML page or use the WordPress custom post type list to give you a quick index of all deployed landing pages. This helps Michael review them all from one place.

```bash
# List all published pages
docker exec $CONTAINER wp --allow-root post list \
  --post_type=page \
  --post_status=publish \
  --fields=ID,post_title,post_name \
  --url=[SUBSITE_URL] \
  --format=table
```

Write this list to `/lp/deploy/page-index.md`:

```markdown
# Landing Page Index

| Ad Group | Page Title | URL | Post ID | Status |
|----------|-----------|-----|---------|--------|
| [Ad Group 1] | [Title] | [SUBSITE_URL][slug]/ | [ID] | HTML Live |
| [Ad Group 2] | [Title] | [SUBSITE_URL][slug]/ | [ID] | HTML Live |
```

## Step 5: Block Conversion (Per Page)

For each page, use the `AskUserQuestion` tool after the HTML push:

> "[AD GROUP] page is live at [URL]. Does it look right? Ready to convert to Gutenberg blocks?"

Options:
- "Yes — convert to blocks"
- "Skip — leave as HTML for now"
- "Needs fixes — [describe issue]"

If approved: read `${CLAUDE_PLUGIN_ROOT}/skills/lp-deploy-2/SKILL.md` and run the block conversion for that page before moving to the next.

If skipping: note status as "HTML Live — block conversion pending" in the state file and continue with the next page.

## Step 6: Final State Update

After all pages are deployed, update `/lp/lp_state.md` with the complete Pages Built table. Mark the campaign as "All pages deployed".

Add a summary to the state file:

```markdown
## Deployment Summary
- **Total pages deployed**: [N]
- **Pages in native blocks**: [N]
- **Pages as HTML blocks**: [N] (pending conversion)
- **Deployed by**: lp-deploy-3
- **Date**: [YYYY-MM-DD]
```

## Handoff

Tell the user:

> "All [N] landing pages are live on the subsite:
>
> [list each page with URL]
>
> Pages still in HTML blocks: [list if any] — run **lp-deploy-2** for each when you're ready to make them fully editable in Gutenberg.
>
> Review the page index at `/lp/deploy/page-index.md`."
