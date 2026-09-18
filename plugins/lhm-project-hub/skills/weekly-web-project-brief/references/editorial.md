# Email contract and portable template

Subject: Web projects | Week of <Monday date> | What needs moving this week
Sender display: Lily | LHM Web Projects. HTML newsletter layout with a real four-column table: Project / Where we're at / Target finish / What needs to happen next. Colour plus Red/Orange/Green text; inline CSS, no JavaScript, webfonts or remote image dependency. Plain-text MIME alternative required.

Use concise Australian English. Aim for a two-minute priority scan, with the full portfolio below. Do not suppress active projects to meet an arbitrary word limit. Summarise unchanged work; show material movement since last week. Do not fill owner sections with future hypothetical QA or repeat every row verbatim. Prefer a handful of real weekly priorities. Avoid patient/clinical detail unrelated to website delivery.

brief.json schema (all content plain text, no embedded HTML):
- week: ISO Monday YYYY-MM-DD; cutoff: human-readable evidence date/time.
- intro: string.
- priorities: list of strings.
- new_projects: list of strings, identifying kickoff/handover dates; empty produces “No new website projects this week.”
- projects: list of {name, url, light: red|orange|green, state, target, next}. Use verified https source links. Include owner in next. Order among equal lights is supplied by the researcher.
- owners: list of {name, actions: list of strings}; allowed names Michael, Kristalyn, Aiya, Jaimee, Josephine. Omit Josephine when no current dependency requires her.
- older_cards: list of strings, optional; identify actual remaining uncertainty, not allegations of inactivity.
- limitations: string, optional, only limitations affecting interpretation.

The renderer supplies legend, date explanation, feedback prompt and Lily sign-off. Week is immutable for a delivery receipt. Preview mode never sends. Rendering on another LLM uses the same JSON and Python standard library; the research instructions do not depend on a provider.

Regression cases from the 19 September review (examples only; refresh live evidence):
- A newer mhealth hold overrides old “build in progress” notes; retain missed target history.
- Smart Makeover's later sample-only scope overrides earlier bulk-copy instructions.
- Completed Dry Eye quiz child tasks must not become new work from stale parent notes.
- ASP prototype ready internally does not prove it was emailed or approved by David.
- Align live-site handover after cancellation must not be reported as unfinished construction.
- Your Story and Any Stage Pilates qualify as new handovers in the initial reporting window, not forever.
- A normal client review is orange; a confirmed stopped build is red. New approval without execution confirmation is orange, not automatically green.
