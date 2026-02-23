# Blog Templates Reference

WordPress block theme templates for the blog listing page and single post view.

## Blog Listing Template (`home.html`)

WordPress uses `home.html` for the blog posts index when `show_on_front = page`.

```html
<!-- wp:template-part {"slug":"header","area":"header"} /-->

<!-- wp:html -->
<div class="blog-header section--dark">
  <div class="container container--narrow">
    <span class="overline overline--accent">Blog</span>
    <h1>Straight Talk for Trade Businesses</h1>
    <p class="text-muted-light">Google Ads, SEO, websites and lead generation — explained in plain English for tradies who want real answers.</p>
  </div>
</div>
<!-- /wp:html -->

<!-- wp:html -->
<div class="blog-listing section">
  <div class="container">
<!-- /wp:html -->

<!-- wp:query {"queryId":1,"query":{"perPage":12,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":true}} -->
<div class="wp-block-query">
  <!-- wp:post-template {"className":"blog-grid"} -->
    <!-- wp:group {"className":"blog-card","layout":{"type":"flex","orientation":"vertical"}} -->
    <div class="wp-block-group blog-card">
      <!-- wp:post-terms {"term":"category","className":"blog-card__category"} /-->
      <!-- wp:post-title {"level":3,"isLink":true,"className":"blog-card__title"} /-->
      <!-- wp:post-excerpt {"moreText":"","excerptLength":28,"className":"blog-card__excerpt"} /-->
      <!-- wp:group {"className":"blog-card__meta","layout":{"type":"flex","flexWrap":"nowrap"}} -->
      <div class="wp-block-group blog-card__meta">
        <!-- wp:post-date {"className":"blog-card__date"} /-->
      </div>
      <!-- /wp:group -->
    </div>
    <!-- /wp:group -->
  <!-- /wp:post-template -->

  <!-- wp:query-pagination {"className":"blog-pagination"} -->
  <div class="wp-block-query-pagination blog-pagination">
    <!-- wp:query-pagination-previous /-->
    <!-- wp:query-pagination-numbers /-->
    <!-- wp:query-pagination-next /-->
  </div>
  <!-- /wp:query-pagination -->

  <!-- wp:query-no-results -->
    <!-- wp:paragraph -->
    <p>No posts found. Check back soon for new content.</p>
    <!-- /wp:paragraph -->
  <!-- /wp:query-no-results -->
</div>
<!-- /wp:query -->

<!-- wp:html -->
  </div>
</div>
<!-- /wp:html -->

<!-- wp:template-part {"slug":"footer","area":"footer"} /-->
```

### Key blocks:
- `wp:query` with `"inherit":true` — WordPress auto-queries posts for the blog index
- `wp:post-template` with `{"className":"blog-grid"}` — renders each post as a card, CSS targets `.blog-grid` for the grid layout
- `wp:post-terms` — renders category links
- `wp:post-excerpt` with `{"excerptLength":28}` — controls word count on cards
- `wp:query-pagination` — prev/next/numbers navigation

## Single Post Template (`single.html`)

```html
<!-- wp:template-part {"slug":"header","area":"header"} /-->

<!-- wp:html -->
<article class="blog-single">
  <div class="blog-single__header section--dark">
    <div class="container container--narrow">
<!-- /wp:html -->

<!-- wp:post-terms {"term":"category","className":"blog-single__category"} /-->

<!-- wp:post-title {"level":1,"className":"blog-single__title"} /-->

<!-- wp:html -->
      <div class="blog-single__meta">
<!-- /wp:html -->

<!-- wp:post-date {"className":"blog-single__date"} /-->

<!-- wp:html -->
        <span class="blog-single__separator">·</span>
<!-- /wp:html -->

<!-- wp:post-author-name {"className":"blog-single__author"} /-->

<!-- wp:html -->
      </div>
    </div>
  </div>
  <div class="blog-single__body section">
    <div class="container container--narrow">
<!-- /wp:html -->

<!-- wp:post-content /-->

<!-- wp:html -->
    </div>
  </div>
</article>
<!-- /wp:html -->

<!-- wp:html -->
<div class="blog-cta section--dark">
  <div class="container container--narrow" style="text-align: center;">
    <span class="overline overline--accent">Ready to grow?</span>
    <h2>Get a Free Website Mockup</h2>
    <p style="color: rgba(255,255,255,0.85); margin-bottom: 2rem;">See what your trade business website would look like — built to rank on Google from day one. No cost, no obligation.</p>
    <a href="/contact" class="btn btn--primary">Get Your Free Mockup</a>
  </div>
</div>
<!-- /wp:html -->

<!-- wp:template-part {"slug":"footer","area":"footer"} /-->
```

### Template structure:
- **Dark header** (`section--dark`): category tag, H1 title, date + separator + author
- **White body** (`section`): `wp:post-content` renders the post HTML in a narrow container
- **CTA section** (`section--dark`): call-to-action with heading, description, and button

### Why wp:html blocks wrap the structure:
The single post template mixes native WP blocks (`wp:post-title`, `wp:post-date`, `wp:post-author-name`, `wp:post-content`, `wp:post-terms`) with custom HTML structure (`.blog-single__header`, `.blog-single__body`, `.blog-single__meta`). The `wp:html` blocks provide the structural wrappers while letting the native blocks handle dynamic content.

## Blog CSS Classes

These classes must exist in `custom.css` for the templates to render correctly:

### Listing page:
| Class | Purpose |
|-------|---------|
| `.blog-header` | Dark header section with padding accounting for fixed header + ribbon |
| `.blog-listing` | White section containing the post grid |
| `.blog-grid` | CSS grid, 2 columns on desktop, 1 on mobile |
| `.blog-card` | Individual card with border, padding, hover elevation |
| `.blog-card__category` | Uppercase category tag link |
| `.blog-card__title` | Post title, linked, with hover color change |
| `.blog-card__excerpt` | Muted excerpt text |
| `.blog-card__meta` | Bottom section with date, separated by top border |
| `.blog-card__date` | Small muted date text |
| `.blog-pagination` | Centered pagination with styled number links |

### Single post:
| Class | Purpose |
|-------|---------|
| `.blog-single__header` | Dark header with padding for fixed header + ribbon |
| `.blog-single__category` | Accent-colored category tag |
| `.blog-single__title` | White H1 title |
| `.blog-single__meta` | Flex row with date, separator, author name |
| `.blog-single__date` | Muted white date |
| `.blog-single__author` | Muted white author name |
| `.blog-single__separator` | Dot separator between date and author |
| `.blog-single__body` | White section containing post content |
| `.blog-single__body h2/h3/h4` | Prose heading styles with top margin for visual separation |
| `.blog-single__body p` | 1.8 line-height, 1.5rem bottom margin |
| `.blog-single__body table/th/td` | Styled data tables with hover rows |
| `.blog-single__body hr` | Subtle 1px divider with 3rem margin |
| `.blog-single__body blockquote` | Left-bordered, muted italic text |
| `.blog-cta` | Dark CTA section at the bottom of each post |
