---
name: wp-blog-publisher
description: "Publish blog posts to a WordPress site from markdown files via WP-CLI over SSH. Use this when the user says 'publish blog posts', 'upload blog posts', 'schedule blog posts', 'push posts to WordPress', 'publish articles', or 'post to the blog'. Handles markdown-to-HTML conversion, category creation, author assignment, scheduling, and Yoast SEO meta. Requires SSH access and WP-CLI on the server."
---

# WP Blog Publisher

Publishes markdown blog posts to a live WordPress site via WP-CLI over SSH. Converts markdown to HTML, creates categories, assigns authors, sets SEO meta fields, and schedules posts at natural-looking times.

## When to Use This Skill

- Publishing one or more blog posts from markdown files to WordPress
- Scheduling a batch of posts at staggered intervals
- Creating blog categories and tagging posts
- Setting up the blog listing page for the first time

## Before Starting

1. **Read SSH connection details** from the project's `wp/ssh.md` file
2. **Verify SSH connectivity** with a test command
3. **Read blog post files** from the specified directory
4. **Check existing posts** with `wp post list --post_type=post`
5. **Check existing categories** with `wp term list category`
6. **Check existing users** with `wp user list` to find the correct author ID
7. **Read WP state** from `wp/wp_state.md` to understand the current site setup

## Blog Post Markdown Format

Posts should be markdown files with YAML frontmatter:

```markdown
---
seo_title: "Your SEO Title Here (Under 60 Characters)"
meta_description: "Meta description for search results, 150-160 characters."
slug: /blog/your-post-slug
primary_keyword: main keyword
secondary_keywords: keyword two, keyword three, keyword four
status: draft
---

# Post Title (H1)

Post content in markdown...
```

### Required frontmatter fields:
- `seo_title` — used for Yoast SEO title and as the WordPress post title
- `meta_description` — set as Yoast `_yoast_wpseo_metadesc`
- `slug` — the URL slug (the last segment after `/blog/` is used as `post_name`)
- `primary_keyword` — for reference during publishing
- `status` — `draft` in the file; actual publish status is set during the upload step

### Optional fields:
- `secondary_keywords` — for reference
- `featured_image` — path to featured image if applicable

## Step 1: Plan the Schedule

If publishing multiple posts, ask the user for their scheduling preference:

```
How should these posts be scheduled?
- "Publish all now"
- "Stagger over time" (recommended for SEO — posts at intervals look more natural)
- "Specific dates" (user provides dates)
```

### Staggered Scheduling Rules

When staggering posts:
- Space posts 2-4 weeks apart (3 weeks is a good default)
- Use varied, natural-looking times (not all at 9:00 AM)
- Good time range: 7:00 AM to 5:00 PM in the site's timezone
- Vary between morning, midday, and afternoon
- Avoid round numbers (use 10:23, not 10:00)
- The first post publishes immediately; subsequent posts are scheduled as `future` status

Example schedule for 4 posts, 3 weeks apart:
| Post | Status | Date | Time |
|------|--------|------|------|
| 1 | publish | Now | Now |
| 2 | future | +3 weeks | 10:23 AM |
| 3 | future | +6 weeks | 14:47 PM |
| 4 | future | +9 weeks | 08:12 AM |

## Step 2: Convert Markdown to HTML

Use Python with the `markdown` library to convert post content to HTML:

```python
import markdown
import re

def parse_frontmatter(content):
    """Extract YAML frontmatter and body from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    body = match.group(2)
    meta = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key not in meta:  # keep first occurrence for duplicate keys
                meta[key] = val
    return meta, body

def md_to_html(md_text):
    """Convert markdown to HTML, removing the H1 (used as post_title)."""
    md_text = re.sub(r'^#\s+.+\n', '', md_text, count=1)
    md_text = md_text.strip()
    html = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code'],
        output_format='html5'
    )
    return html
```

### Important notes:
- Strip the first H1 heading from the body. WordPress uses `post_title` for the H1, so including it in the content creates a duplicate
- Use the `tables` extension for any posts with comparison tables
- Use `fenced_code` if posts contain code blocks
- Do NOT use the `nl2br` extension — it converts single newlines to `<br>` which breaks paragraph spacing

## Step 3: Upload to WordPress via WP-CLI

### Shell Quoting Problem

**Critical:** Post titles with apostrophes, parentheses, or special characters will break shell quoting when passed inline to `wp post create`. Do NOT pass titles as inline arguments.

**Solution:** Use temp files on the server for title, content, and meta description, then reference them via `$(cat /tmp/file.txt)` in the WP-CLI command. Upload using `scp`, not heredocs.

```bash
#!/bin/bash
cd /path/to/wordpress

# Read title and content from temp files (uploaded via scp)
POST_ID=$(wp post create /tmp/wp_post_content.html \
  --post_title="$(cat /tmp/wp_post_title.txt)" \
  --post_name="the-post-slug" \
  --post_status="publish" \
  --post_type="post" \
  --post_author=2 \
  --porcelain)

# Set Yoast SEO meta
wp post meta update $POST_ID _yoast_wpseo_metadesc "$(cat /tmp/wp_post_metadesc.txt)"
wp post meta update $POST_ID _yoast_wpseo_title "$(cat /tmp/wp_post_title.txt)"

# Clean up
rm -f /tmp/wp_post_content.html /tmp/wp_post_title.txt /tmp/wp_post_metadesc.txt
```

