# Readiness and learning rules

## Brief readiness

A brief is `ready` only when the assignee can begin without guessing a material fact and the completion/review path is clear.

| Check | Ready when | Typical response when missing |
|---|---|---|
| Outcome | A concrete end state is stated | Ask requester what must be true when finished |
| Owner fit | Canonical role supports the work | Confirm or propose the correct owner |
| Client/project | Correct active context is resolved | Ask client; then read current projects |
| Destination | Exact site/page/account/file/environment is known | Ask for URL or destination |
| Access | Access is confirmed or a named person will verify/grant it | Create no execution task until resolved when blocking |
| Inputs | Required source communication/assets are present | Ask requester, team or client as appropriate |
| Dependencies | Required approvals/decisions/upstream work are evidenced | Stop at the gate |
| Authority | Requester and assignee may perform the proposed step | Escalate scope/strategy/cost/production action |
| Completion | An observable verification exists | Define a simple check |
| Next handoff | Reviewer/recipient and channel are known | Ask who receives it next |
| Timing | Explicit date exists or is safely unset | Never invent a due date |

Not every task needs every field in BasicOps. Readiness is checked in Hermes; BasicOps remains concise.

## Common work-type prompts

Use these only as diagnostic prompts, not mandatory boilerplate.

### Website or design change

- Current page/site/staging URL
- Source request or approved design/content
- Exact change and exclusions
- CMS/repository/hosting access confirmation
- Staging versus production destination
- Desktop/mobile check
- Review owner and publish/deploy authority

### SEO, GMB or content

- Page/profile/document URL
- Target service/location/topic and approved direction
- Evidence or source data
- Client/AHPRA constraints where applicable
- Draft, staging or publish boundary
- Review/approval owner

### Client administration or platform task

- Exact client/system/account
- Access confirmation and access owner
- Source request/evidence
- Expected record or outcome
- Whether the task communicates or commits anything externally
- Follow-up owner

## Learning classification

### One-off task or client fact

Use when feedback applies only to this task/client/version. Correct the brief/task if authorised and write the verified fact to the canonical client/project record when it must persist.

### Person preference

Use when the assignee states what they need in briefs they receive. Record source and date under their `## Handoff preferences`. Do not infer a preference from silence or from someone speaking for them.

Suggested format:

```markdown
## Handoff preferences

- Website-change briefs should include the current page or staging URL. — confirmed by Aiya, YYYY-MM-DD
```

### Candidate process requirement

Use when feedback appears useful across people or clients. Record it as `Observe again` with occurrence count and dated source. Promote only after Michael explicitly approves it or the same material lesson occurs in at least two independent sessions.

### Contradiction or authority change

Do not overwrite silently. Preserve both positions and identify the decision needed. Route to Michael only for strategy, scope, commercial, role-authority or unresolved cross-team conflict.

## Feedback response

Respond compactly:

```markdown
Got it. I have:
- corrected: <current handoff change>
- recorded: <person/client fact, if authorised>
- observing: <candidate wider rule, if any>

Next time I will <specific behaviour>.
```

