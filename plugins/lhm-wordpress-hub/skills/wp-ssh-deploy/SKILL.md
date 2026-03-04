---
name: wp-ssh-deploy
description: "Push a local WordPress site to a remote server via SSH and WP-CLI. Use this when the user says 'deploy to server', 'push to production', 'sync to live', 'upload site via SSH', 'deploy via SSH', 'push WordPress to server', or 'wp-ssh-deploy'. Handles theme files, pages, custom post types with meta, media, customizer settings, menus, and options. Requires SSH access to a server with WP-CLI installed."
---

# WP SSH Deploy

Push a local WordPress installation (Docker or native) to a remote server via SSH. Transfers theme files, pages, custom post types with meta, media uploads, customizer settings (theme_mods), and site options.

## When to Use This Skill

- Deploying a locally-built WordPress site to a live server
- Syncing local changes (theme, content, settings) to production
- Migrating a Docker-based WordPress install to cPanel or VPS hosting
- Pushing updates to a remote WordPress multisite subsite

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/wp-ssh-deploy/LEARNED.md` -- apply any relevant entries
2. Read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for WP-CLI patterns
3. Gather SSH connection details (see Step 1)
4. Confirm the local WordPress source (Docker container, native install, or WP-CLI path)

## Step 1: Gather SSH Connection Details

The skill needs these connection details. They can come from:
- A project-level SSH access file (e.g. `ssh.md`, `SSH Access.md`)
- User input via `AskUserQuestion`
- A state file from a previous deployment

Required details:
- **SSH command**: e.g. `ssh -i ~/.ssh/keyfile user@host`
- **Remote WP path**: the WordPress install directory on the server (e.g. `~/public_html/` or `~/subdomain.example.com/`)
- **Remote site URL**: the live site URL (for WP-CLI `--url` flag on multisite)

Verify connectivity:
```bash
ssh [SSH_COMMAND] "echo 'Connected' && wp --info --path=[REMOTE_WP_PATH] 2>/dev/null | head -3 || echo 'WP-CLI not found'"
```

If WP-CLI is not available on the server, check common locations:
```bash
ssh [SSH_COMMAND] "which wp 2>/dev/null || ls /usr/local/bin/wp 2>/dev/null || echo 'WP-CLI not installed'"
```

**Note:** cPanel servers typically have WP-CLI pre-installed at `/usr/local/bin/wp`. Check before attempting to install.

If WP-CLI is missing, install it:
```bash
ssh [SSH_COMMAND] "curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && mv wp-cli.phar ~/bin/wp 2>/dev/null || mv wp-cli.phar /usr/local/bin/wp"
```

## Step 2: Confirm What to Deploy

Use `AskUserQuestion` to confirm what should be pushed:

- **Theme files** (rsync the theme directory)
- **Pages** (all pages with content, slug, status, template, and post meta)
- **Custom post types** (e.g. locations, services -- with all meta fields)
- **Media** (images, logos, favicons)
- **Customizer / theme_mods** (brand colours, typography, identity)
- **Site options** (site title, tagline, permalink structure)
- **Menus** (navigation menus with items)

Default: deploy everything.

## Step 3: Identify the Local Source

### If local source is Docker:
```bash
# Set variables
CONTAINER="wp-wordpress-1"  # or from lp_state.md
LOCAL_URL="http://localhost:8083/[subsite-slug]/"

# Verify Docker is running
docker ps --filter name=$CONTAINER --format '{{.Names}}'

# Test WP-CLI locally
docker exec $CONTAINER wp --allow-root option get siteurl --url=$LOCAL_URL
```

### If local source is native WP-CLI:
```bash
wp option get siteurl --path=[LOCAL_WP_PATH]
```

Store the local WP-CLI command prefix as `$LOCAL_WP` for reuse:
- Docker: `docker exec $CONTAINER wp --allow-root --url=$LOCAL_URL`
- Native: `wp --path=$LOCAL_WP_PATH`

## Step 4: Deploy Theme Files

Use rsync over SSH for efficient file transfer. This is idempotent and only transfers changed files.

```bash
rsync -avz --delete \
  --exclude='.DS_Store' \
  --exclude='node_modules' \
  --exclude='.git' \
  [LOCAL_THEME_PATH]/ \
  [SSH_USER]@[SSH_HOST]:[REMOTE_WP_PATH]/wp-content/themes/[THEME_SLUG]/
