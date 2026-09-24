---
title: Guided Chrome changes in Google Ads
description: How to make Google Ads changes AdPulse can't, using Claude in Chrome with Michael navigating and approving. UI paths verified 2026-09-24.
---

# Guided Chrome changes in Google Ads

Use this for anything the capability table marks "Chrome only", or when AdPulse fails.

## Procedure

1. Read the `anthropic-skills:chrome-browser` skill, then load the Chrome tools in one ToolSearch call: `tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`, `find`, `read_page`, `get_page_text`, `form_input`.
2. Call `tabs_context_mcp`, then open a **new** tab. Don't reuse Michael's tabs.
3. Navigate to `https://ads.google.com/aw/overview`. **Don't add `__e=`, `ocid=` or other parameters** to a fresh URL; that returns a 400 error. The account picker loads.
4. Tell Michael, in one message:
   - which account to pick (name and customer ID)
   - which campaign and screen to open
   - to approve any "Confirm it's you" prompt
   - to reply when he's there

   Then stop and wait.
5. When he replies, take a screenshot to confirm the right account and screen.
6. Make the change: prefer `find` for element refs, use screenshots for coordinates, and wait 2-4 seconds after saves and page loads.
7. After saving, take a screenshot of the saved state (the table row or settings summary) as verification.
8. Where GAQL can read the setting, verify with it too (for example `customer.call_reporting_setting.call_conversion_action`).
9. Close the tab at the end unless Michael wants it kept open.

Once the account is selected, account-level pages can be opened by URL. Reuse the `ocid`, `ascid`, `euid`, `__u`, `uscid`, `__c` and `authuser` parameters from the current tab URL.

Stop and ask Michael if a click or save fails 2-3 times, or if a screen doesn't match what's expected.

## UI paths

**PMax audience signals and search themes**

- Path: Campaigns > (PMax campaign) > Asset groups > table view > pencil icon in the "Audience signal" column. This opens "Edit signals".
- Search themes: expand the "Search themes" panel, type into "Add search themes", press Enter.
- Audiences: under "Audience signal", click "Additional signals" > "Interests and detailed demographics", then type into the search box.
  - Results show their type (Affinity, In-market). Pick the type that was approved.
  - Names differ slightly from how people say them: in-market is "Sport & Fitness", not "Sports & Fitness". Use `find` to locate options by label and type.
  - The search box keeps the previous query. Triple-click it before typing a new one.
- Click "Save" at the bottom. On success it returns to the asset groups table, and the "Audience signal" column shows the new signal.
- **Health policy:** Google rejects health-intent search themes (for example "physio appointment booking") under "Health in personalised advertising", and highlights them in red. Remove the rejected theme, save the rest, and tell Michael. Don't propose health-condition or booking-intent themes, or custom/past-patient health audiences.

**Account default call conversion action**

- Path: Goals > Conversions > Conversion settings (`/aw/conversions/customersettings`) > "Call conversion action" > choose from the dropdown > Save.
- The summary row shows the selected action when saved.
- GAQL check: `SELECT customer.call_reporting_setting.call_conversion_action FROM customer`.

**Conversion action primary/secondary and campaign goals**

- Path: Goals > Conversions > Summary, or the campaign's settings > Goals.
- This is a consequential change. Get explicit approval for the exact action and state.

## Known behaviours

- "Confirm it's you" re-authentication can appear before saves. Only Michael can complete it. If a previous session's pending draft is waiting on it, don't resubmit it without asking.
- Google Ads Editor changes Michael makes himself count as done only on his confirmation. Record them as owner-reported until they're read back.
- Screenshots come back at the full coordinate frame. Use `scale: 0.5` for quick looks, and full scale before precise clicks.
