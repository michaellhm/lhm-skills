# {{client_name}} website

You are an AI assistant. This repo is the website and the knowledge base for {{client_name}}. Read this file, then read `brain/Overview.md`.

## What is here

- `brain/` what we know about the client and how their copy should be written
- `site/` the Astro website (Cloudflare Pages builds from this folder)
- `skills/` the skills you can run: start-website, review-website, share-preview, finish-review

## Before you start

Install Git, Node (the version in `site/package.json`) and Python 3.10 or newer.

Mac (Terminal):

    git clone https://github.com/OWNER/{{client_slug}}.git ~/Documents/Projects/{{client_slug}}
    cd ~/Documents/Projects/{{client_slug}}/site && npm install && npm run dev

Windows (PowerShell):

    git clone https://github.com/OWNER/{{client_slug}}.git $env:USERPROFILE\Documents\Projects\{{client_slug}}
    cd $env:USERPROFILE\Documents\Projects\{{client_slug}}\site; npm install; npm run dev

Replace OWNER with the GitHub owner of this repo.

## Your assistant

- ChatGPT: open this repo in the Codex app. It reads `AGENTS.md`. Plain ChatGPT chat in a browser cannot open a repo.
- Claude: open this folder in Claude Code or Claude desktop. It reads `CLAUDE.md`.
- Gemini: run `gemini` in this folder (Gemini CLI). It reads `GEMINI.md`.

Then say "start website". Skills live in `skills/`.

## Rules

- Read `brain/Overview.md` before any content work, and follow `brain/Content Rules.md` when writing.
- Never paste passwords or tokens into chat.
