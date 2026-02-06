---
name: start
description: "Start a marketing work session. Use this when the user wants to begin working, asks 'what should I work on', mentions a client, or invokes /lhm-marketing-hub:start. This skill identifies the client, asks what they want to accomplish, and loads the right marketing skill."
---

# Start a Marketing Session

You are starting a new marketing work session. Follow these steps:

## 1. Identify the Client

Ask the user: **"Which client are we working on today?"**

Once they respond:
- Search the current working directory for a folder matching the client name (try the name as-is, lowercase, kebab-case, abbreviations)
- If found, confirm: "I found the folder at [path] - is that right?"
- If not found, ask where the client files are or offer to create a new folder

## 2. Ask What They Want to Work On

Ask: **"What do you want to work on today?"**

Then match their response to the best skill from the catalog below.

## Available Skills

### Google Ads & PPC
| Skill | Use When |
|-------|----------|
| **Ad Copy Generator** | Creating or refreshing responsive search ads (RSAs) |
| **Bid & Budget Optimizer** | Adjusting budgets, bid strategies, or spend control |
| **Keyword Optimizer** | Finding wasted spend, negative keywords, match types |
| **Landing Page Optimizer** | Auditing landing pages for conversions |
| **Monthly Strategy Session** | Start-of-month account review and zone analysis |
| **PMax Banner Generator** | Creating Performance Max banner assets |

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

## 3. Load the Skill

Once you know the task, read the matching SKILL.md from the plugin's skills directory:

`${CLAUDE_PLUGIN_ROOT}/skills/[skill-name]/SKILL.md`

Read the full SKILL.md file and any referenced templates or examples in the same skill folder.

Once loaded, follow that skill's instructions completely to help the user with their task. Save all output to the client's folder.
