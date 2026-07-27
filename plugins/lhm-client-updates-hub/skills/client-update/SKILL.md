---
name: client-update
description: "Propagate a client data change across all client files. Use when a client's name, service offering, contact details, branding, or other core details have changed. Finds every reference in the client folder and updates them. Flags downstream strategic work needed. Triggers on: 'client changed their name', 'they rebranded', 'new contact', 'updated their services', 'client update', 'name change', 'Raise the Bar Psychology is now Raise the Bar Clinic'."
---

# Client Update

Propagate a change in client data across all files in the client folder. Log the change. Flag what downstream work is needed.

## Step 1: Understand the change

**Read this before asking anything.** If invoked as a handoff from `post-meeting-review`, its Step 3.5 sweep has already produced the change, the file list, the forward-looking and historical split, the reversed decisions, and anything flagged on live advertising surfaces. Take those as given. Skip the questions below, skip the scan in Step 2, skip the detection work in 2b, 2c and 2d, then **start at Step 2e**. Do not skip that gate. It is the only thing standing between the handoff and edited files, because `post-meeting-review` deliberately edits nothing itself. When you finish Step 5, hand control back so `post-meeting-review` can continue at its Step 4.

Otherwise, ask:
- What changed? (name, services, contact details, branding, location, other)
- Is this a **substitution** (old value → new value) or a **removal** (a service discontinued, a location closed, a practitioner departed, a claim withdrawn)?
- What was the old value? What is the new value, if there is one?
- Effective date?

**Removals behave differently to substitutions.** There is no new value to swap in, so the find-and-replace flow in Step 3 does not apply. References get stripped, redirected, left in place pending a decision, or replaced with an agreed alternative. Say which mode you are in before scanning.

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

### 2b. Sort the hits before touching anything

| Pile | Examples | Action |
|------|----------|--------|
| Forward-looking artefacts | sitemaps, keyword maps, redirect maps, site and page briefs, GBP optimisation plans, landing page copy, project management docs, live site content, ad copy | Needs updating |
| Historical records | past meeting notes, monthly reports, analytics exports, prior strategy sessions, delivered reports | Leave alone |

Editing historical records rewrites history and destroys the audit trail. A report that said the client offered podiatry in May was correct in May.

### 2c. Check for decisions this change reverses

Search the forward-looking pile for anything marked *confirmed*, *signed off*, *decided*, or *approved* that the change invalidates. A service removal can overturn work a colleague signed off days earlier, along with the research behind it, and nobody notices until the build breaks.

When you find one, surface it with the original reasoning attached and name who made the call. Shape of it:

> Dropping [service] reverses the [decision] that [name] confirmed on [date]. That decision [what it did] on the back of [the evidence behind it]. It can no longer stand, which leaves [the concrete consequence]. This needs a call before [the specific file] is edited.

**Do not resolve these yourself.** Present the options and their trade-offs, and let the user decide. Whatever they choose becomes an input to Step 3.

### 2d. For regulated services, check live advertising surfaces

The client folder is not the whole picture. Google Business Profile categories, service lists, business descriptions and directory entries are all advertising surfaces, and a compliance breach there is live exposure independent of any rebuild in progress. Check the GBP plan and flag anything that needs pulling down today rather than at launch.

### 2e. Confirm before editing anything

This gate applies on every path, including the handoff from `post-meeting-review`. Nothing gets edited until the user has answered.

Ask: "I found [N] references across [M] files. [X] need updating and [Y] are historical, so they stay as they are. [Z] conflicts need your call before I touch anything. Want me to proceed?"

Resolve the conflicts in this exchange, whether they came from 2c or from the handoff, so Step 3 has a decision to act on rather than a hole.

## Step 3: Update files

For each confirmed **forward-looking** file:
- **Substitutions:** update the old value to the new value. Preserve surrounding context, changing only the value rather than rewriting sentences.
- **Removals:** strip the reference, or replace it with whatever the user decided in 2e. Where a removal leaves a structural hole (a redirect target that no longer exists, a nav item with nowhere to point) and the user has not given you a destination, do not invent one. Leave it and list it under Step 4.

Historical records do not get touched, whether the sort came from 2b or arrived with the handoff.

For `client_profile.md`: add a change log entry at the top. If `post-meeting-review` has already updated the profile in its own Step 3, do not undo or duplicate that work; just add the log entry alongside it.
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
| Service removed | Pause related ad groups and negate the terms, redirect or remove the service page, remove the GBP category and service entry, rewrite the GBP business description, find new destinations for any URLs that redirected to it, check directory listings |
| Service removed (regulated) | All of the above, treated as urgent. Advertising a service with no practitioner able to deliver it is an AHPRA breach, and an LHM client was reported and audited over exactly this in 2026. The live GBP is the priority, ahead of any site rebuild. |
| New location | Local SEO for new location, GMB listing, location-specific landing page |
| Contact details changed | Update website, GMB listing, ad extensions |
| Rebrand (logo/colours) | WordPress visual updates, ad creative refresh |

Present the relevant implications:
"This change has downstream implications:
- [Specific work item]: recommend running [skill]
- [Specific work item]: recommend running [skill]

Want me to queue any of these now?"

## Step 5: Confirm completion

"Update complete. [N] references updated across [M] files. Change logged in client_profile.md."

If this run was a handoff from `post-meeting-review`, this is not the end of the session. Hand control back so it can resume at its Step 4, and hold the Step 4 implications above so they can be merged into its Step 6 rather than presented twice.