```

If rsync is not available (some cPanel hosts), fall back to scp:
```bash
scp -r [LOCAL_THEME_PATH]/ [SSH_USER]@[SSH_HOST]:[REMOTE_WP_PATH]/wp-content/themes/[THEME_SLUG]/
```

For Docker, copy theme out first:
```bash
# If theme is bind-mounted locally (check docker-compose.yml volumes), use the local path directly
# Otherwise extract from container:
docker cp $CONTAINER:/var/www/html/wp-content/themes/[THEME_SLUG] /tmp/[THEME_SLUG]
rsync -avz --delete /tmp/[THEME_SLUG]/ [SSH_USER]@[SSH_HOST]:[REMOTE_WP_PATH]/wp-content/themes/[THEME_SLUG]/
```

Verify on remote:
```bash
ssh [SSH_COMMAND] "ls [REMOTE_WP_PATH]/wp-content/themes/[THEME_SLUG]/style.css && echo 'Theme present'"
```

## Step 5: Export and Import Media

Export media attachment URLs from local:
```bash
$LOCAL_WP media list --fields=ID,url,title,file --format=csv > /tmp/media-export.csv
```

For each media file, download from local and upload to remote:

### Docker source:
```bash
# List media files
docker exec $CONTAINER wp --allow-root media list --fields=ID,file,title --format=csv --url=$LOCAL_URL

# Copy media from container to local temp
docker cp $CONTAINER:/var/www/html/wp-content/uploads/ /tmp/wp-uploads/

# Rsync uploads to remote
rsync -avz /tmp/wp-uploads/ [SSH_USER]@[SSH_HOST]:[REMOTE_WP_PATH]/wp-content/uploads/
```

Then register the files in the remote WordPress media library:
```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && find wp-content/uploads/ -type f \( -name '*.jpg' -o -name '*.png' -o -name '*.webp' -o -name '*.svg' -o -name '*.gif' \) -newer wp-content/uploads/.deploy-marker 2>/dev/null" | while read file; do
  ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp media import \$file --preserve-filetime [URL_FLAG]"
done
```

Alternatively, if media count is small, import individually:
```bash
# Import logo
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp media import wp-content/uploads/[YEAR]/[MONTH]/logo.png --title='Site Logo' [URL_FLAG] --porcelain"
```

Track the local-to-remote attachment ID mapping for later use (featured images, custom logo, etc.).

## Step 6: Export and Import Customizer (theme_mods)

Export theme_mods from local:
```bash
$LOCAL_WP option get theme_mods_[THEME_SLUG] --format=json > /tmp/theme-mods.json
```

Before importing, check if the remote already has theme_mods and merge rather than overwrite:
```bash
# Get existing remote mods
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp option get theme_mods_[THEME_SLUG] --format=json [URL_FLAG]" > /tmp/remote-mods.json

# Merge local over remote (local wins on conflicts)
# Use Python or jq to merge the JSON objects
```

Upload merged theme_mods:
```bash
scp /tmp/theme-mods.json [SSH_USER]@[SSH_HOST]:/tmp/theme-mods.json
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp option update theme_mods_[THEME_SLUG] --format=json < /tmp/theme-mods.json [URL_FLAG]"
```

For individual theme_mod values (simpler, no merge needed):
```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp theme mod set [KEY] '[VALUE]' [URL_FLAG]"
```

### Attachment ID remapping

Theme_mods that reference attachment IDs (e.g. `custom_logo`, `site_icon`) need remapping. The local attachment ID will differ from the remote one. Use the ID mapping from Step 5 to update these values after import.

## Step 7: Export and Import Site Options

Key options to sync:
```bash
# Export from local
$LOCAL_WP option get blogname
$LOCAL_WP option get blogdescription
$LOCAL_WP option get permalink_structure
$LOCAL_WP option get page_on_front
$LOCAL_WP option get show_on_front
$LOCAL_WP option get page_for_posts

# Set on remote
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp option update blogname '[VALUE]' [URL_FLAG]"
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp option update blogdescription '[VALUE]' [URL_FLAG]"
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp option update permalink_structure '[VALUE]' [URL_FLAG]"
```

For `page_on_front` and `page_for_posts`, remap local page IDs to remote page IDs (from Step 8 mapping).

## Step 8: Export and Import Pages

Export all pages from local:
```bash
$LOCAL_WP post list --post_type=page --fields=ID,post_title,post_name,post_status,post_parent,menu_order,page_template --format=csv > /tmp/pages-export.csv
```

For each page:

### 8a. Export content
```bash
$LOCAL_WP post get [LOCAL_ID] --field=post_content > /tmp/page-[SLUG]-content.html
```

### 8b. Export post meta
```bash
$LOCAL_WP post meta list [LOCAL_ID] --format=csv > /tmp/page-[SLUG]-meta.csv
```

### 8c. Create on remote
```bash
# Upload content file
scp /tmp/page-[SLUG]-content.html [SSH_USER]@[SSH_HOST]:/tmp/

