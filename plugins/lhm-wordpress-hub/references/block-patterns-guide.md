# Block Patterns Development Guide

Reference for creating WordPress block patterns — reusable arrangements of blocks that form page sections.

## What Block Patterns Are

Block patterns are pre-built combinations of Gutenberg blocks. They let you define page sections (hero banners, card grids, CTAs) as reusable building blocks that content editors can insert and customize.

## Pattern File Structure

Patterns live in `/patterns/` inside the theme. Each pattern is a PHP file with a header comment and block markup.

```
theme-name/
  /patterns/
    hero-banner.php
    card-grid.php
    cta-section.php
    testimonials.php
    features-grid.php
    stats-counter.php
    team-grid.php
    faq-accordion.php
    contact-form.php
    image-text-split.php
```

## Pattern File Format

```php
<?php
/**
 * Title: Hero Banner
 * Slug: theme-name/hero-banner
 * Categories: hero
 * Keywords: hero, banner, header, intro
 * Description: Full-width hero section with heading, subheading, and CTA button.
 * Viewport Width: 1400
 */
?>

<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|80","bottom":"var:preset|spacing|80","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"backgroundColor":"primary","textColor":"background","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull has-primary-background-color has-background-color has-text-color has-background">

  <!-- wp:heading {"textAlign":"center","level":1,"fontSize":"xx-large"} -->
  <h1 class="wp-block-heading has-text-align-center has-xx-large-font-size">Your Headline Here</h1>
  <!-- /wp:heading -->

  <!-- wp:paragraph {"align":"center","fontSize":"large"} -->
  <p class="has-text-align-center has-large-font-size">Supporting subheadline that expands on the value proposition.</p>
  <!-- /wp:paragraph -->

  <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
  <div class="wp-block-buttons">
    <!-- wp:button {"backgroundColor":"accent","textColor":"background"} -->
    <div class="wp-block-button"><a class="wp-block-button__link has-background-color has-accent-background-color has-text-color has-background wp-element-button">Get Started</a></div>
    <!-- /wp:button -->
  </div>
  <!-- /wp:buttons -->

</div>
<!-- /wp:group -->
```

## Common Patterns for Business Sites

### Hero Banner
Full-width section with heading, subheading, and CTA. Usually the first section on any page.

### Image + Text Split
Two-column layout with image on one side, text + CTA on the other. Alternating left/right per section.

### Card Grid
Grid of cards (services, features, team members). Typically 3 or 4 columns.

### Testimonials
Customer quotes with attribution. Can be grid, slider, or single featured quote.

### CTA Section
Call-to-action band. Strong heading, brief text, prominent button. Usually full-width with accent background.

### Stats/Counter
Row of numbers with labels (e.g. "500+ Clients", "10 Years Experience").

### FAQ Accordion
Question/answer pairs using the Details block (WP 6.3+).

### Contact Section
Contact information alongside a form placeholder or embed.

### Features Grid
Icon + heading + description in a grid. For service or feature showcases.

### Team Grid
Photos + names + roles in a responsive grid.

## Block Markup Reference

### Group (Section Wrapper)
```html
<!-- wp:group {"align":"full","backgroundColor":"background","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull has-background-color has-background">
  <!-- inner blocks -->
</div>
<!-- /wp:group -->
```

### Columns
```html
<!-- wp:columns {"align":"wide"} -->
<div class="wp-block-columns alignwide">
  <!-- wp:column {"width":"50%"} -->
  <div class="wp-block-column" style="flex-basis:50%">
    <!-- content -->
  </div>
  <!-- /wp:column -->
  <!-- wp:column {"width":"50%"} -->
  <div class="wp-block-column" style="flex-basis:50%">
    <!-- content -->
  </div>
  <!-- /wp:column -->
</div>
<!-- /wp:columns -->
```

### Heading
```html
<!-- wp:heading {"textAlign":"center","level":2,"fontSize":"x-large"} -->
<h2 class="wp-block-heading has-text-align-center has-x-large-font-size">Section Title</h2>
<!-- /wp:heading -->
```

### Paragraph
```html
<!-- wp:paragraph {"align":"center","fontSize":"medium"} -->
<p class="has-text-align-center has-medium-font-size">Body text here.</p>
<!-- /wp:paragraph -->
```

### Button
```html
<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
<div class="wp-block-buttons">
  <!-- wp:button {"backgroundColor":"primary"} -->
  <div class="wp-block-button"><a class="wp-block-button__link has-primary-background-color has-background wp-element-button" href="/contact">Contact Us</a></div>
  <!-- /wp:button -->
</div>
<!-- /wp:buttons -->
```

### Image
```html
<!-- wp:image {"align":"wide","sizeSlug":"full"} -->
<figure class="wp-block-image alignwide size-full"><img src="" alt="Description"/></figure>
<!-- /wp:image -->
```

### Cover (Background Image)
```html
<!-- wp:cover {"url":"image.jpg","dimRatio":60,"overlayColor":"primary","align":"full"} -->
<div class="wp-block-cover alignfull">
  <span class="wp-block-cover__background has-primary-background-color has-background-dim-60 has-background-dim"></span>
  <div class="wp-block-cover__inner-container">
    <!-- inner blocks -->
  </div>
</div>
<!-- /wp:cover -->
```

### Spacer
```html
<!-- wp:spacer {"height":"var:preset|spacing|60"} -->
<div style="height:var(--wp--preset--spacing--60)" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

## Registering Pattern Categories

In `functions.php`:

```php
function theme_register_pattern_categories() {
    register_block_pattern_category('hero', ['label' => 'Hero Sections']);
    register_block_pattern_category('cta', ['label' => 'Call to Action']);
    register_block_pattern_category('content', ['label' => 'Content Sections']);
    register_block_pattern_category('testimonials', ['label' => 'Testimonials']);
    register_block_pattern_category('team', ['label' => 'Team']);
    register_block_pattern_category('faq', ['label' => 'FAQ']);
}
add_action('init', 'theme_register_pattern_categories');
```

## Key Principles

1. **Use theme.json presets** — always reference `var:preset|color|primary` and `var:preset|spacing|50` instead of hardcoded values. This ensures patterns respect the design system.
2. **One pattern per section** — each pattern should represent one logical page section. Combine patterns to build pages.
3. **Meaningful defaults** — use placeholder text that reflects the pattern's intent (not "Lorem ipsum").
4. **Constrained layout** — wrap content in a Group with `"layout":{"type":"constrained"}` to respect content width.
5. **Full-width sections** — use `"align":"full"` on the outer Group for edge-to-edge sections, then constrain inner content.
6. **Prefer native blocks** — use core blocks before reaching for custom blocks. Cover, Group, Columns, and Buttons handle most layouts.
