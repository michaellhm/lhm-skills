---
name: social-reel
description: Create a narrated vertical reel from an approved topic, post or carousel using a script-and-audio review before Remotion production. Use when the user says "make a reel", "turn this post into a reel", "script and voice preview", or "build a narrated social video". Supports one consistent local synthetic voice, screenshot anonymisation, music and speed variants; does not publish or schedule posts.
---

# Social Reel

Prepare the words and an audible draft first. Let Michael finesse the message and delivery, then build a reel from the approved version. Do not spend a full video render on an unapproved script unless he explicitly requests a rough visual experiment.

## Context and destination

Read this skill's `LEARNED.md`, the plugin's `references/anti-ai-writing-guidelines.json` and `references/delivery-artifact-contract.md`. For client-specific work, also resolve the canonical client context using `references/obsidian-context-contract.md`. Reuse the verified social project and its editorial preferences when adapting an existing post. `weekly-social-carousel` owns backlog selection and carousel production; this skill owns the spoken adaptation and reel.

Save durable outputs under `<verified_work_root>/social-reel/YYYY-MM/YYYY-MM-DD-slug/`, or the established content structure in the user's verified social repository. Never use the plugin source/cache as the deliverable destination. The LHM pilot lives in a `reels/` project within `lhm-social`; discover and verify the checkout instead of assuming a particular user's absolute path.

## 1. Script and audible draft

- Read the actual source post, caption and relevant assets. Retain its useful advice, offer and audience. Adapt it for speech rather than reading slides aloud.
- Lead with a concrete clinic-owner problem or opportunity. Explain why the viewer should care, then give a practical test or next step. Use plain English, including appointment names that a non-practitioner understands.
- Numerical hooks must state their assumptions. For example, 100 monthly bookings with a 20% relative improvement is 120 bookings at the same traffic. Label it an illustrative example, not a client result or promise. Bookings are not necessarily new patients. Distinguish relative uplift from percentage-point change.
- Write `script.json` as an ordered array of scene narration strings, and a readable `script.md`. Treat the hook as part of the reviewed script, not an unreviewed addition at video-build time.
- Choose or reuse one voice. Generate a short sample before a full narration when the speaker is new. On Apple Silicon, the proven local option is Qwen3-TTS through MLX Audio. A voice-description request for an Australian accent is an audition, not a verified Australian preset. See [production recipes](references/production-recipes.md).
- Generate the complete audio draft using the same speaker reference throughout. Never independently design a new voice for every scene. Keep the reference audio's original transcript fixed even when the target script changes. Do not clone Michael's voice until he requests it and supplies/identifies his recording.
- Save `voice.json` with engine/model, voice identity, reference paths, reference transcript, seed and chosen playback rate. Save `audio-manifest.json` as `{"audio": ["audio/scene-0.wav", "audio/scene-1.wav"]}` in script order. For a single full narration, list that one file. The manifest lists raw narration; the reviewed playback rate lives in `voice.json`.
- Present the readable script and a playable audio draft at the proposed final pace. Michael preferred 1.5x for the pilot, but audition the current content rather than treating that rate as universal. Preserve natural pitch. State the estimated final duration.
- Return `awaiting_script_audio_approval`. Ask for feedback on wording, context, pronunciation, speaker consistency and pace. Continue script/audio refinements as requested. Do not treat silence as approval or ask again after the exact version has already been approved in the session.

## 2. Record approval and build

Record explicit approval of the current script, voice and audible draft in `approval.json`. Use the [review gate helper](scripts/review_gate.py), which binds approval to the script, audio bytes and voice settings:

```text
python3 <skill>/scripts/review_gate.py approve <package> --by Michael --note "Exact approval from the conversation"
python3 <skill>/scripts/review_gate.py check <package>
```

Run `approve` only after the human has approved that exact draft. The helper records evidence; it does not itself obtain consent. An explicit request to skip script review may be recorded as a scoped override using the human's actual wording, never inferred from a general request to create a reel.

After the check passes:

