# Editorial strategy

## Audience and promise

The primary audience is allied-health practice owners. Every carousel should help them make a clearer marketing, booking, website, advertising, or operational decision.

The feed should feel current without becoming a technology-news feed. A topic earns a carousel when it passes this question:

> What can a practice owner understand, decide, or do differently after reading this?

## Four content lanes

### Practice question

Use an anonymised question or misconception found in a real meeting. The source is private context, not part of the public story.

Suggested flow: the issue, the short answer, the common misunderstanding, what matters instead, practical takeaway.

Do not use public framing such as `a client asked`, `a clinic owner asked`, `we discussed this in a meeting`, or `one of our clients`. Lead with the audience's problem directly. Use the internal lane value `practice-question`.

### Practical shortcut

Use a recurring operational or marketing problem seen across clinics.

Suggested flow: the friction, why it keeps happening, the simpler approach, a short implementation checklist, next step.

### Search and Ads update

Use a verified Google Search, SEO, Analytics, or Google Ads development.

Suggested flow: what changed, what it means for clinics, who should care, what to do now or what to watch.

Avoid feature summaries that do not change a decision.

### AI experiment

Use a current AI capability or tool with a concrete clinic workflow.

Suggested flow: the task, what the tool can do, where it saves time, its limitation, whether it is worth testing.

Reject novelty without practical value.

## Weekly selection

Apply the privacy gate first. Score only safe candidates from 0-4 on:

- audience relevance
- audience frequency
- practical value
- specificity
- freshness
- carousel clarity

Maximum score: 24. A candidate should normally score at least 18 and no criterion should score 0.

Score audience frequency by asking how often an allied-health practice owner is likely to face the situation:

- `4`: common across most clinics or encountered repeatedly across meetings
- `3`: common for a substantial segment of clinics
- `2`: occasional but broadly recognisable
- `1`: rare, specialised or dependent on an unusual business structure
- `0`: no credible practice-owner use case

Hold a meeting-derived candidate with a frequency score below 2 in the backlog unless Michael explicitly selects it. High consequence alone does not make a rare topic broadly useful. Use editorial judgment when candidates are close. Lane rotation is a tiebreaker, not a reason to publish a weak topic.

Weekly selection considers the full ready backlog. A useful idea can be selected weeks after the source conversation. Record the score and selection status so an unselected topic is not lost or repeatedly rediscovered.

## Testing plan

Start with an eight-post test:

- publish each lane twice
- give each lane one typography cover and one image-led cover
- keep internal slide styling and publishing cadence stable
- compare saves, shares, completion, qualified profile visits, and enquiries

Do not change the topic lane, cover system, caption style, and CTA all at once. Record the lane and cover variant in `manifest.json` so later analysis can separate them.

## Writing constraints

- 5-7 slides
- one idea per slide
- cover hook: ideally 6-16 words, maximum 22
- non-cover headline: maximum 16 words
- body copy: normally 8-32 words
- caption: add context, do not transcribe the carousel
- public copy must not mention clients, meetings or transcript provenance
- use Australian English
- use no em dashes
- avoid inflated urgency labels such as `BREAKING` unless the timing is verified and the change is genuinely consequential
