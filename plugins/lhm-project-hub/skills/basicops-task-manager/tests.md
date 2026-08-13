# Acceptance tests

## Direct Michael task

Prompt: `Create a task in Michael's BasicOps to review whether Alpha's new Hawthorn location is included in the website scope.`

Expected:

- Title: `Alpha: Website - Review Hawthorn location scope`
- Michael Tasks / INBOX / Michael
- Blank description
- Human discussion beginning `Michael, we need to…` and ending with the Kristalyn handoff
- No invented due date
- Duplicate search, read-back and verified URL

## Context-heavy source

Prompt contains sitemap versions, scope implications, dependencies and acceptance tests.

Expected: preserve useful detail in Hermes/project context; do not place it in the title or description. Discussion remains under 100 words.

## Team assignment during pilot

Prompt: `Create a task for Kristalyn to coordinate Alpha's five-page copy batch.`

Expected: prepare the exact task and request Kristalyn's explicit approval before assignment unless the canonical workflow records graduation for this routine task type.

## Duplicate request

Repeat an already-created task request with different wording.

Expected: find the materially equivalent open task and return its URL without creating another.

## Unknown client label

Prompt names a client with no recorded abbreviation.

Expected: inspect canonical client context or existing BasicOps tasks; never invent an abbreviation.

## Reference URL

Prompt includes a Fathom or staging URL.

Expected: description contains only the useful URL; context and next handoff remain in discussion.
