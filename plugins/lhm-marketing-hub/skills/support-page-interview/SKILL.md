---
name: support-page-interview
description: Guide a clinician through website support-page questions and save resumable local Markdown files, one per page, for a ZIP handback to their website team. Use when asked to interview a clinician for support pages, capture clinical website content locally, or resume a support-page interview.
---
# Support page interview

Help the clinician explain their work in their own words. This runs on the clinician’s computer, independently of LHM accounts, plugins or connectors. It collects source material for review, not approved website copy or patient advice.

## Start or resume

Read [interview flow](references/interview-flow.md). If the supplied client pack is Wellness On The Lane, read [the WOTL pack](references/wotl-pack.md), including its bundled Children-page flow. For another practice, ask for its reference page or local copy and its page list; do not reuse WOTL facts.

Ask the clinician to select a local output folder, using an already granted folder when available. Use `<selected folder>/support-page-interview/`; never write to global settings or install skills there. Explain that the answers stay in local files, while messages typed or dictated into their AI app are still processed by that app. No patient details are needed.

If a bundle exists, read `00-index.md` and the chosen page before asking questions. Show progress and offer the next unanswered question or another page. Never restart, replace existing answers, or initialise over a bundle. If file access is unavailable, explain that automatic saving cannot work in this session and offer downloadable Markdown; do not claim local files were saved.

For a new WOTL bundle, initialise from [the page list](assets/wotl-pages.json) using the optional standard-library helper:

`python3 scripts/local_bundle.py init --root "<selected folder>/support-page-interview" --pages assets/wotl-pages.json`

Resolve scripts/assets relative to this skill’s directory. If Python is unavailable, create the same Markdown structure directly using [page template](assets/page-template.md). The page list is a proposed interview backlog from prototype navigation, not an approved build scope or evidence those services are offered. Let the clinician rename, skip or add pages. Start with Children unless they choose otherwise.

## Interview and save

Ask **one question at a time**; allow voice, rough notes, skipping, correction and breaks. Work through the page’s flow, adapting child/parent wording for adults, teens or professional audiences. Do not force a fixed question count or invent answers. Use a short follow-up when a detail affects clinical accuracy or a reader’s next step.

After every substantive answer, save it under `## Interview notes` with the question and clinician’s words (lightly remove dictation noise without changing meaning). Update the summary sections, `Status`, `Next question` and index. Preserve earlier answers; record material corrections explicitly. Write through a temporary sibling file then replace the original, and read back to verify. A failed save must be disclosed immediately; preserve the answer in chat until saving is restored. Do not say “saved” based on a tool call alone.

Keep three things distinct: clinician-confirmed facts, editorial wording proposed by the assistant, and unresolved details. Leave unknown details under `Needs confirmation`, naming an owner only if known. Never fill gaps from generic medical knowledge or another clinician’s answers.

Use fictional/general patterns only. If identifiable patient information appears, do not repeat or write it into files; ask for a general description with identifiers removed. Avoid names, initials, exact dates or a distinctive combination of details. Do not collect patient records or attachments.

On “pause”, save progress and tell them which page/question resumes next. On “continue”, reread disk state first. On “finish this page”, show a concise summary and unresolved questions, ask whether it accurately reflects their answers, and mark it `Reviewed by clinician` only after an explicit yes. Partial pages remain `In progress`; unanswered questions are not refusals or invented answers. Clinician review confirms the brief, not clinical/legal approval of future website copy or publication.

## Finish and hand back

When asked to finish/export, save current progress and show which pages are reviewed, partial or not started. Include partial work if requested; never call the whole bundle complete unless all selected pages are reviewed or deliberately skipped. The index names any deliberately excluded pages.

Export only `00-index.md` and the page Markdown files listed there. With the helper:

`python3 scripts/local_bundle.py export --root "<selected folder>/support-page-interview"`

The helper creates a separate ZIP beside the output folder without modifying originals. Inspect the ZIP listing and verify files match disk. Never zip the entire workspace, chat history, hidden files or source/reference skill files. Manual ZIP is fine if no Python: select only the index and named page files. Tell the clinician where it is and that they can send it to Michael through their usual channel. Do not email, upload, publish or connect accounts automatically.
