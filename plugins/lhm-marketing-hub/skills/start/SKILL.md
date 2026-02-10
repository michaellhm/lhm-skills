---
name: start
description: "Start a marketing work session. Use this when the user wants to begin working, asks 'what should I work on', mentions a client, or invokes /lhm-marketing-hub:start. This skill runs the pre-flight check, identifies the client, loads their profile, and routes to the right skill."
---

# Start a Marketing Session

Follow these steps in order. Do not skip steps.

## 1. Pre-flight — Verify Clients Folder

Check whether the current working directory contains multiple client-named folders.

- The Clients root folder is **dynamic** — do not assume a fixed path
- If you can see client folders, narrate: "I can see X client folders."
- If you cannot: say "I can't see any client folders. Please navigate to your Clients directory." and **stop**

## 2. Select & Validate Client

Ask: **"Which client are we working on today?"**

Once the user responds:
- Search for a matching folder (try: as-is, lowercase, kebab-case, abbreviations)
- **If found**: confirm it
- **If not found**: create the folder and run the client-onboarding skill

### Onboarding Triggers

Run onboarding (read `${CLAUDE_PLUGIN_ROOT}/skills/client-onboarding/SKILL.md`) when:
- The client folder was just created
- `client_profile.md` does not exist
- `client_profile.md` exists but is empty

Onboarding **never overwrites** existing content. It only appends or enriches.

## 3. Load Client Context

- Read `client_profile.md` from the client folder
- Treat it as authoritative context for all downstream skills
- Do not re-ask for information already present
- Narrate: "Client profile loaded."

## 4. Ask What to Work On

Ask: **"What are we working on today?"**

Match the response to the skill catalog below. If multiple skills match, list options and let the user choose. If nothing fits, say so. **Do not invent skills.**

## Available Skills

### Google Ads & PPC
| Skill | Use When |
|-------|----------|
| **Ad Copy Generator** | Creating or refreshing responsive search ads (RSAs) |
| **Bid & Budget Optimizer** | Adjusting budgets, bid strategies, or spend control |
| **Keyword Optimizer** | Finding wasted spend, negative keywords, match types |
| **Landing Page Optimizer** | Auditing landing pages for conversions |
| **Google Ads Monthly Review** | Account health check and AdPulse zone analysis |
| **PMax Banner Generator** | Creating Performance Max banner assets |

### Strategy & Research
| Skill | Use When |
|-------|----------|
| **Competitive Analysis** | Evaluating competitors, Porter's 5 Forces, market positioning |
| **Keyword Research** | Finding keyword opportunities, intent analysis, topic clusters |

### SEO & Content
| Skill | Use When |
|-------|----------|
| **Content Gap Analysis** | Finding keyword, topic, and content format gaps vs competitors |
| **SEO Content Writer** | Writing SEO-optimized blog posts, guides, and articles |
| **GEO Content Optimizer** | Optimizing content for AI citations and generative engines |
| **Meta Tags Optimizer** | Creating title tags, meta descriptions, OG and Twitter tags |
| **Content Quality Auditor** | Running a full CORE-EEAT 80-item quality audit |
| **Content Refresher** | Identifying and refreshing underperforming content |

### Analytics & Reporting
| Skill | Use When |
|-------|----------|
| **GA Event Config** | Setting up GA4 property, classifying events and conversions |
| **GA Dashboard** | Generating analytics dashboards with period comparison |

### SaaS & Growth Marketing
| Skill | Use When |
|-------|----------|
| **A/B Test Setup** | Planning or implementing experiments |
| **Analytics Tracking** | Setting up or auditing GA4/GTM tracking |
| **Competitor Alternatives** | Creating comparison/alternative pages |
| **Content Strategy** | Planning what content to create |
| **Copy Editing** | Improving existing marketing copy |
| **Copywriting** | Writing new marketing copy for any page |
| **Email Sequence** | Creating drip campaigns and email flows |
| **Form CRO** | Optimizing lead capture and contact forms |
| **Free Tool Strategy** | Planning free tools for lead gen |
| **Launch Strategy** | Planning product launches |
| **Marketing Ideas** | Generating marketing strategies and ideas |
| **Marketing Psychology** | Applying behavioral science to marketing |
| **Onboarding CRO** | Improving post-signup activation |
| **Page CRO** | Increasing conversions on any page |
| **Paid Ads** | Running campaigns on Google, Meta, LinkedIn |
| **Paywall/Upgrade CRO** | Optimizing in-app upgrade flows |
| **Popup CRO** | Creating effective popups and modals |
| **Pricing Strategy** | Pricing decisions and packaging |
| **Product Marketing Context** | Creating product marketing docs |
| **Programmatic SEO** | Scaling SEO pages with templates |
| **Referral Program** | Building referral/affiliate programs |
| **Schema Markup** | Adding structured data to sites |
| **SEO Audit** | Diagnosing SEO issues |
| **Signup Flow CRO** | Optimizing registration flows |
| **Social Content** | Creating social media content |

## 5. Load the Skill

Read the matching SKILL.md from:

`${CLAUDE_PLUGIN_ROOT}/skills/[skill-name]/SKILL.md`

Read any referenced templates or examples in the same skill folder.

### Output Folder Structure

For every skill execution, enforce this inside the client folder:
1. Create a skill-specific folder: `google_ads/`, `pricing/`, `seo/`, `content/`, etc.
2. Inside it, create a date-based subfolder: `YYYY-MM` (e.g. `google_ads/2026-02/`)
3. Save all outputs there
4. Formats: `.md` for analysis, `.csv` for data, `.json` for structured output
5. **Never overwrite** — version files if needed

Follow the skill's instructions completely.
