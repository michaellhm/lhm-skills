---
name: lp-subsite-setup
description: "Configure a WordPress multisite subsite for a landing page campaign. Use this when the user says 'set up landing page site', 'configure subsite', 'set up the health theme', 'set up branding on the landing page site', 'configure the multisite for [client]', or 'lp-subsite-setup'. Handles theme activation, site identity, brand colours, typography, social proof, social media URLs, and location CPT entries. Always run this before lp-deploy-1."
---

# LP Subsite Setup

Configure a WordPress multisite subsite with the client's branding, identity, and content structure. This is the foundation every landing page deploys on top of.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-subsite-setup/LEARNED.md` — apply any relevant entries
2. Read `client_profile.md` to load branding, logo, colours, social media URLs, and clinic info
3. Read `lp/lp_state.md` if it exists — it may already contain the subsite URL and theme slug
4. Read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for WP-CLI patterns

## Step 1: Confirm Subsite Config

If `lp/lp_state.md` already has a subsite URL and theme, skip to Step 2.

Use the `AskUserQuestion` tool to confirm:
- The multisite base URL (e.g. `http://localhost:8083/`)
- The subsite slug for this client (e.g. `physio-clinic-name`)
- The industry/theme to activate (default: `lhm-health` for healthcare clients)

Then detect the Docker container name:
```bash
docker ps --format "{{.Names}}" | grep -i wp
```

Store as `CONTAINER` for all subsequent commands. If not using Docker, run WP-CLI directly.

## Step 2: Create or Confirm the Subsite

Check if the subsite already exists:
```bash
docker exec $CONTAINER wp --allow-root site list --url=[BASE_URL] --format=csv
```

If it doesn't exist, create it:
```bash
docker exec $CONTAINER wp --allow-root site create \
  --slug=[CLIENT_SLUG] \
  --title="[CLINIC_NAME]" \
  --email=admin@localhealthmarketing.com.au \
  --url=[BASE_URL]
```

Note the new subsite ID from the output. The subsite URL is `[BASE_URL][CLIENT_SLUG]/`.

## Step 3: Activate Theme

Activate the correct theme on the subsite:
```bash
docker exec $CONTAINER wp --allow-root theme activate [THEME_SLUG] \
  --url=[SUBSITE_URL]
```

Verify activation:
```bash
docker exec $CONTAINER wp --allow-root theme status --url=[SUBSITE_URL]
```

**Theme slug mapping:**
- Healthcare, allied health, physiotherapy, chiropractic, podiatry → `lhm-health`
- Add new mappings to LEARNED.md as new themes are created

## Step 4: Configure Site Identity

### 4a. Upload Logo

If a logo file path is in `client_profile.md`, import it as a media attachment:
```bash
docker exec $CONTAINER wp --allow-root media import "[LOGO_URL_OR_PATH]" \
  --url=[SUBSITE_URL] \
  --title="[CLINIC_NAME] Logo"
```

Note the attachment ID from output. Then set it as the site logo:
```bash
docker exec $CONTAINER wp --allow-root option update theme_mods_[THEME_SLUG] \
  '{"custom_logo": [ATTACHMENT_ID]}' \
  --format=json \
  --url=[SUBSITE_URL]
```

If updating a theme_mods key that already has values, read first then merge — do not overwrite the entire object.

### 4b. Set Site Title and Tagline

```bash
docker exec $CONTAINER wp --allow-root option update blogname "[CLINIC_NAME]" \
  --url=[SUBSITE_URL]

docker exec $CONTAINER wp --allow-root option update blogdescription "[TAGLINE]" \
  --url=[SUBSITE_URL]
```

### 4c. Upload and Set Favicon (Site Icon)

```bash
docker exec $CONTAINER wp --allow-root media import "[FAVICON_URL_OR_PATH]" \
  --url=[SUBSITE_URL] \
  --title="[CLINIC_NAME] Favicon"

docker exec $CONTAINER wp --allow-root option update site_icon [FAVICON_ATTACHMENT_ID] \
  --url=[SUBSITE_URL]
```

## Step 5: Configure Brand Settings

Read the current theme_mods to see what keys the health theme uses before writing:
```bash
docker exec $CONTAINER wp --allow-root option get theme_mods_[THEME_SLUG] \
  --format=json \
  --url=[SUBSITE_URL]
```

