---
name: lp-deploy-2
description: "Convert a landing page from raw Gutenberg HTML blocks to native WordPress blocks for full editor editability. Use this when the user says 'convert to blocks', 'convert to Gutenberg', 'lp-deploy-2', 'make the landing page editable', 'convert the HTML blocks', or 'Gutenberg conversion'. Requires lp-deploy-1 to have run successfully. Produces a native block version of the page that works in the Gutenberg editor."
---

# LP Deploy 2 -- Convert HTML to Native Gutenberg Blocks

Take the raw HTML prototype (currently sitting in `wp:html` blocks) and convert it section by section to native WordPress blocks. The visual frontend should not change. Only the editor experience improves.

The golden rule: **the frontend proven in deploy-1 is the reference. Every converted section must match it.**

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-deploy-2/LEARNED.md`
2. Read `lp/lp_state.md` -- confirm the target page has status "HTML Live" and has a Post ID
3. **Read the conversion patterns reference** -- `${CLAUDE_PLUGIN_ROOT}/references/gutenberg-conversion-patterns.md`. This is the single source of truth for block markup. Every section you convert MUST follow these patterns exactly.
4. **Prefer the client's `wp/wp-cli.sh` helper** over raw `docker exec` commands. It auto-installs WP-CLI and passes the correct `--url` flag. The theme CSS file is `assets/css/custom-components.css` (not `custom.css`) for the healthcare-theme. Theme files can be edited directly via the client's `wp/healthcare-theme` symlink.
5. Get the current page content:

```bash
docker exec $CONTAINER wp --allow-root post get [POST_ID] \
  --field=post_content \
  --url=[SUBSITE_URL]
```

Save the current content as `/lp/deploy/[SLUG]-content.html` (this is your fallback if something goes wrong).

## Step 1: Section Inventory (Mandatory)

Before converting anything, create a complete inventory of every section on the page. This prevents the "half converted" problem where some sections get done and others are missed.

1. Read the current page content (the `wp:html` blocks from deploy-1)
2. List every section by its class name, in order from top to bottom
3. For each section, decide: **convert to native blocks** or **keep as wp:html**
4. Present the inventory to the user for approval before starting

Example inventory format:

```
Section Inventory for [PAGE NAME]:
1. .hero-section -- CONVERT (wp:cover or wp:group with align:full)
2. .trust-bar -- CONVERT (wp:group with grid layout)
3. .pain-points-section -- CONVERT (wp:group with heading + paragraphs)
4. .features-section -- CONVERT (wp:group with grid layout)
5. .testimonials-section -- CONVERT (wp:quote blocks)
6. .process-section -- CONVERT (wp:group with grid layout)
7. .faq-section -- KEEP AS HTML (JS-driven accordion with single-open behaviour)
8. .locations-section -- KEEP AS HTML (dynamic CPT data)
9. .cta-section -- CONVERT (wp:group with align:full)

Total: 9 sections. 7 will be converted, 2 kept as HTML.
```

**Do not start converting until the user approves the inventory.**

### Keep as `wp:html` only if:

- The section uses JavaScript that can't be replicated natively (complex animations, single-open accordion)
- It relies on dynamic CPT data (locations grid with PHP shortcodes)
- Converting it would change the visual output and you can't resolve the discrepancy
- JS-driven FAQ accordion using `<button>` pattern with `.is-open` class toggling (converting to `wp:details` would lose single-open-at-a-time behaviour from frontend.js)
- Hero sections with CSS grid (`hero__grid`), trust strip `<span>` elements, and custom button classes have too many inline elements with no native block equivalent
- Announcement bar with inline `<span>` elements and pipe dividers (no native block equivalent)

**Nesting `wp:html` inside `wp:group` is fine.** The HTML block renders correctly and the parent group remains editable in Gutenberg.

If keeping a section as `wp:html`, document why in `lp_state.md`.

## Step 2: Convert Sections (One at a Time)

Work through the inventory in order, converting one section at a time. After each section, push and visually verify before moving on.

### The Mandatory Full-Width Pattern

Every section MUST use this nesting structure. This is the #1 reason conversions fail (pages appear ~600px wide in the editor instead of full-width):

```html
<!-- wp:group {"className":"section-name","align":"full","layout":{"type":"default"}} -->
<div class="wp-block-group alignfull section-name">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">

  <!-- inner content blocks here -->

