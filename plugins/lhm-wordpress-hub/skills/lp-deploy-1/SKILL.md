---
name: lp-deploy-1
description: "Push the first landing page HTML prototype into WordPress as Gutenberg HTML blocks. Use this when the user says 'deploy the landing page', 'push to WordPress', 'lp-deploy-1', 'drop in the prototype', 'set up the subsite and get the page live', or 'deploy deploy-1'. Requires lp-subsite-setup to have run and a prototype at /lp/prototype/. Wraps prototype sections in wp:html blocks and creates the WordPress page."
---

# LP Deploy 1 — Push HTML Prototype to WordPress

Take the approved HTML prototype for the primary ad group, slice it into per-section Gutenberg HTML blocks, and push it to the WordPress subsite. The goal is a pixel-perfect frontend as fast as possible — editorial editability comes in deploy-2.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-deploy-1/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/lp-reference.md` — especially "Central Multisite Infrastructure"
3. Read `lp/lp_state.md` — confirm:
   - Subsite URL and container name are present
   - Theme is activated
   - At least one prototype exists in `/lp/prototype/`
4. If lp-subsite-setup has NOT been run, stop and tell the user to run it first
5. Read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for WP-CLI patterns

Store the subsite URL and container name as variables. All WP-CLI commands in this skill require `--url=[SUBSITE_URL]`.

**Prefer the client's `wp/wp-cli.sh` helper** over raw `docker exec` commands. It auto-installs WP-CLI (which is ephemeral in `wordpress:6.7-php8.2-apache`) and passes the correct `--url` flag. The theme can also be edited directly via the client's `wp/healthcare-theme` symlink, which points to the central canonical copy.

## Step 1: Confirm Target Ad Group

Use the `AskUserQuestion` tool:

> "Which ad group's landing page should I deploy first?"

List ad groups that have a prototype ready (from lp_state.md). Default to the primary ad group.

Read the prototype file at `/lp/prototype/[SLUG]/index.html`.

## Step 2: Extract and Slice Body Content

The WordPress page only needs the page body content — not the `<head>`, `<header>`, or `<footer>` (the theme handles those in template parts).

Extract the sections between the site header and site footer:
- Start after `</header>` (or `<!-- end header -->`)
- End before `<footer` (or `<!-- start footer -->`)

Slice into individual section blocks. Each top-level `<section>` becomes a separate `<!-- wp:html -->` block. This is critical: one monolithic HTML block is impossible to debug.

**Gutenberg HTML block format:**
```html
<!-- wp:html -->
<section class="hero-section">
  [section content]
</section>
<!-- /wp:html -->

<!-- wp:html -->
<section class="trust-bar">
  [section content]
</section>
<!-- /wp:html -->
```

Save the sliced content to `/lp/deploy/[SLUG]-content.html`.

## Step 3: Push Required CSS to the Theme

The prototype's `<style>` block contains CSS that the WordPress theme doesn't have yet. Extract it and add it to the theme's custom CSS.

Check what the theme's custom CSS file is called:
```bash
docker exec $CONTAINER ls wp-content/themes/[THEME_SLUG]/assets/css/ --allow-root 2>/dev/null
```

The healthcare-theme uses `custom-components.css` (not `custom.css`). Other themes may differ. Check for the actual filename before appending.

Append the prototype CSS. If a `wp/healthcare-theme` symlink exists in the client folder, you can edit the file directly through that symlink (it points to the central canonical theme copy). Otherwise use docker cp:
```bash
docker cp /path/to/lp/prototype/[SLUG]/extracted.css [CONTAINER]:/tmp/lp-styles.css
docker exec $CONTAINER bash -c "cat /tmp/lp-styles.css >> /var/www/html/wp-content/themes/[THEME_SLUG]/assets/css/[CSS_FILENAME]"
```

Also add WordPress block gap resets if not already present:
```css
/* Reset WP default block gaps */
.wp-site-blocks > * + *,
.is-layout-flow > * + * {
  margin-block-start: 0;
}
```

If the theme uses `wp_add_inline_style` or a Customizer CSS option instead of a file, use:
```bash
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_custom_css "[CSS]" \
  --url=[SUBSITE_URL]
