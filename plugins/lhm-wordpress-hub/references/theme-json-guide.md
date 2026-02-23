# theme.json Configuration Guide (WP 6.9+)

Reference for building custom block themes with `theme.json`. This is the primary configuration file for WordPress block themes — it controls typography, colors, spacing, layout, and block-level styles.

## Minimal Starter

```json
{
  "$schema": "https://schemas.wp.org/wp/6.9/theme.json",
  "version": 3,
  "settings": {
    "appearanceTools": true,
    "layout": {
      "contentSize": "800px",
      "wideSize": "1200px"
    },
    "color": {
      "palette": [],
      "gradients": [],
      "defaultPalette": false,
      "defaultGradients": false
    },
    "typography": {
      "fontFamilies": [],
      "fontSizes": [],
      "fluid": true,
      "defaultFontSizes": false
    },
    "spacing": {
      "spacingSizes": [],
      "units": ["px", "rem", "%", "vw"]
    }
  },
  "styles": {},
  "templateParts": [],
  "customTemplates": []
}
```

## Color Palette

Define the brand palette. WordPress generates CSS custom properties automatically.

```json
"color": {
  "palette": [
    { "slug": "primary", "color": "#1a365d", "name": "Primary" },
    { "slug": "secondary", "color": "#2b6cb0", "name": "Secondary" },
    { "slug": "accent", "color": "#ed8936", "name": "Accent" },
    { "slug": "background", "color": "#ffffff", "name": "Background" },
    { "slug": "foreground", "color": "#1a202c", "name": "Foreground" },
    { "slug": "muted", "color": "#718096", "name": "Muted" }
  ],
  "defaultPalette": false,
  "defaultGradients": false
}
```

Generated CSS: `var(--wp--preset--color--primary)`, etc.

## Typography

Use fluid typography for responsive scaling without media queries.

```json
"typography": {
  "fluid": true,
  "fontFamilies": [
    {
      "fontFamily": "'Inter', sans-serif",
      "slug": "body",
      "name": "Body",
      "fontFace": [
        {
          "fontFamily": "Inter",
          "fontWeight": "400 700",
          "fontStyle": "normal",
          "fontDisplay": "swap",
          "src": ["file:./assets/fonts/inter-variable.woff2"]
        }
      ]
    },
    {
      "fontFamily": "'Playfair Display', serif",
      "slug": "heading",
      "name": "Heading"
    }
  ],
  "fontSizes": [
    { "slug": "small", "size": "0.875rem", "name": "Small", "fluid": { "min": "0.875rem", "max": "1rem" } },
    { "slug": "medium", "size": "1rem", "name": "Medium", "fluid": { "min": "1rem", "max": "1.125rem" } },
    { "slug": "large", "size": "1.5rem", "name": "Large", "fluid": { "min": "1.25rem", "max": "1.5rem" } },
    { "slug": "x-large", "size": "2.25rem", "name": "X-Large", "fluid": { "min": "1.75rem", "max": "2.25rem" } },
    { "slug": "xx-large", "size": "3rem", "name": "XX-Large", "fluid": { "min": "2.25rem", "max": "3rem" } }
  ],
  "defaultFontSizes": false
}
```

## Spacing Scale

Define a spacing scale that maps to CSS custom properties.

```json
"spacing": {
  "spacingSizes": [
    { "slug": "10", "size": "0.25rem", "name": "1" },
    { "slug": "20", "size": "0.5rem", "name": "2" },
    { "slug": "30", "size": "1rem", "name": "3" },
    { "slug": "40", "size": "1.5rem", "name": "4" },
    { "slug": "50", "size": "2rem", "name": "5" },
    { "slug": "60", "size": "3rem", "name": "6" },
    { "slug": "70", "size": "5rem", "name": "7" },
    { "slug": "80", "size": "8rem", "name": "8" }
  ],
  "units": ["px", "rem", "%", "vw"]
}
```

Generated CSS: `var(--wp--preset--spacing--30)`, etc.

## Global Styles

Apply defaults to the entire site.

```json
"styles": {
  "color": {
    "background": "var(--wp--preset--color--background)",
    "text": "var(--wp--preset--color--foreground)"
  },
  "typography": {
    "fontFamily": "var(--wp--preset--font-family--body)",
    "fontSize": "var(--wp--preset--font-size--medium)",
    "lineHeight": "1.6"
  },
  "spacing": {
    "blockGap": "var(--wp--preset--spacing--40)"
  },
  "elements": {
    "heading": {
      "typography": {
        "fontFamily": "var(--wp--preset--font-family--heading)",
        "fontWeight": "700",
        "lineHeight": "1.2"
      }
    },
    "link": {
      "color": {
        "text": "var(--wp--preset--color--primary)"
      },
      ":hover": {
        "color": {
          "text": "var(--wp--preset--color--secondary)"
        }
      }
    },
    "button": {
      "color": {
        "background": "var(--wp--preset--color--primary)",
        "text": "var(--wp--preset--color--background)"
      },
      "border": {
        "radius": "4px"
      },
      "typography": {
        "fontWeight": "600"
      }
    }
  }
}
```

## Block-Level Styles

Override styles for specific blocks.

```json
"styles": {
  "blocks": {
    "core/group": {
      "spacing": {
        "padding": {
          "top": "var(--wp--preset--spacing--50)",
          "bottom": "var(--wp--preset--spacing--50)",
          "left": "var(--wp--preset--spacing--40)",
          "right": "var(--wp--preset--spacing--40)"
        }
      }
    },
    "core/separator": {
      "color": {
        "text": "var(--wp--preset--color--muted)"
      },
      "border": {
        "width": "1px"
      }
    }
  }
}
```

## Template Parts & Custom Templates

Register template parts (header, footer, sidebar) and custom templates.

```json
"templateParts": [
  { "name": "header", "title": "Header", "area": "header" },
  { "name": "footer", "title": "Footer", "area": "footer" },
  { "name": "sidebar", "title": "Sidebar", "area": "uncategorized" }
],
"customTemplates": [
  { "name": "blank", "title": "Blank", "postTypes": ["page", "post"] },
  { "name": "landing-page", "title": "Landing Page", "postTypes": ["page"] },
  { "name": "full-width", "title": "Full Width", "postTypes": ["page", "post"] }
]
```

## File Structure for Block Theme

```
theme-name/
  style.css              # Theme header comment (required)
  theme.json             # Global settings and styles
  functions.php          # Enqueue scripts, register patterns
  /templates/
    index.html           # Fallback template (required)
    home.html            # Homepage
    page.html            # Default page
    single.html          # Single post
    archive.html         # Archive/listing
    404.html             # 404 page
    search.html          # Search results
  /parts/
    header.html          # Header template part
    footer.html          # Footer template part
  /patterns/
    hero-banner.php      # Reusable block patterns
    card-grid.php
    cta-section.php
    testimonials.php
  /styles/
    dark.json            # Style variations
    minimal.json
  /assets/
    /fonts/              # Self-hosted fonts
    /images/             # Theme images
```

## Key Principles

1. **No custom CSS if theme.json can do it** — use theme.json settings and styles first. Only add CSS for things theme.json can't express.
2. **Fluid typography** — always enable `"fluid": true` for responsive text without media queries.
3. **Design tokens as presets** — define colors, font sizes, and spacing as presets. Reference them with `var(--wp--preset--...)` throughout.
4. **Disable defaults** — set `defaultPalette`, `defaultGradients`, and `defaultFontSizes` to false to keep the editor clean.
5. **Self-host fonts** — use `fontFace` to serve fonts from the theme for performance and privacy.