- Build a scene plan that maps every spoken section to a matching title, concise on-screen text, visual and timing. Preserve the approved meaning. Long sections can change their on-screen point during narration rather than displaying a paragraph throughout.
- Use Remotion, normally 1080 x 1920 with the source timeline at 30 fps. Read [production recipes](references/production-recipes.md). Reuse the existing project where appropriate; keep unrelated publishing/site logic intact.
- Measure actual audio lengths, add short breathing gaps, and derive scene durations from those files. Do not guess narration timings. Keep a source-speed master and make the approved final-speed export separately.
- Prefer visuals that demonstrate the advice: a cursor hesitating between appointment labels, a clearer choice, a booking journey reaching confirmation, or a relevant screenshot. Use a stronger animated hook before the instructional scenes when appropriate. Avoid generic decorative B-roll.
- Inspect screenshots before use. Remove clinic names, logos, phone numbers, domains, addresses, account details and other identifying data as needed. Use the available image-editing workflow for bitmap edits, save the anonymised asset in the project, and inspect the entire edited asset as well as the final crop. Never present modified UI or example figures as observed performance from the pictured clinic.
- Keep critical text clear of platform controls; preview on a phone-sized canvas. Carry LHM's existing navy/orange style unless a new direction is requested. Let animation guide attention, without making the advice hard to read.
- Add optional original or appropriately licensed music at a low level under narration, with a fade. Record provenance and any attribution requirements. "Free download" is not proof of commercial reuse rights. No paid service signup is required by default.

## 3. Review and delivery

- Inspect the opening, longest-text scene, screenshot crop and CTA, including representative animation frames. Check for clipping and identifiers. Verify spoken copy, brand pronunciation, audible endings, audio/video alignment and final duration. An automatic transcript is useful evidence but cannot establish accent quality or speaker consistency; disclose what still needs listening review.
- Save the final MP4 and open it inline or in the available preview. Return its real path and duration, plus the editable preview when available. Keep earlier approved exports for comparison.
- For visual-only feedback, preserve approved narration and render the changed scenes. For script, voice, reference, pronunciation or pace changes, regenerate the affected audio as needed and reopen script/audio review; the helper must reject stale approval. A request to make a specified revision and rebuild authorises that bounded rebuild without another confirmation. Record the exact new-version approval/override after preparing its audio.
- A speed-only request may be fulfilled by a pitch-preserving audio tempo change and uniform video retiming of the source master. Update the editable preview to match and verify stream durations. Never stack 1.5x onto an already accelerated 1.2x export when the request means 1.5x original speed.
- Save `delivery.json` with source topic, script approval digest, voice identity, scene plan, music/screenshot provenance, source and final durations, playback rate, QA results and verified artefact paths. No source screenshot, client recording, model cache or generated output belongs in the skill's Git source.

Social scheduling, publication, team messages, merging code and plugin installation are separate actions. Do not perform them merely because the reel is approved. A Desktop export is permitted when requested; sending it to a colleague requires an explicit send instruction.

## Posting advice when asked

Treat cadence as an experiment. A reasonable starting test is Monday carousel (saveable checklist) and Wednesday reel (spoken hook and demonstration) for four weeks. Do not encode this as an automatic schedule or claim those days are optimal. Make each format useful independently. Compare non-follower reach and retention for reels, saves/shares and profile visits across formats, plus relevant DMs/enquiries and production effort. Check current first-party platform guidance before asserting platform behaviour. If production capacity is tight, a reel-first test with selective carousels is reasonable; do not drop carousels solely because reels have more views.

## Structured handoff

Input:

```json
{"source_post":"verified path or supplied topic","work_root":"verified durable root","mode":"script_audio | build | revise","voice_reference":"optional authorised local file","playback_rate":1.5,"approval_evidence":"optional exact user message"}
```

Output:

```json
{"state":"awaiting_script_audio_approval | awaiting_visual_review | completed | blocked","package":"verified path","script_approval_digest":null,"duration_seconds":null,"artefacts":[],"qa":{"copy":"pending","privacy":"pending","audio":"pending","visual":"pending"},"publication":"not_requested","next_action":"Review the script and listen to the audio"}
```

Use `completed` only for the requested stage after required artefacts have been saved and read back. Script/audio review is a valid stage result, not a claim that a final reel exists.