```

## Step 4: Enqueue Google Fonts (if needed)

If the prototype uses a Google Font, verify it is enqueued by the theme on this subsite. Check `functions.php` for the font. If missing, add it to the theme's functions.php or use the Customizer additional CSS to load it via `@import`.

## kses Sanitisation Warning

`wp_update_post()` and `wp post update` run content through kses sanitisation, which strips `<iframe>`, `<script>`, and other "unsafe" tags. If the landing page contains Google Maps embeds, video iframes, or other HTML in `<!-- wp:html -->` blocks, use `$wpdb->update()` on the posts table directly + `clean_post_cache($pid)` to bypass kses. See `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for the pattern.

Empty `<!-- wp:html -->` blocks (e.g. map placeholders) survive deployment but their embed content (iframes) needs to be populated separately after page creation using the `$wpdb->update()` bypass. Include map embeds in the initial content file where possible, or run a post-deploy PHP script.

## Step 5: Create the WordPress Page

Copy the content file into the Docker container and create the page:
```bash
# Copy file into container
docker cp lp/deploy/[SLUG]-content.html $CONTAINER:/tmp/[SLUG]-content.html

# Create the page
PAGE_ID=$(docker exec $CONTAINER wp --allow-root post create \
  --post_type=page \
  --post_title="[LANDING PAGE TITLE]" \
  --post_name="[SLUG]" \
  --post_status=publish \
  --post_content="$(docker exec $CONTAINER cat /tmp/[SLUG]-content.html)" \
  --url=[SUBSITE_URL] \
  --porcelain)

echo "Page created with ID: $PAGE_ID"
```

Note: `--porcelain` returns just the post ID, useful for follow-up commands.

**Landing page title convention:** use the ad group name + clinic name for relevance.
E.g. "Physiotherapy [Suburb] | [Clinic Name]"

## Step 6: Link Location Data to the Page

If the landing page shows location cards dynamically from the Location CPT, link the relevant location to the page:
```bash
docker exec $CONTAINER wp --allow-root post meta update $PAGE_ID \
  _healthcare_location_id [LOCATION_CPT_ID] \
  --url=[SUBSITE_URL]
```

Check `lp_state.md` for location CPT IDs created during lp-subsite-setup.

## Step 7: Verify the Frontend

Open the page URL in a browser: `[SUBSITE_URL][SLUG]/`

Check these things visually:
1. All sections from the prototype are visible
2. Brand colours and typography match the prototype
3. No broken layout (sections aren't bleeding into each other)
4. Mobile view looks correct (check at 390px width)

**If layout is broken**: the most common cause is WordPress adding default block gap margins. Add the gap resets from Step 3 if not already present.

**If CSS is missing**: verify the custom.css file contains the prototype styles and the theme is enqueuing it.

## Step 8: Update State File

Update `/lp/lp_state.md`:
- Add the Post ID to the Pages Built table
- Update status to "HTML Live"

```markdown
| [Ad Group] | /lp/copy/[slug]-copy.md | /lp/prototype/[slug]/index.html | /lp/deploy/[slug]-content.html | ⏳ | [POST_ID] | HTML Live |
```

## Approval Gate

Use the `AskUserQuestion` tool:

> "The [AD GROUP] landing page is live at [PAGE_URL]. Check the frontend — does it match the prototype? Approved to convert to Gutenberg blocks?"

Options:
- "Looks good — run lp-deploy-2 to convert to blocks"
- "CSS issues — needs fixes first"
- "Leave as HTML for now, move on to remaining pages"

Do not run lp-deploy-2 without approval. If the user wants to check or fix the page first, note that it is still in HTML block form and the state is "HTML Live — awaiting block conversion".