# Create the page
REMOTE_ID=$(ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp post create /tmp/page-[SLUG]-content.html \
  --post_type=page \
  --post_title='[TITLE]' \
  --post_name='[SLUG]' \
  --post_status='[STATUS]' \
  --page_template='[TEMPLATE]' \
  --menu_order=[ORDER] \
  [URL_FLAG] \
  --porcelain")
```

### 8d. Set post meta on remote
```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp post meta update $REMOTE_ID [META_KEY] '[META_VALUE]' [URL_FLAG]"
```

### 8e. Handle parent pages
Create parent pages first, then set `--post_parent` on child pages using the ID mapping.

### Shell quoting
Post titles and content with special characters (apostrophes, quotes, HTML) will break shell quoting. Always use temp files uploaded via scp, then reference with `$(cat /tmp/file.txt)` or pass the file directly to `wp post create`.

### kses sanitisation
If page content contains `<iframe>`, `<script>`, or other tags that WordPress kses strips, use the `$wpdb->update()` bypass. Upload a PHP script that writes directly to the posts table:

```bash
scp /tmp/bypass-kses.php [SSH_USER]@[SSH_HOST]:/tmp/
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp eval-file /tmp/bypass-kses.php [URL_FLAG]"
```

## Step 9: Export and Import Custom Post Types

Discover registered CPTs on local:
```bash
$LOCAL_WP post-type list --format=csv
```

For each non-default CPT (e.g. `healthcare_location`):

### 9a. List all posts
```bash
$LOCAL_WP post list --post_type=[CPT] --fields=ID,post_title,post_name,post_status,menu_order --format=csv
```

### 9b. Export each post with meta
```bash
$LOCAL_WP post get [LOCAL_ID] --field=post_content > /tmp/cpt-[SLUG]-content.html
$LOCAL_WP post meta list [LOCAL_ID] --format=csv > /tmp/cpt-[SLUG]-meta.csv
```

### 9c. Create on remote
```bash
REMOTE_CPT_ID=$(ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp post create \
  --post_type=[CPT] \
  --post_title='[TITLE]' \
  --post_name='[SLUG]' \
  --post_status='[STATUS]' \
  [URL_FLAG] \
  --porcelain")
```

### 9d. Set meta
```bash
# For each meta field from the CSV (skip internal WP meta starting with _edit_, _wp_)
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp post meta update $REMOTE_CPT_ID '[META_KEY]' '[META_VALUE]' [URL_FLAG]"
```

Keep a mapping of local CPT IDs to remote CPT IDs. Pages that reference CPT posts via meta (e.g. `_healthcare_location_id`) need remapping.

## Step 10: Export and Import Menus

```bash
# List menus
$LOCAL_WP menu list --format=csv

# For each menu, list items
$LOCAL_WP menu item list [MENU_SLUG] --fields=ID,title,type,object,object_id,url,menu_item_parent,position --format=csv
```

Create menus on remote:
```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp menu create '[MENU_NAME]' [URL_FLAG]"
```

Add items, remapping object IDs (page IDs, CPT IDs) using the mapping from previous steps.

## Step 11: Remap Cross-References

After all content is imported, fix cross-references:

1. **Page parent IDs**: update `post_parent` using the page ID mapping
2. **Front page / posts page**: `wp option update page_on_front [REMOTE_ID]`
3. **Location references on pages**: `wp post meta update [PAGE_ID] _healthcare_location_id [REMOTE_LOCATION_ID]`
4. **Custom logo attachment**: `wp theme mod set custom_logo [REMOTE_ATTACHMENT_ID]`
5. **Site icon**: `wp option update site_icon [REMOTE_ATTACHMENT_ID]`
6. **Featured images**: `wp post meta update [POST_ID] _thumbnail_id [REMOTE_ATTACHMENT_ID]`
7. **Content internal links**: search-replace local URLs with remote URLs:
```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp search-replace '[LOCAL_URL]' '[REMOTE_URL]' --all-tables [URL_FLAG]"
```

## .htaccess Preservation Warning

When writing multisite rewrite rules to `.htaccess` on cPanel servers, preserve existing cPanel PHP handler lines. Append WordPress multisite rules above the cPanel section, do not overwrite the file. For multisite conversion on cPanel, `wp core multisite-convert --subdomains=0` handles wp-config.php constants automatically, but `.htaccess` multisite rewrite rules must be written manually.

## Step 12: Flush and Verify

```bash
ssh [SSH_COMMAND] "cd [REMOTE_WP_PATH] && wp cache flush [URL_FLAG] && wp rewrite flush [URL_FLAG]"
```

Verify the live site:
1. Check homepage loads (HTTP 200)
2. Check a sample page loads with correct content
3. Check theme is active and styled
4. Check media images load (no broken images)
5. Check customizer values applied (brand colours visible)

```bash
curl -s -o /dev/null -w '%{http_code}' [REMOTE_SITE_URL]
```

## Validation Checkpoints

- [ ] SSH connection verified
- [ ] Remote WP-CLI functional
- [ ] Theme files uploaded and activated
- [ ] All pages created with correct content and slugs
- [ ] Custom post types created with meta
- [ ] Media uploaded and registered
- [ ] Customizer settings applied (theme_mods)
- [ ] Site options set (title, tagline, permalinks)
- [ ] Cross-references remapped (page parents, location IDs, attachment IDs)
- [ ] URL search-replace completed
- [ ] Cache flushed
- [ ] Frontend verified visually

## Related Skills

- **lp-subsite-deploy** -- LeadScalePro-specific wrapper for deploying multisite subsites
- **wp-blog-publisher** -- publish blog posts via SSH
- **lp-subsite-setup** -- configure a local multisite subsite (pre-deployment)
- **visual-qa** -- visual regression testing post-deployment
