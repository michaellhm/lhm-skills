# Healthstin homepage: personas and brief

Prepared by Local Health Marketing, October 2026. Working document behind the homepage prototype in this folder (`index.html`). Structure follows the approved proposed sitemap (`../../prospect-sitemap-opportunity/2026-10/`).

## Who actually lands on the homepage

Healthstin's homepage serves two very different groups: people choosing care for themselves or a family member, and professionals sending clients to them. Most of the first group arrive already knowing how they will pay (NDIS plan, aged-care package, DVA card, WorkCover claim or their own pocket). Funding decides the path far more than the service name does, so the homepage should let each visitor pick their situation in one click.

### 1. Karen, adult daughter arranging care for her mum

- **Situation:** Mum is 81, had a fall last winter and now has a Support at Home package. Karen works full time and is organising everything by phone and email.
- **Searches:** "physio home visit [suburb]", "falls prevention exercise elderly", "can I use support at home for physio".
- **Needs to see quickly:** that Healthstin comes to the house, which suburbs they cover, that the package can pay for it, and a real person to call.
- **Worries:** being sold something the package will not cover, unreliable visits, clinicians who rush older people.
- **What wins her:** clear aged-care funding path, home-visit coverage, reviews from other families, the phone number visible at all times.

### 2. Lisa, mum of a teenager with cerebral palsy (self-managed NDIS)

- **Situation:** Son Josh is 15. They self-manage the plan and have used three providers in four years.
- **Searches:** "NDIS physio cerebral palsy", "hydrotherapy NDIS [city]", "registered NDIS provider near me".
- **Needs to see quickly:** registered NDIS provider, condition experience (CP, autism, intellectual disability), pool and gym access, how invoicing works for self-managed plans.
- **Worries:** staff turnover, therapists who do not understand complex disability, waitlists.
- **What wins her:** condition pages, the pool-based clinics, the free 10-minute phone consultation to ask questions before committing.

### 3. Priya, NDIS support coordinator

- **Situation:** Carries 40+ participants across western Melbourne and needs reliable allied health partners who answer emails.
- **Searches:** rarely Google. She arrives from a colleague's recommendation or a provider list and goes straight for the referral form.
- **Needs to see quickly:** a referral button that is never more than one click away, coverage areas, which funding types are accepted, and proof other coordinators trust them.
- **Worries:** referrals that disappear, no progress updates, providers who cannot start quickly.
- **What wins her:** a dedicated referrer path, quotes from other support coordinators (Healthstin already has these), HealthLink and online referral options.

### 4. Dr Nguyen, GP (and DVA or WorkCover case managers)

- **Situation:** Writing a chronic disease management plan or a DVA referral and wants somewhere credible to send the patient.
- **Needs to see quickly:** credentials (ESSA accredited exercise physiologists, physiotherapists), the funding schemes accepted (Medicare, DVA, WorkCover), HealthLink.
- **What wins them:** professional presentation and accreditation logos, no marketing fluff.

### 5. Tom, 58, private patient after a knee replacement

- **Situation:** Discharged from hospital, surgeon suggested hydrotherapy, has private health cover.
- **Searches:** "hydrotherapy near me", "physio after knee replacement [suburb]", "physio or exercise physiologist".
- **Needs to see quickly:** the nearest clinic, whether there is a pool, private health rebates, how to book online.
- **What wins him:** location list, the physio vs exercise physiology explainer, online booking.

### 6. Graham, 74, DVA Gold Card holder

- **Situation:** Vietnam veteran wanting to stay strong and independent. Prefers to call.
- **Needs to see quickly:** that his Gold Card covers it, the phone number in large type, group classes or the pool.
- **What wins him:** the DVA path, plain language, a calm and respectful tone.

## What that means for the homepage

