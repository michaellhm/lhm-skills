# Privacy rules for meeting-derived content

## Default position

The useful idea can leave the meeting. The identity and confidential context cannot.

Client-derived content is private source material. Access to a transcript does not authorise publication of its details.

## Never expose without explicit permission

- client, clinic, practitioner, patient, staff, supplier, or referrer names
- locations or combinations of facts that identify the clinic
- patient stories, symptoms, diagnoses, treatment details, or appointment records
- revenue, budgets, conversion rates, booking volumes, targets, account data, or private performance figures
- staffing, conduct, ownership, contractual, legal, or financial matters
- passwords, account identifiers, screen captures, meeting recordings, or transcript excerpts
- unannounced plans, internal disagreements, or personal commentary

## Safe transformation

- paraphrase the question and preserve its commercial meaning
- generalise the setting to `a clinic owner` or `a practice owner`
- remove client-specific numbers, systems, suburbs, practitioners, and timing
- combine recurring patterns only when no single client can be inferred
- keep the original meeting URL and timestamp in `source-receipt.private.json`, never in public slide or caption copy

Do not assume that removing a name makes content anonymous. Consider whether the remaining details identify the speaker to staff, patients, competitors, or other clients.

## Privacy gate

Mark a candidate `unsafe` and discard it when:

- the lesson depends on sensitive details
- useful meaning is lost after anonymisation
- the statement could embarrass, disadvantage, or misrepresent the client
- it contains health information or could be read as a patient testimonial
- the speaker's permission would be required to publish a direct quote

When uncertain, do not publish the candidate. Record a generic topic suggestion without the source detail or choose another idea.

## Final inspection

Check slide copy, caption, filenames, HTML title and metadata, image metadata, alt text, manifest fields, and public source note. The private source receipt must have a `.private.json` suffix and must be excluded from any public deployment.