Map these values from `client_profile.md` to the theme's mod keys. Common key names for `lhm-health`:

| Setting | theme_mods key |
|---------|---------------|
| Primary colour | `primary_color` |
| Primary dark | `primary_dark_color` |
| Primary light | `primary_light_color` |
| Header colour | `header_color` |
| Body text colour | `body_text_color` |
| Google font | `body_font_family` |

Build the full theme_mods JSON by reading the existing value, merging in the brand values, then updating:
```bash
# Read existing
EXISTING=$(docker exec $CONTAINER wp --allow-root option get theme_mods_[THEME_SLUG] --format=json --url=[SUBSITE_URL])

# Write merged JSON
docker exec $CONTAINER wp --allow-root option update theme_mods_[THEME_SLUG] \
  '[MERGED_JSON]' \
  --format=json \
  --url=[SUBSITE_URL]
```

If you hit unfamiliar key names, check the theme's `functions.php` or `customizer.php` for registered settings. Add confirmed keys to LEARNED.md.

## Step 6: Configure Social Proof and Social Media

These are typically stored as theme_mods or custom options. Check the theme's customizer file to confirm, then update:

```bash
# Social proof
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_google_review_count "[COUNT]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_google_rating "[RATING]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_google_reviews_url "[URL]" --url=[SUBSITE_URL]

# Social media URLs
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_facebook_url "[URL]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_instagram_url "[URL]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_tiktok_url "[URL]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root option update [THEME_SLUG]_youtube_url "[URL]" --url=[SUBSITE_URL]
```

Skip any social media URLs not present in `client_profile.md`.

## Step 7: Create Location CPT Entries

For each location in `client_profile.md`, create a post using the `location` CPT (or whatever CPT the health theme registers):

```bash
docker exec $CONTAINER wp --allow-root post create \
  --post_type=location \
  --post_title="[SUBURB] Clinic" \
  --post_status=publish \
  --url=[SUBSITE_URL]
```

After creating each location post, add its meta fields:
```bash
LOCATION_ID=<id from output>

docker exec $CONTAINER wp --allow-root post meta add $LOCATION_ID phone "[PHONE]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root post meta add $LOCATION_ID address "[ADDRESS]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root post meta add $LOCATION_ID google_maps_embed "[MAPS_EMBED_URL]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root post meta add $LOCATION_ID booking_url "[BOOKING_URL]" --url=[SUBSITE_URL]
docker exec $CONTAINER wp --allow-root post meta add $LOCATION_ID open_hours "[HOURS_STRING]" --url=[SUBSITE_URL]
```

If the theme uses ACF for CPT fields, use `wp acf post update` instead. Check LEARNED.md for the confirmed approach.

## Step 8: Write State File

Create or update `/lp/lp_state.md`:

```markdown
# Landing Page Campaign State

## Multisite Config
- **WP Base URL**: [BASE_URL]
- **Subsite URL**: [SUBSITE_URL]
- **Subsite ID**: [SUBSITE_ID]
- **Theme**: [THEME_SLUG]
- **Container**: [DOCKER_CONTAINER_NAME]

## Subsite Setup
| Item | Status | Notes |
|------|--------|-------|
| Subsite created | ✅ | ID: [ID] |
| Theme activated | ✅ | [THEME_SLUG] |
| Logo | ✅ / ⏳ | Attachment ID: [ID] |
| Site title + tagline | ✅ | |
| Favicon | ✅ / ⏳ | |
| Brand colours | ✅ | |
| Social proof | ✅ | |
| Social media URLs | ✅ | |
| Locations CPT | ✅ | [N] locations |

## Campaign
- **Brief**: /lp/campaign_brief.md
- **Ad Groups**: (populated by lp-copy)

## Pages Built
| Ad Group | Copy File | Prototype | HTML Push | Blocks | Post ID | Status |
|----------|-----------|-----------|-----------|--------|---------|--------|
```

## Step 9: Approval Gate

Tell the user:

> "Subsite setup complete for [CLINIC_NAME] at [SUBSITE_URL]. Theme, branding, and location data are configured. Ready to run **lp-copy** to write the landing page copy, or **lp-prototype** if copy is already done."
