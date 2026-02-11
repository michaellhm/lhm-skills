---
name: client-update-email
description: "Generate a plain-language client update email after completing a task. Use this when the user mentions 'client update', 'update the client', 'email the client', 'client email', 'explain what we did', 'send a summary', 'client report email', or 'let the client know'. This skill takes the work just completed and turns it into a friendly, jargon-free email the client will actually understand."
---

# Client Update Email

You generate clear, friendly emails that explain to the client what was done and why — in plain language they'll understand. No marketing jargon. No filler. Just honest, helpful communication.

## Step 1: Gather Context

Use the `AskUserQuestion` tool to understand the situation:

1. **"What's the reason for this work?"** — options:
   - "Rankings dropped"
   - "Ad performance declined"
   - "Monthly review / routine check-in"
   - "Client requested changes"
   (plus Other for custom input)

2. **"What did we work on?"** — options:
   - "Google Ads optimisation"
   - "SEO / content changes"
   - "Analytics / tracking setup"
   - "Landing page / website changes"
   (plus Other for custom input)

Also check:
- Read `client_profile.md` for the client's name and contact context
- Look at any files created in the current session (recent outputs in the client folder) to pull specific details of what was done

If the user has just finished a skill or agent workflow in this session, use that context directly — don't make them repeat it.

## Step 2: Draft the Email

Write the email following these rules:

### Tone & Style
- **Friendly and direct** — like explaining to a smart friend who doesn't work in marketing
- **Plain language** — if a 10-year-old wouldn't understand a word, replace it
- **Not condescending** — simple doesn't mean dumbed down. Respect their intelligence, just don't assume they know the jargon
- **Short** — 150-300 words max. Clients are busy

### Structure

```
Subject: [What was done] — [Client Name] Update

Hi [First Name],

[1-2 sentences: Why we did this work. The trigger or reason.]

[2-4 sentences: What we actually did, in plain terms. Be specific but not technical.]

[1-2 sentences: What this should mean for them. The expected outcome, honestly stated — no promises, no hype.]

[Optional: 1 sentence on what's next or what to watch for.]

Happy to jump on a call if you'd like to talk through any of this.

Cheers,
[Sign-off]
```

### Words & Phrases to AVOID

Never use these — they're marketing clichés or weasel words that erode trust:

| Don't Say | Say Instead |
|-----------|-------------|
| "leverage" | "use" |
| "optimise" (to a client) | "improve" or "adjust" |
| "utilise" | "use" |
| "synergy" | just describe what works together |
| "moving the needle" | "making a difference" or be specific |
| "low-hanging fruit" | "quick wins" or "easy fixes" |
| "deep dive" | "closer look" |
| "circle back" | "follow up" |
| "touch base" | "catch up" or "check in" |
| "ROI" (without explaining) | "return on what you're spending" |
| "CPA" (without explaining) | "cost per lead" or "cost per enquiry" |
| "CTR" | "click rate" or "how often people click" |
| "ROAS" | "return on ad spend" — then explain: "for every $1 spent, you're getting $X back" |
| "We're excited to..." | just say what you did |
| "I wanted to reach out..." | just get to the point |
| "As per our conversation" | "As we discussed" or just skip it |
| "Please don't hesitate to..." | "Happy to chat if you have questions" |

### Acronyms Rule

If you must use a technical term, explain it in brackets the first time:
- "We adjusted your Google Ads bidding (how much you're willing to pay per click)"
- "Your bounce rate (how many people leave without doing anything) dropped from 65% to 48%"

### Honesty Rules

- **Don't oversell results** — "This should help" not "This will transform your business"
- **Don't hide bad news** — if something isn't working, say so plainly
- **Don't pad the email** — if we made one change, don't make it sound like ten
- **Give context for numbers** — don't say "CTR improved 0.3%" without saying whether that's good or not

## Step 3: Present & Refine

Present the draft email to the user. Ask:
- "Does this capture everything? Anything to add or change?"
- "Who should I address it to?" (if not clear from client_profile.md)

## Step 4: Save

Save to: `client_updates/YYYY-MM/client-update-YYYY-MM-DD.md` inside the client folder.

## Examples

### Good Example

> Subject: Google Ads adjustments — February update
>
> Hi Sarah,
>
> Your ad costs were creeping up this month while leads stayed flat, so we made some changes to get things back on track.
>
> We paused two campaigns that were spending money but not bringing in enquiries, and shifted that budget to the campaigns that are working well. We also added some negative keywords — these are search terms we don't want your ads showing for, like "free" and "DIY", which were wasting about $200/month.
>
> You should start seeing your cost per enquiry come down over the next 2-3 weeks. We'll keep an eye on it and let you know how it tracks.
>
> Happy to chat if you have any questions.
>
> Cheers,
> [Name]

### Bad Example (what NOT to write)

> Subject: Q1 Performance Optimisation & Strategic Realignment
>
> Hi Sarah,
>
> I wanted to touch base regarding the optimisation work we've been leveraging across your Google Ads ecosystem. We've conducted a deep dive into your campaign performance metrics and identified several low-hanging fruit opportunities to move the needle on your ROAS.
>
> We've optimised your bid strategies, refined your keyword targeting matrix, and implemented negative keyword protocols to enhance CTR and reduce CPA across all active campaigns.
>
> These strategic adjustments should synergistically drive improved conversion metrics and ROI moving forward.

## Related Skills

- **google-ads-monthly-review** — often triggers the need for a client update
- **seo-audit** — another common trigger for client communication
- **ga-dashboard** — data source for update emails
