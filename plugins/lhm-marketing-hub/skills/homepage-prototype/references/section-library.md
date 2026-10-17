# Section library

Proven homepage sections, in the order that worked for a multi-location allied health provider. Pick what the personas brief calls for and reorder freely. `assets/healthstin-homepage-example.html` contains working code for every section; search it for the class names given here.

## Contents

1. Top strip and header
2. Hero
3. "How can we help you today?" path selector
4. Accreditation logo row
5. Our services
6. How you can access our services
7. Conditions or specialties (dark, tabbed)
8. Funding and getting started
9. What our clients say
10. Meet our team
11. For referrers (dark band)
12. Locations
13. Partners and recognition
14. Final call to action (full-width brand band)
15. Footer

---

## 1. Top strip and header (`.strip`, `header.site`)

- A dark strip above the header holds the phone number and the two primary actions (for example Book an Appointment and Refer a Patient). Keeping these out of the main bar gives the navigation room to breathe.
- Header: logo left, navigation right, sticky. Navigation labels and dropdown contents come straight from the approved sitemap.
- Mega menus for big groups (two or three columns with small group headings). Dropdowns in the right half of the bar should open leftwards so they never run off screen.
- Below about 1200px switch to a menu button with a full-width panel of collapsible groups.

## 2. Hero (`.hero-video`, `.hero-split`)

- Headline, one line of supporting copy, two buttons. Keep a strong existing line from the client if they have one.
- Full-width background video works well when the client has usable footage: dark gradient overlay on the text side, muted loop, pause button, still poster image, and no video for reduced-motion users.
- A split layout (copy left, photo right) is the alternative. When unsure, build both and add a small Video/Photo toggle in the prototype note bar so the client can compare.

## 3. Path selector (`.paths`)

- "How can we help you today?" with three or four cards, one per persona (for example private patient, NDIS, aged-care package, referring a client). Each card: icon, plain title starting "I'm…", one sentence, and a link to the right getting-started page.
- Keep all cards the same style. Mark a referrer card with an accent colour on its icon and link, not a dark background.

## 4. Accreditation logos (`.logos`)

- One quiet row of greyscale logos (schemes, professional bodies, regulators), full colour on hover. Logos come from the client's site.

## 5. Our services (`.svc`)

- Three photo-led cards, one per core discipline: photo (with a thin brand-colour line underneath), title, one-sentence description, four sub-service links, and an "About…" link.
- A single line underneath for secondary services ("Also available: …"), including any location-specific ones.

## 6. How you can access our services (`.ways`)

- Three cards for delivery modes, for example in clinic, home visits, telehealth and community. Real photos: the building, the branded car, a laptop on a video call.

## 7. Conditions or specialties (`.conditions`)

- Dark band. Left: heading, one sentence, and "Not sure if we can help?" with the phone number. Right: pill tabs for each group, with a list of links beside a matching photo.
- Tabs need proper roles, arrow-key support and a visible selected state.

## 8. Funding and getting started (`.funding`)

- Left: "Your first steps" card (numbered steps and one button). Right: a grid of funding pathway cards, each with small scheme logos, a title and one sentence.

## 9. What our clients say (`.rev`)

- Three verbatim reviews with stars and the platform name, plus the overall rating badge. Trim long reviews with an ellipsis; never reword them.

## 10. Meet our team (`.team`)

- One horizontally scrolling row of clinician cards (photo, first name, role), arrows that scroll by most of the visible width, and a "Meet the full team" link. Clinicians only; leave out admin and marketing staff. If two people share a first name, add an initial.

## 11. For referrers (`.referrers`)

- Dark band with a short list of what referrers get, two buttons (refer online, the client's referral system), and one or two quotes from referrers.

## 12. Locations (`.loc-layout`)

- Clinics grouped by state in two columns, each with the venue name; a side card for home-visit areas with "Check your suburb".

## 13. Partners and recognition (`.partners`, `.awards`)

- A partner quote beside a grid of partner logos.
- Awards as a carousel by year: year chips, arrows, each slide showing the award graphics with a short list of what was won. No autoplay. Read the award details off the graphics carefully and flag them for the client to confirm.

## 14. Final call to action (`.final`, `.cta-band`)

- Full-width band in a brand-colour gradient (dark enough for white text), the team cut-out breaking out of the top edge, a plain heading ("Talk to our team"), one sentence, the two primary buttons and the phone number.

## 15. Footer

- The client's dark neutral, four or five link columns that mirror the main navigation, contact details, an acknowledgement of country for Australian clients, and legal links.