</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

Critical requirements:
- `"align":"full"` in the JSON AND `alignfull` on the rendered div -- both are required
- Inner `container` group for centred content with max-width
- `"layout":{"type":"default"}` to prevent WP from injecting layout classes that conflict with prototype CSS

### Section-to-Block Mapping

Refer to `${CLAUDE_PLUGIN_ROOT}/references/gutenberg-conversion-patterns.md` for the exact markup of each pattern. The patterns file has copy-paste-ready examples for every section type.

| Section class | Block approach | Pattern to use |
|---|---|---|
| `.site-header` | Skip (template part) | N/A |
| `.hero-section` (with background image/video) | `wp:cover` with inner blocks | Hero with Video Background |
| `.hero-section` (colour only) | `wp:group` with align:full | Hero with Background Colour |
| `.trust-bar` | `wp:group` > grid > stat items | Trust Bar |
| `.pain-points-section` | `wp:group` > container > heading + paragraphs | Content Section (Narrow) |
| `.solution-section` | `wp:group` > container > heading + paragraphs | Content Section (Narrow) |
| `.features-section` | `wp:group` > container > grid with feature cards | Features Grid |
| `.services-section` | `wp:group` > container > grid with service cards | Card Grid |
| `.testimonials-section` | `wp:group` > container > grid with `wp:quote` | Card Grid (with quote blocks) |
| `.process-section` | `wp:group` > container > grid with step items | Process/Steps |
| `.results-section` | `wp:group` > container > metrics grid | Results/Case Study |
| `.industry-section` | `wp:group` > container > grid with industry cards | Industry Grid |
| `.fit-section` | `wp:group` > container > 2-column grid | Good Fit / Bad Fit |
| `.faq-section` | `wp:group` > container > `wp:details` blocks | FAQ (if no JS accordion) |
| `.cta-section` | `wp:group` > container > heading + list + buttons | CTA Section |
| `.locations-section` | Keep as `wp:html` (dynamic CPT data) | N/A |
| `.site-footer` | Skip (template part) | N/A |

### Conversion Rules

**Use exact prototype class names.** The CSS was extracted from the prototype. If the prototype has `.hero-section`, the block must have `className: "hero-section"`. WordPress adds its own classes alongside yours. They stack, they don't conflict.

**JSON attributes must match rendered HTML.** The Gutenberg block validator compares JSON against HTML. Mismatches cause "This block contains unexpected content" errors.

**Do NOT use WP layout attributes when prototype CSS handles responsive grid/flex.** If the prototype CSS already defines `display: grid` or `display: flex` with `@media` queries for responsive breakpoints, do NOT add WP layout attributes (`layout: {type: "grid"}`). WP grid layout ignores `@media` queries and breaks responsive breakpoints. Use `wp:group` with `className` only and let the prototype CSS handle the layout.

**CSS specificity: prototype CSS always wins over WP defaults.** WP `is-layout-flow` margin rules use `:where()` selectors (0 specificity). Any prototype CSS with class or element selectors wins automatically without `!important`.

**Reveal animation limitations.** `data-delay` attributes for staggered IntersectionObserver reveal animations can't be added to native blocks. Accept simultaneous fade-in as a trade-off for editor editability.

**Buttons: use `wp:buttons` wrapper.** Don't use raw `<a>` tags. Exception: if prototype CSS targets bare `.btn` on `<a>` tags and the `wp:button` wrapper breaks styling, keep the button group as `wp:html` nested inside the otherwise-native section.

**Lists: use `wp:list` + `wp:list-item`.** Every `<ul>` or `<ol>` in the prototype gets converted to native list blocks.

