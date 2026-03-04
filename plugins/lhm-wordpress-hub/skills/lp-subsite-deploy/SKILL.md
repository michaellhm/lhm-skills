---
name: lp-subsite-deploy
description: "Deploy a LeadScalePro multisite subsite from local Docker to the live server. Use this when the user says 'deploy the subsite', 'push subsite to live', 'deploy to LeadScalePro', 'push to production', 'deploy client site', 'lp-subsite-deploy', 'sync subsite to server', or 'push [client] live'. Exports everything from the local Docker subsite (theme, pages, locations, images, customizer, options) and creates/updates the matching subsite on the remote multisite. Reads SSH credentials from the multisite project's SSH access file."
---

# LP Subsite Deploy

Deploy a complete WordPress multisite subsite from the local Docker development environment to the live LeadScalePro multisite server. This skill handles the full pipeline: reading SSH credentials, identifying the local subsite, creating the remote subsite if needed, and pushing all content (theme, pages, custom post types, media, customizer settings, and options).

## When to Use This Skill

- Deploying a new client subsite to production for the first time
- Syncing local changes on a subsite to the live server
- Re-deploying after local content or design changes
- Pushing landing pages, locations, and branding to production

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-subsite-deploy/LEARNED.md` -- apply any relevant entries
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/wp-ssh-deploy/LEARNED.md` -- apply SSH deployment learnings
3. Read `${CLAUDE_PLUGIN_ROOT}/references/lp-reference.md` -- especially "Central Multisite Infrastructure"
4. Read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for WP-CLI patterns

## Step 1: Locate the Multisite Project

The LeadScalePro multisite Docker setup lives in a central directory. Find it by checking for the `docker-compose.yml` and `wp.sh` files:

```bash
# Convention: the multisite project is adjacent to client folders
# Look for it by searching for the wp.sh helper or docker-compose.yml with multisite config
find ~/Documents -maxdepth 3 -name "wp.sh" -path "*leadscalepro*" 2>/dev/null
```

Store this as `$MULTISITE_ROOT`.

## Step 2: Read SSH Access Credentials

Look for an SSH access file in the multisite project root. Common filenames:
- `SSH Access.md`
- `ssh.md`
- `ssh-access.md`
- `.ssh-config`

```bash
ls "$MULTISITE_ROOT"/SSH*.md "$MULTISITE_ROOT"/ssh*.md 2>/dev/null
```

Read the file and extract:
- **Server IP or hostname**
- **SSH username**
- **SSH key path** (look for references to `~/.ssh/` key files)
- **Key passphrase** (if listed)
- **Remote WordPress path** (derive from domain: `~/[domain]/` on cPanel)
- **cPanel URL** (if available, for reference)

**Important:** Never log, echo, or display passwords or passphrases in command output. Use them only in `expect` scripts or ssh-agent operations.

### Add SSH key to agent

If the key is passphrase-protected, add it to the SSH agent:
```bash
expect -c '
spawn ssh-add [KEY_PATH]
expect "passphrase"
send "[PASSPHRASE]\r"
expect eof
'
```

### Verify connection
```bash
ssh [SSH_COMMAND] "echo 'Connected' && whoami && wp --info 2>/dev/null | head -3"
```

## Step 3: Identify the Local Subsite

### 3a. Verify Docker is running
```bash
cd $MULTISITE_ROOT && ./wp.sh status
```

If not running:
```bash
cd $MULTISITE_ROOT && ./wp.sh start
```

Wait for containers to be healthy.

### 3b. List available subsites
```bash
docker exec wp-wordpress-1 wp --allow-root site list --format=table
```

### 3c. Ask which subsite to deploy (if multiple)
Use `AskUserQuestion` if more than one non-main subsite exists:

> "Which subsite should I deploy to production?"

List available subsites as options.

Store:
- `$LOCAL_SUBSITE_URL` (e.g. `http://localhost:8083/ehp/`)
- `$SUBSITE_SLUG` (e.g. `ehp`)
- `$SUBSITE_ID`

### 3d. Identify remote target
The remote subsite path mirrors the local slug. The remote multisite URL is derived from the SSH access file's domain field.

- `$REMOTE_BASE_URL` (e.g. `https://lp.leadscalepro.com.au/`)
- `$REMOTE_SUBSITE_URL` (e.g. `https://lp.leadscalepro.com.au/ehp/`)
- `$REMOTE_WP_PATH` (e.g. `~/lp.leadscalepro.com.au/`)
- `$URL_FLAG` = `--url=$REMOTE_SUBSITE_URL`

## Step 4: Audit Local Subsite Content

Before deploying, inventory what exists locally:

