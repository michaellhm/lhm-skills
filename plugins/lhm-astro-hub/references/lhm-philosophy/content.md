---
title: LHM Content Philosophy
description: How LHM thinks about content production. Read at the start of every content session.
---

# LHM Content Philosophy

## Interview before writing

Never produce a word of content without first understanding:
- What are we writing and why?
- Who is the audience and what do they already know?
- What action do we want them to take after reading?
- What does the client want to say vs what does the audience need to hear?

Ask these questions even if the user thinks they've already answered them. Vague briefs produce vague content.

## Research before brief

After the interview, offer research options before writing the brief:
- "Want me to run keyword research to find the right angle for this?"
- "Want me to run TAYA question discovery to find the questions this needs to answer?"
- "Want me to research this topic to find facts, stats, and expert positions we can cite?"

Do not skip research and go straight to the brief. Research-backed content ranks and converts better. AI-generated content with no research is slop.

## Brief before writing

A structured brief is generated and confirmed before any writing begins. No exceptions.

The brief must include: target keyword and intent, content type, target word count, target audience, key questions to answer, internal links to include, external sources to cite, client voice notes from `client_profile.md`, and the specific goal (rank for X, convert visitors to Y, answer the question Z).

Get the user to approve the brief before proceeding.

## 8-pass pipeline with multi-model routing

All content over 300 words goes through the 8-pass engine. Passes are split across models by role:

- **Pass 1 (research synthesis):** Gemini 2.5 Pro via OpenRouter (`google/gemini-2.5-pro`) — strongest at grounding and factual recall. Pass it the research gathered in the pre-brief phase and ask it to synthesise the key points, stats, and angles.
- **Passes 2-7 (outline, drafts, burstiness, perplexity, human bookends, conversion injection):** Claude — maintain voice consistency during the core writing phase.
- **Pass 8 (final QC):** GPT-4o via OpenRouter (`openai/gpt-4o`) — fresh eyes, different bias. Prompt: "Review this content for AI writing patterns, factual claims that need verification, weak CTAs, and any structural issues. Be critical."

Never generate long-form content in a single pass regardless of model.

## Anti-AI writing

All output enforces the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`. Read this file before any writing pass.

## Second opinion

After the brief is approved and before writing begins, offer:
"Want a second opinion on this brief before we write?"
