---
name: client-update
description: "Propagate a client data change across all client files. Use when a client's name, service offering, contact details, branding, or other core details have changed. Finds every reference in the client folder and updates them. Flags downstream strategic work needed. Triggers on: 'client changed their name', 'they rebranded', 'new contact', 'updated their services', 'client update', 'name change', 'Raise the Bar Psychology is now Raise the Bar Clinic'."
---

# Client Update

Propagate a change in client data across all files in the client folder. Log the change. Flag what downstream work is needed.

## Step 1: Understand the change

Ask:
- What changed? (name, services, contact details, branding, location, other)
- What was the old value?
- What is the new value?
- Effective date?

## Step 2: Scan and list references

Scan all files in the client folder for the old value. List every file and occurrence found:

```
Found [N] references across [M] files:
- client_profile.md (line 3): "Raise the Bar Psychology" → update to "Raise the Bar Clinic"
- google_ads/2026-06/monthly-review-2026-06.md (line 1): "Raise the Bar Psychology"
- seo/2026-05/keyword-map.md (lines 4, 12, 18)
- meetings/2026-06-20-meeting-notes.md (line 1)
- [etc.]
```

Ask: "I found [N] references. Want me to update all of them?"

## Step 3: Update files

For each confirmed file:
- Update the old value to the new value
- Preserve surrounding context — do not rewrite sentences, only change the value

For `client_profile.md`: add a change log entry at the top:
```markdown
## Change Log
- YYYY-MM-DD: [What changed] (old: [value] → new: [value])
```

## Step 4: Flag strategic implications

After updating files, identify what downstream work the change creates:

| Change type | Likely downstream work |
|-------------|----------------------|
| Business name change | Google Ads brand campaign update, RSA refresh, page title/meta updates, GMB name update |
| New service added | New service page, keyword research, ad group, GMB service addition |
| Service removed | Pause related ad groups, redirect or remove service page |
| New location | Local SEO for new location, GMB listing, location-specific landing page |
| Contact details changed | Update website, GMB listing, ad extensions |
| Rebrand (logo/colours) | WordPress visual updates, ad creative refresh |

Present the relevant implications:
"This change has downstream implications:
- [Specific work item] — recommend running [skill]
- [Specific work item] — recommend running [skill]

Want me to queue any of these now?"

## Step 5: Confirm completion

"Update complete. [N] references updated across [M] files. Change logged in client_profile.md."
