# WP-CLI Reference for Site Building

Common WP-CLI commands used during the WordPress build phase. If using a WordPress MCP server, translate these to equivalent MCP tool calls.

## Core Setup

```bash
# Install WordPress
wp core download
wp config create --dbname=mydb --dbuser=root --dbpass=pass
wp core install --url=example.com --title="Site Name" --admin_user=admin --admin_email=admin@example.com --admin_password=securepass

# Update WordPress
wp core update
wp core update-db
```

## Theme Management

```bash
# Install and activate theme
wp theme install theme-slug --activate
wp theme activate theme-slug

# List themes
wp theme list

# Delete theme
wp theme delete theme-slug

# Scaffold a block theme (if using create-block-theme plugin)
wp scaffold theme theme-slug --theme_name="Theme Name"
```

## Plugin Management

```bash
# Install and activate
wp plugin install plugin-slug --activate

# Activate/deactivate
wp plugin activate plugin-slug
wp plugin deactivate plugin-slug

# List plugins
wp plugin list

# Update all
wp plugin update --all

# Delete plugin
wp plugin delete plugin-slug

# Recommended plugins for builds
wp plugin install wordpress-seo --activate           # Yoast SEO
wp plugin install redirection --activate              # Redirects
wp plugin install wp-fastest-cache --activate          # Caching
wp plugin install wordfence --activate                 # Security
wp plugin install contact-form-7 --activate            # Forms
wp plugin install google-site-kit --activate           # Analytics
```

## Pages & Content

```bash
# Create a page
wp post create --post_type=page --post_title="About Us" --post_status=publish --post_content="<content>"

# Create page from file
wp post create ./content/about.html --post_type=page --post_title="About Us" --post_status=publish

# Update page content
wp post update <page_id> --post_content="<new content>"
wp post update <page_id> ./content/about.html

# Set page as homepage
wp option update show_on_front page
wp option update page_on_front <page_id>

# Set blog page
wp option update page_for_posts <page_id>

# List pages
wp post list --post_type=page --fields=ID,post_title,post_status

# Delete a page
wp post delete <page_id>

# Update page meta
wp post meta update <page_id> _wp_page_template "templates/landing-page.html"
```

## Bypassing kses Sanitisation (Iframes / Embeds)

`wp_update_post()` and `wp post update` run content through kses which strips `<iframe>`, `<script>`, and other "unsafe" tags. When you need to insert Google Maps embeds, video iframes, or other HTML into `<!-- wp:html -->` blocks, use a PHP script with `$wpdb->update()` instead:

```php
<?php
// Bootstrap WordPress
define('ABSPATH', '/var/www/html/');
require_once ABSPATH . 'wp-load.php';
switch_to_blog($blog_id); // multisite only
global $wpdb;

$iframe = '<iframe class="location-map" src="https://www.google.com/maps/embed?pb=..." allowfullscreen="" loading="lazy"></iframe>';

// Replace empty wp:html placeholder
$post = get_post($page_id);
$content = str_replace(
    "<!-- wp:html -->\n\n<!-- /wp:html -->",
    "<!-- wp:html -->\n{$iframe}\n<!-- /wp:html -->",
    $post->post_content
);

// Direct DB update bypasses kses
$wpdb->update(
    $wpdb->posts,
    array('post_content' => $content),
    array('ID' => $page_id),
    array('%s'),
    array('%d')
);
clean_post_cache($page_id);
```

## Menus

```bash
# Create menu
wp menu create "Primary Navigation"
wp menu create "Footer Navigation"

# Add page to menu
wp menu item add-post primary-navigation <page_id>

# Add custom link
wp menu item add-custom primary-navigation "Contact" "https://example.com/contact"

# Assign menu to location
wp menu location assign primary-navigation primary

# List menu items
wp menu item list primary-navigation
```

## Media

```bash
# Import image
wp media import ./assets/logo.png --title="Site Logo"

# Import all images from folder
wp media import ./assets/images/*

# Set featured image
wp post meta update <post_id> _thumbnail_id <attachment_id>
```

## Site Options

```bash
# Site identity
wp option update blogname "Site Name"
wp option update blogdescription "Site tagline"

# Permalinks
wp rewrite structure '/%postname%/'
wp rewrite flush

# Timezone
wp option update timezone_string "Australia/Sydney"

# Date format
wp option update date_format "j F Y"

# Disable comments globally
wp option update default_comment_status closed
wp option update default_ping_status closed
```

## Users

```bash
# Create user
wp user create editor editor@example.com --role=editor --user_pass=securepass

# Update user role
wp user set-role <user_id> editor

# List users
wp user list --fields=ID,user_login,user_email,roles
```

## Search & Replace

```bash
# Update URLs (e.g., staging to production)
wp search-replace 'staging.example.com' 'example.com' --all-tables --precise

# Dry run first
wp search-replace 'old-text' 'new-text' --all-tables --dry-run
```

## Database

```bash
# Export database
wp db export backup.sql

# Import database
wp db import backup.sql

# Optimize
wp db optimize

# Run query
wp db query "SELECT ID, post_title FROM wp_posts WHERE post_type='page'"
```

## Cache & Transients

```bash
# Flush cache
wp cache flush

# Delete transients
wp transient delete --all
wp transient delete --expired
```

## Cron

```bash
# List scheduled events
wp cron event list

# Run all due events
wp cron event run --due-now

# Test cron
wp cron test
```

## Widget & Sidebar (Classic)

```bash
# List widgets
wp widget list sidebar-1

# These are mostly replaced by template parts in block themes
```

## Block Theme Specific

```bash
# Export block theme customizations
# Requires the Create Block Theme plugin
wp create-block-theme export

# List registered block patterns
wp eval "print_r(WP_Block_Patterns_Registry::get_instance()->get_all_registered());"

# List registered template parts
wp eval "print_r(get_block_templates(array(), 'wp_template_part'));"
```

## Maintenance & Debugging

```bash
# Enable/disable maintenance mode
wp maintenance-mode activate
wp maintenance-mode deactivate

# Check site health
wp site health

# Debug: show PHP version and extensions
wp cli info
wp eval "phpinfo();"

# Generate salts
wp config shuffle-salts
```

## Useful Pipelines

```bash
# Create all pages from a list
for page in "Home" "About" "Services" "Contact"; do
  wp post create --post_type=page --post_title="$page" --post_status=publish
done

# Delete all draft pages
wp post delete $(wp post list --post_type=page --post_status=draft --format=ids)

# Export list of page IDs and titles
wp post list --post_type=page --fields=ID,post_title --format=csv > pages.csv
```