```bash
CONTAINER="wp-wordpress-1"
LOCAL_WP="docker exec $CONTAINER wp --allow-root --url=$LOCAL_SUBSITE_URL"

echo "=== Theme ==="
$LOCAL_WP theme list --status=active --format=csv

echo "=== Pages ==="
$LOCAL_WP post list --post_type=page --fields=ID,post_title,post_name,post_status --format=table

echo "=== Custom Post Types ==="
$LOCAL_WP post-type list --format=csv | grep -v "^name" | grep -v "^post$\|^page$\|^attachment$\|^revision$\|^nav_menu_item$\|^wp_"

echo "=== Locations ==="
$LOCAL_WP post list --post_type=healthcare_location --fields=ID,post_title,post_name,post_status --format=table 2>/dev/null

echo "=== Media ==="
$LOCAL_WP media list --fields=ID,title,file --format=table

echo "=== Theme Mods ==="
$LOCAL_WP option get theme_mods_$(${LOCAL_WP} theme list --status=active --field=name) --format=json 2>/dev/null

echo "=== Site Options ==="
$LOCAL_WP option get blogname
$LOCAL_WP option get blogdescription
```

Present the inventory to the user for confirmation before deploying.

## Step 5: Ensure Remote Subsite Exists

### 5a. Check if multisite is enabled on remote
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp config get MULTISITE"
```

If not multisite yet, the network must be set up first (this is a one-time operation):
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp core multisite-convert --subdomains=0 --title='[NETWORK_TITLE]'"
```

Then update `.htaccess` with multisite rewrite rules (preserve any existing cPanel PHP handler lines).

**Note:** The remote multisite uses subdirectory install (not subdomains). Subsites are at `/[slug]/` paths.

### 5b. Check if the subsite already exists
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp site list --format=csv"
```

### 5c. Create subsite if needed
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp site create \
  --slug=$SUBSITE_SLUG \
  --title='[SITE_TITLE]' \
  --email=admin@localhealthmarketing.com.au"
```

Note the new site ID.

## Step 6: Deploy Theme

### 6a. Identify the local theme path

Check the `docker-compose.yml` volumes for bind-mounted theme paths:
```bash
grep -A5 "volumes:" "$MULTISITE_ROOT/docker-compose.yml" | grep themes
```

If the theme is bind-mounted (typical), use the local filesystem path directly. Otherwise, copy from the container.

**Note:** The healthcare-theme is typically bind-mounted in `docker-compose.yml` at `./wp-content/themes/healthcare-theme`, so the local filesystem path can be used directly for rsync (no need for `docker cp`).

### 6b. Upload theme to remote
```bash
# Prefer rsync for efficiency
rsync -avz --delete \
  --exclude='.DS_Store' \
  --exclude='node_modules' \
  --exclude='.git' \
  -e "ssh [SSH_KEY_FLAGS]" \
  $LOCAL_THEME_PATH/ \
  [SSH_USER]@[SSH_HOST]:$REMOTE_WP_PATH/wp-content/themes/[THEME_SLUG]/
```