### For scheduled posts:

Add `--post_date="2026-03-17 10:23:00"` and use `--post_status="future"`. The date should be in the site's local timezone (check with `wp option get timezone_string`).

### Workflow per post:

1. Parse frontmatter and extract title, slug, meta description
2. Convert markdown body to HTML
3. Write HTML content, title, and meta description to local temp files
4. `scp` the temp files to the server's `/tmp/`
5. `scp` a shell script that runs the WP-CLI commands
6. Execute the shell script via SSH
7. Verify the post was created with `wp post list`

## Step 4: Create Categories

Map posts to service-related categories based on their content:

```bash
# Create categories
GOOGLE_ADS_ID=$(wp term create category "Google Ads" \
  --slug=google-ads \
  --description="Google Ads tips and guides for trade businesses" \
  --porcelain)

SEO_ID=$(wp term create category "SEO" \
  --slug=seo \
  --description="Search engine optimisation for trade businesses" \
  --porcelain)

WEBSITES_ID=$(wp term create category "Websites" \
  --slug=websites \
  --description="Tradie website design, costs and best practices" \
  --porcelain)
```

### Assigning categories to posts:

```bash
wp post update <post_id> --post_category=$CAT_ID_1,$CAT_ID_2
```

Posts can have multiple categories. Assign based on the post's primary and secondary topic. Remove the default "Uncategorized" category by assigning specific categories.

## Step 5: Set Author

Assign the correct author to all posts:

```bash
# Find the author ID
wp user list --fields=ID,user_login,display_name

# Update author on post
wp post update <post_id> --post_author=<user_id>

# Update display name if needed
wp user meta update <user_id> first_name "First"
wp user meta update <user_id> last_name "Last"
wp user update <user_id> --display_name="First Last"
```

## Step 6: Verify Blog Infrastructure

If this is the first time publishing blog posts, check that the blog listing page exists:

### Blog page setup:

```bash
# Check if a blog page exists
wp option get page_for_posts

# If 0 (not set), create the blog page
BLOG_PAGE_ID=$(wp post create --post_type=page \
  --post_title="Blog" \
  --post_name="blog" \
  --post_status="publish" \
  --porcelain)

# Set as the posts page
wp option update page_for_posts "$BLOG_PAGE_ID"
```

### Template requirements:

The blog listing requires a `home.html` template in the block theme (WordPress uses `home.html` for the blog posts index when a static front page is set). If `home.html` is currently used for the homepage:

1. Copy `home.html` to `front-page.html` (preserves homepage rendering)
2. Replace `home.html` with the blog listing template
3. Deploy both templates to the server

See the blog listing template reference in `references/blog-templates.md`.

### CSS injection order:

When adding blog CSS to `custom.css`, inject it before the RESPONSIVE section. Add blog-specific responsive rules as separate media queries at the end. This keeps the main responsive section clean.

After adding blog CSS, bump the theme version in `style.css` to bust browser caches. The theme's `functions.php` uses `wp_get_theme()->get('Version')` as the version parameter for enqueued stylesheets.

### CSS requirements:

Blog-specific CSS classes needed in `custom.css`:
- `.blog-header` — dark header section for the blog listing page
- `.blog-grid` — CSS grid for post cards (2 columns, 1 on mobile)
- `.blog-card` — individual post card with border, padding, hover shadow
- `.blog-card__category`, `.blog-card__title`, `.blog-card__excerpt`, `.blog-card__date`
- `.blog-single__header` — dark header for single posts
- `.blog-single__title`, `.blog-single__meta`, `.blog-single__body`
- `.blog-single__body h2/h3/h4/p/ul/ol/hr/table/blockquote` — prose typography
- `.blog-cta` — CTA section at the bottom of single posts

## Step 7: Post-Publish Verification

After all posts are uploaded:

```bash
# List all posts with status and dates
wp post list --post_type=post \
  --fields=ID,post_title,post_status,post_date,post_author \
  --format=table

# Verify categories assigned
for id in <post_ids>; do
  echo -n "Post $id: "
  wp post term list $id category --fields=name --format=csv | tail -n +2
done

# Flush caches
wp cache flush
wp rewrite flush
```

Then verify visually:
1. Check the blog listing page renders with post cards
2. Click through to a published single post
3. Verify the header shows: category tag, title, date, author name
4. Verify the body content renders with proper typography
5. Check that internal links work

## Validation Checkpoints

- [ ] All markdown files parsed without errors
- [ ] H1 removed from content (no duplicate title)
- [ ] Post titles display correctly (no truncation from quoting issues)
- [ ] Slugs match the frontmatter `slug` field
- [ ] Published post is live and accessible
- [ ] Scheduled posts show `future` status with correct dates
- [ ] Categories created and assigned to all posts
- [ ] Author set to the correct user on all posts
- [ ] Yoast SEO title and meta description set on all posts
- [ ] Blog listing page shows post cards (not full post content)
- [ ] Single post template renders with styled header and body

## Related Skills

- **seo-content-writer** (lhm-marketing-hub) — write the blog post content
- **wp-page-builder** — build WordPress pages (not blog posts)
- **content-refresher** (lhm-marketing-hub) — identify posts that need updating