| Need | Who it serves | Homepage answer |
|---|---|---|
| Pick my situation in one click | Everyone | "How can we help?" selector straight under the hero: private patient, NDIS, aged care, referring a client |
| Phone and two actions always visible | Karen, Graham, Priya | Top strip: phone, Book an Appointment, Refer a Patient |
| Proof this is a serious, accredited organisation | GPs, coordinators, Lisa | Accreditation logo bar, scale figures (8 clinics, 4 states, 10,000+ clients) |
| What do you actually do | Tom, Lisa | Three disciplines, with the physio vs exercise physiology explainer kept from the current site |
| Where and how | Karen, Tom | Three ways we care: in our clinics (pools and gyms), in your home, online and in the community |
| Can my funding pay for it | Everyone except Priya | Getting started band: NDIS, Support at Home, DVA, WorkCover, Medicare, private health |
| Is my condition something you treat | Lisa, Tom | Conditions grid linking to condition pages |
| Do others trust them | Everyone | Google reviews plus quotes from support coordinators |
| Is there one near me | Tom, Karen | Clinics by state plus home-visit cities |
| I'm a professional, make it easy | Priya, Dr Nguyen | Dedicated referrer section with online referral, HealthLink and phone |

## Design direction

- **Tone:** ultra conservative, calm and established. It should read like a national provider with a board, not a start-up.
- **Style:** Trust and Authority pattern with an "I am a..." path selector (UI UX Pro Max: Trust & Authority, Enterprise Gateway). Strict grid, generous white space, thin rules, no gradients, no decorative animation.
- **Colour:** deep forest ink `#12301F` for headings and dark bands, primary green `#386A1F` for buttons and links (6.5:1 on white), Healthstin's brand green `#65CA48` used only as an accent on dark backgrounds, warm off-white `#F5F7F3` for alternate sections.
- **Type:** Lexend for headings (500 to 600 weight), Source Sans 3 for body at 17px. Both are designed for readability, which suits an older and disability audience.
- **Accessibility:** AA contrast throughout, visible focus states, 44px minimum targets, reduced-motion respected, no information carried by colour alone.

## Content kept from the current site

- Hero line "Movement is for everyone."
- Accreditation logos (NDIS, DVA, Medicare, ESSA, WorkSafe Victoria, ReturnToWork SA, WorkCover WA, aged care).
- Physio vs exercise physiology explainer, shortened.
- Figures already published on the site: 10,000+ lives improved, 10+ years, 260+ Google reviews rated Excellent.
- Google reviews and support coordinator quotes, trimmed but not reworded.

## Open questions for Healthstin

1. Photography: the current images are low resolution and inconsistent. The prototype uses their own photos at small sizes; a half-day shoot (pool, gym, home visit, team) would lift the whole site.
2. Online booking: is there a booking system (for example Cliniko or Splose) we can link to, or does "Book an Appointment" go to a form?
3. Referral turnaround: if Healthstin can commit to a response time for referrals, say so in the referrer section. The prototype makes no promise.
4. Bexley: confirm it is an active clinic so the count of eight is right.
5. Children: confirm whether paediatric work is offered before it appears in the conditions or audience copy.
6. Hurstville-only services: the Hurstville page lists cupping, gua sha and low-level laser therapy alongside remedial massage and acupuncture. None of these are in the proposed What We Do menu. Confirm which clinics offer them before giving them their own pages; the prototype mentions them as Hurstville services only.
7. Hero video: every existing video has burned-in captions or title cards. The prototype loops 8 to 20 seconds of the Nick and Bryce clip under a dark overlay as a placeholder. A 20 to 30 second clip of clean footage (pool, gym, home visit), shot without captions, would give the full-width video hero the look it needs.

## Colour update (October 2026, after first review)

Moved from forest green to Healthstin's own palette, taken from the live clinic pages and footer: charcoal `#161E1D` for headings, dark bands and footer, Healthstin green `#65CA48` as the accent on dark, a deeper green `#3B7D23` for buttons on white (5.1:1), their referral purple `#712C7C` for every Refer a Patient action, and neutral grey `#F1F2F3` for alternate sections.