### 6c. Network-enable and activate on subsite
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp theme enable [THEME_SLUG] --network 2>/dev/null; wp theme activate [THEME_SLUG] $URL_FLAG"
```

## Step 7: Deploy Media

### 7a. Export uploads from Docker
```bash
# Get the uploads directory for this subsite
# In multisite, uploads are at wp-content/uploads/sites/[SITE_ID]/
docker cp $CONTAINER:/var/www/html/wp-content/uploads/sites/$SUBSITE_ID/ /tmp/wp-uploads-$SUBSITE_SLUG/
```

If the subsite uses the main site's uploads (site ID 1 or non-multisite local):
```bash
docker cp $CONTAINER:/var/www/html/wp-content/uploads/ /tmp/wp-uploads-$SUBSITE_SLUG/
```

### 7b. Upload to remote
On the remote multisite, find the correct uploads path for the subsite:
```bash
REMOTE_SITE_ID=$(ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp site list --field=blog_id --slug=$SUBSITE_SLUG")
```

```bash
rsync -avz \
  -e "ssh [SSH_KEY_FLAGS]" \
  /tmp/wp-uploads-$SUBSITE_SLUG/ \
  [SSH_USER]@[SSH_HOST]:$REMOTE_WP_PATH/wp-content/uploads/sites/$REMOTE_SITE_ID/
```

### 7c. Register media in WordPress
For each uploaded file, register it in the media library:
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp media import wp-content/uploads/sites/$REMOTE_SITE_ID/[FILE] --title='[TITLE]' $URL_FLAG --porcelain"
```

Or bulk import:
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && find wp-content/uploads/sites/$REMOTE_SITE_ID/ -type f \( -name '*.jpg' -o -name '*.png' -o -name '*.webp' -o -name '*.svg' \) -exec wp media import {} $URL_FLAG --porcelain \;"
```

Track the local-to-remote attachment ID mapping.

## Step 8: Deploy Customizer Settings

Export all theme_mods from local:
```bash
THEME_SLUG=$($LOCAL_WP theme list --status=active --field=name)
$LOCAL_WP theme mod list --format=table
```

Set each theme_mod on remote individually (safest approach, avoids merge conflicts):
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp theme mod set [KEY] '[VALUE]' $URL_FLAG"
```

Common keys to transfer:
- Brand colours: `healthcare_color_primary`, `healthcare_color_primary_dark`, `healthcare_color_primary_light`, `healthcare_color_heading`, `healthcare_color_body`, `healthcare_color_nav_bg`, `healthcare_color_announcement_bg`
- Typography: `healthcare_font_family`
- Identity: `healthcare_clinic_name`, `healthcare_tagline`
- Social proof: `healthcare_review_count`, `healthcare_google_rating`, `healthcare_review_url`
- Social media: `healthcare_social_facebook`, `healthcare_social_instagram`, `healthcare_social_linkedin`
- Logo: `custom_logo` (needs attachment ID remapping)

### Remap attachment IDs
If `custom_logo` or `site_icon` reference local attachment IDs, remap to the remote IDs from Step 7.

## Step 9: Deploy Site Options

```bash
# Site identity
LOCAL_BLOGNAME=$($LOCAL_WP option get blogname)
LOCAL_BLOGDESC=$($LOCAL_WP option get blogdescription)
LOCAL_PERMALINK=$($LOCAL_WP option get permalink_structure)

ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && \
  wp option update blogname '$LOCAL_BLOGNAME' $URL_FLAG && \
  wp option update blogdescription '$LOCAL_BLOGDESC' $URL_FLAG && \
  wp option update permalink_structure '$LOCAL_PERMALINK' $URL_FLAG"
```

## Step 10: Deploy Custom Post Types (Locations)

### 10a. Export locations from local
```bash
$LOCAL_WP post list --post_type=healthcare_location --fields=ID,post_title,post_name,post_status,menu_order --format=csv
```

### 10b. For each location, export meta
```bash
$LOCAL_WP post meta list [LOCAL_ID] --format=csv
```

Filter to relevant meta keys (prefix `_healthcare_location_`):
- `_healthcare_location_phone`
- `_healthcare_location_address`
- `_healthcare_location_maps_url`
- `_healthcare_location_booking_url`
- `_healthcare_location_free_call_url`
- `_healthcare_location_opening_hours`

### 10c. Create locations on remote
```bash
REMOTE_LOC_ID=$(ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post create \
  --post_type=healthcare_location \
  --post_title='[TITLE]' \
  --post_name='[SLUG]' \
  --post_status=publish \
  $URL_FLAG \
  --porcelain")
```

### 10d. Set location meta
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && \
  wp post meta update $REMOTE_LOC_ID _healthcare_location_phone '[PHONE]' $URL_FLAG && \
  wp post meta update $REMOTE_LOC_ID _healthcare_location_address '[ADDRESS]' $URL_FLAG && \
  wp post meta update $REMOTE_LOC_ID _healthcare_location_booking_url '[URL]' $URL_FLAG && \
  wp post meta update $REMOTE_LOC_ID _healthcare_location_opening_hours '[HOURS]' $URL_FLAG"
```

Track local-to-remote location ID mapping.

## Step 11: Deploy Pages

### 11a. Export pages from local
```bash
$LOCAL_WP post list --post_type=page --fields=ID,post_title,post_name,post_status,post_parent,menu_order,page_template --format=csv
```

### 11b. For each page, export content and meta
```bash
# Content
$LOCAL_WP post get [LOCAL_ID] --field=post_content > /tmp/page-[SLUG].html

# Meta (filter to custom meta, skip internal WP keys)
$LOCAL_WP post meta list [LOCAL_ID] --format=csv
```

### 11c. Create pages on remote
Upload content via scp, then create via WP-CLI:
```bash
scp /tmp/page-[SLUG].html [SSH_USER]@[SSH_HOST]:/tmp/

REMOTE_PAGE_ID=$(ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post create /tmp/page-[SLUG].html \
  --post_type=page \
  --post_title='[TITLE]' \
  --post_name='[SLUG]' \
  --post_status='[STATUS]' \
  --page_template='[TEMPLATE]' \
  --menu_order=[ORDER] \
  $URL_FLAG \
  --porcelain")
```

### Shell quoting safety
Always use temp files for content and titles. Never pass HTML content or titles with special characters as inline shell arguments.

### kses bypass
If pages contain `<iframe>` or `<script>` tags (e.g. Google Maps embeds), these get stripped by WordPress kses sanitisation. Use the `$wpdb->update()` bypass:

```php
<?php
// bypass-kses.php
$page_id = $argv[1] ?? 0;
$content = file_get_contents('/tmp/page-content.html');
global $wpdb;
$wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $page_id]);
clean_post_cache($page_id);
echo "Updated post $page_id bypassing kses";
```

```bash
scp bypass-kses.php [SSH_USER]@[SSH_HOST]:/tmp/
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp eval-file /tmp/bypass-kses.php $REMOTE_PAGE_ID $URL_FLAG"
```

### 11d. Set page meta
```bash
# Location reference (remap ID)
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post meta update $REMOTE_PAGE_ID _healthcare_location_id $REMOTE_LOC_ID $URL_FLAG"