**Inline SVG icons: use emoji or wp:image.** Inline SVG in `wp:html` blocks is invisible in the editor.

### Push and Verify After Each Section

After converting a section, save the full page markup to `/lp/deploy/[SLUG]-content-blocks.html` and push:

```bash
docker cp lp/deploy/[SLUG]-content-blocks.html $CONTAINER:/tmp/[SLUG]-content-blocks.html

docker exec $CONTAINER wp --allow-root post update [POST_ID] \
  --post_content="$(docker exec $CONTAINER cat /tmp/[SLUG]-content-blocks.html)" \
  --url=[SUBSITE_URL]
```

Check the frontend after each section push. If a section looks wrong after conversion, the issue is in the block structure (not the CSS, because deploy-1 proved the CSS works). Fix block structure and re-push before moving on.

## kses and Content Placement Warnings

### kses Strips Iframes
`wp_update_post()` runs content through kses sanitisation which strips `<iframe>` tags (Google Maps embeds, videos). Use `$wpdb->update()` on the posts table directly + `clean_post_cache($pid)` to bypass. See `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for the full pattern.

### Content Placement in Gutenberg Blocks
When inserting content into `wp:group` blocks via regex or string replacement, the new content must go BEFORE the closing `</div>`, not between `</div>` and `<!-- /wp:group -->`. The `</div>` closes the rendered DOM element. Anything placed after it but before the block comment renders outside the component in the DOM.

### Link Colour in Dark Sections
"Learn more" links and other `::after` arrow pseudo-elements need explicit `color: var(--healthcare-primary)` (or the appropriate brand colour). Colour inheritance can fail when the parent `<p>` gets overridden by block editor paragraph styles.

## Step 3: Editor QA

After ALL sections in the inventory are converted (or explicitly kept as HTML), verify the editor experience. This is not optional.

Open the block editor and check every item:

1. **Every section has visible, editable content** -- no blank white space, no raw code
2. **Sections span full width** -- not constrained to ~600px in the editor. If narrow, you're missing `align:full`
3. **Multi-column layouts show columns** -- not stacked single-column blocks
4. **All text (headings, paragraphs, CTAs) is editable inline**
5. **Icons are visible** (emoji or images, not blank SVG placeholders)
6. **No unexplained `wp:html` blocks** except the ones documented in your inventory

### Editor Width Fix

If sections appear narrow in the editor (~600px instead of full-width):

1. Check every outer section group has `"align":"full"` in JSON AND `alignfull` on the div
2. Check theme.json has `useRootPaddingAwareAlignments: true`
3. Check editor.css has: `.editor-styles-wrapper .alignfull { max-width: none; }`
4. Check theme.json `styles.spacing.blockGap` is `"0"` (prevents white strips between sections)

## Step 4: Completion Checklist

Before declaring done, verify against the original inventory:

```
Conversion Complete:
[ ] All sections from inventory are accounted for
[ ] Converted sections: [list with status]
[ ] HTML-kept sections: [list with reasons]
[ ] Frontend matches deploy-1 baseline at desktop and mobile
[ ] Editor shows full-width sections (not constrained to contentSize)
[ ] All text is editable in block editor
[ ] No "This block contains unexpected content" errors
[ ] Content saved to /lp/deploy/[SLUG]-content-blocks.html
```

Tell the user the results:
> "Editor QA: [N] sections converted to native blocks. [SECTION] kept as HTML because [REASON]. Full editor editability confirmed."

## Update State File

Update `/lp/lp_state.md`:
- Change page status to "Blocks Live"
- Note any sections kept as `wp:html` with reasons

```markdown
| [Ad Group] | ... | /lp/deploy/[slug]-content-blocks.html | [POST_ID] | Blocks Live |
```

## Handoff

Tell the user:

> "Page is now fully editable in Gutenberg at [SUBSITE_URL]wp-admin/post.php?post=[POST_ID]&action=edit
>
> Run **lp-deploy-3** to build the remaining landing pages."