# Featured image (remap attachment ID)
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post meta update $REMOTE_PAGE_ID _thumbnail_id $REMOTE_ATTACHMENT_ID $URL_FLAG"
```

### 11e. Set page parents
After all pages are created, set parent relationships using the ID mapping:
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post update $REMOTE_CHILD_ID --post_parent=$REMOTE_PARENT_ID $URL_FLAG"
```

### 11f. Set front page
If a static front page is set locally:
```bash
LOCAL_FRONT=$($LOCAL_WP option get page_on_front)
# Remap to remote ID
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp option update show_on_front page $URL_FLAG"
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp option update page_on_front $REMOTE_FRONT_ID $URL_FLAG"
```

## Step 12: URL Search-Replace

Replace all local URLs with remote URLs in the database:
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp search-replace 'http://localhost:8083/$SUBSITE_SLUG' 'https://[REMOTE_DOMAIN]/$SUBSITE_SLUG' --all-tables-with-prefix $URL_FLAG --dry-run"
```

Review the dry-run output, then run for real:
```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp search-replace 'http://localhost:8083/$SUBSITE_SLUG' 'https://[REMOTE_DOMAIN]/$SUBSITE_SLUG' --all-tables-with-prefix $URL_FLAG"
```

## Step 13: Flush and Verify

```bash
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp cache flush $URL_FLAG && wp rewrite flush $URL_FLAG"
```

### Verify deployment:
```bash
# HTTP status
curl -s -o /dev/null -w '%{http_code}' $REMOTE_SUBSITE_URL

# Site title
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp option get blogname $URL_FLAG"

# Page count
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post list --post_type=page --post_status=publish --format=count $URL_FLAG"

# Location count
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp post list --post_type=healthcare_location --post_status=publish --format=count $URL_FLAG"

# Theme active
ssh [SSH_COMMAND] "cd $REMOTE_WP_PATH && wp theme list --status=active --field=name $URL_FLAG"
```

Open the site in a browser to visually confirm. Use the Playwright MCP tools if available:
```
browser_navigate to $REMOTE_SUBSITE_URL
browser_snapshot to check structure
```

## Step 14: Update State

If a `lp/lp_state.md` or deployment state file exists, update it with:
- Remote subsite URL
- Deployment date
- Deployed page IDs and URLs
- Deployment status

## Approval Gate

Tell the user:

> "Subsite deployed to [REMOTE_SUBSITE_URL]. [N] pages, [N] locations, theme and branding all synced. Check the live site and confirm it looks correct."

Options:
- "Looks good -- deployment complete"
- "Issues found -- need fixes"
- "Run visual-qa to compare local vs live"

## Validation Checkpoints

- [ ] SSH connection verified
- [ ] Local Docker subsite identified and audited
- [ ] Remote subsite created (or confirmed existing)
- [ ] Theme uploaded and activated
- [ ] Media files uploaded and registered
- [ ] Customizer / theme_mods applied
- [ ] Site options set (title, tagline)
- [ ] Locations created with all meta fields
- [ ] Pages created with content and meta
- [ ] Cross-references remapped (location IDs, attachment IDs, page parents)
- [ ] URL search-replace completed
- [ ] Cache flushed
- [ ] Frontend verified (HTTP 200, correct title, styled correctly)

## Related Skills

- **wp-ssh-deploy** -- general-purpose WordPress SSH deployment (this skill is the LeadScalePro-specific wrapper)
- **lp-subsite-setup** -- configure a local subsite before deployment
- **visual-qa** -- pixel-perfect visual comparison post-deployment
- **wp-blog-publisher** -- publish blog posts via SSH
