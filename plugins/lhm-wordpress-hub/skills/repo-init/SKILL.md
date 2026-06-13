---
name: repo-init
description: "Set up Git repositories for a new client project. Use this when the user says 'set up the repo', 'init the client repo', 'create the client repos', 'initialise the project repo', 'set up GitHub for this client', 'create repos for [client]', 'new client repo', 'repo-init', or is starting a new client project and needs Git set up. Creates both <client>-site and <client>-prototype repos on GitHub, scaffolds the code repo's docs/ folder with context documents pulled from existing client files, and commits the initial scaffold."
---

# Repo Init

Automate first-time Git repository setup for a new client project. This implements Section 5 of the Client Repo Workflow SOP.

The rule: **Git syncs code. Drive syncs everything else. They never overlap.**

Repos must live at `~/Documents/Projects/<client>/` (Mac) or `C:\Users\<you>\Documents\Projects\<client>\` (Windows) — outside any Drive-synced folder.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-init/LEARNED.md`.

## Step 1: Verify Prerequisites

Run:

```bash
gh auth status
```

If this fails or returns "not logged in": **stop here**. Tell the user:

> "GitHub CLI is not authenticated. Run `gh auth login` and complete the auth flow, then come back and run repo-init again."

Do not continue until auth is confirmed.

## Step 2: Gather Details

Use `AskUserQuestion` with these three questions together:

**Question 1 — GitHub destination:**
> "Where should the repos be created? Enter the GitHub username or org name (e.g. `my-org` or `jaimee-lhm`). No hardcoded default — confirm per client."

(Free text — no preset options. Must ask every time.)

**Question 2 — Client slug:**
> "What's the client slug? This becomes the folder name and repo prefix (e.g. `woodlands-physio`, `sydney-dental`). Lowercase, hyphens only."

(Detect from `client_profile.md` YAML frontmatter `business_name` if present, but confirm with user.)

**Question 3 — Operating system:**
Options:
- Mac
- Windows

## Step 3: Confirm the Local Path — Drive Warning

Based on OS, show the target path:
- Mac: `~/Documents/Projects/<client>/`
- Windows: `C:\Users\<username>\Documents\Projects\<client>\`

Tell the user:

> "I'll create the client folder at `<path>`. This is outside Google Drive — required by the SOP. If your Documents folder is synced to Drive or OneDrive, the repos will corrupt. Confirm this path is outside Drive before proceeding."

Use `AskUserQuestion`:
> "Is `<path>` outside your Google Drive / OneDrive sync folder?"

Options:
- "Yes, it's outside Drive — proceed"
- "No / not sure — let me check"

If "No / not sure": stop and wait. Do not create anything until confirmed.

## Step 4: Create Local Client Folder

**Mac:**

```bash
mkdir -p ~/Documents/Projects/<client>
cd ~/Documents/Projects/<client>
```

**Windows** (run in PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\Projects\<client>"
Set-Location "$env:USERPROFILE\Documents\Projects\<client>"
```

## Step 5: Create Both GitHub Repos and Clone

Run these from inside the client folder. The `--clone` flag creates the repo on GitHub and clones it locally in one step.

**Mac/Linux:**

```bash
cd ~/Documents/Projects/<client>
gh repo create <destination>/<client>-site --private --clone
gh repo create <destination>/<client>-prototype --private --clone
```

**Windows:**

```powershell
Set-Location "$env:USERPROFILE\Documents\Projects\<client>"
gh repo create <destination>/<client>-site --private --clone
gh repo create <destination>/<client>-prototype --private --clone
```

If either `gh repo create` command fails (repo already exists, auth issue, etc.): stop and report the exact error. Do not continue.

After this step, the local structure is:

```
~/Documents/Projects/<client>/
  <client>-site/       ← cloned, empty
  <client>-prototype/  ← cloned, empty
```

## Step 6: Scaffold the Code Repo

Work inside `<client>-site/`.

### 6.1 Create folder structure

```
<client>-site/
  docs/
  skills/
  src/        ← placeholder for the codebase
```

**Mac:**

```bash
mkdir -p ~/Documents/Projects/<client>/<client>-site/docs
mkdir -p ~/Documents/Projects/<client>/<client>-site/skills
mkdir -p ~/Documents/Projects/<client>/<client>-site/src
```

### 6.2 Pull content from existing client files

Check whether the following files exist in the current working directory (where Claude Code is open — usually the client root in Drive or the existing project folder):

| Source file (existing) | Destination in repo |
|---|---|
| `client_profile.md` | `docs/client-overview.md` |
| `playbook.md` | `docs/playbook.md` |
| `design/brand_guidelines.md` | `docs/brand-style.md` |
| `design/design_system.md` | `docs/design-system.md` |

For each source file that **exists**: read it and write its full content into the destination file in the repo.

For each source file that **does not exist**: create the destination file with the starter template below.

### 6.3 Starter templates (use when source file is missing)

**`docs/client-overview.md`**

```markdown
# Client Overview — [Client Name]

> Who the client is, contacts, and project context. This document travels with the code — keep it current.

## Business

- **Name:**
- **Industry:**
- **Website:**
- **Primary contact:**
- **Phone:**

## Context

[Background on the client, their market, why they came to LHM.]

## Key Contacts

| Name | Role | Email | Phone |
|------|------|-------|-------|

## Notes

```

**`docs/playbook.md`**

```markdown
# Campaign Playbook — [Client Name]

> Brand voice, services, USPs, and tone. Source of truth for all copy and content decisions.

## Brand Voice


## Services


## USPs


## Tone of Voice


## Notes

```

**`docs/brand-style.md`**

```markdown
# Brand Style Guide — [Client Name]

> Colours, typography, logo usage. Shared with the client.

## Colour Palette

| Name | Hex | Usage |
|------|-----|-------|

## Typography

- **Heading font:**
- **Body font:**

## Logo

- Primary logo: (attach file or link to Drive)
- Usage rules:

## Notes

```

**`docs/design-system.md`**

```markdown
# Design System — [Client Name]

> Design tokens, spacing, component specs. Input for theme scaffold and prototype skills.

## Colour Tokens


## Typography Scale


## Spacing Scale


## Breakpoints


## Component Specs


## Notes

```

### 6.4 Create `skills/README.md` placeholder

```markdown
# Client-Facing Skills — [Client Name]

This folder holds lightweight skills for client use — for example, skills that help the client request content changes or update their profile. These skills reference the committed docs in `docs/` by relative path, so they work on any machine where the repo is cloned.

## Adding a skill

Create a subfolder with a `SKILL.md` file. Keep skills small and client-focused. The full LHM build pipeline lives in the marketplace, not here.

## Skills in this repo

(none yet)
```

### 6.5 Create `src/README.md`

```markdown
# Source Code

The website codebase lives here.

- **WordPress build:** theme files, blocks, and patterns go under `src/`
- **Astro build:** the Astro project root is `src/`

See `docs/design-system.md` for design tokens and `docs/client-overview.md` for project context.
```

### 6.6 Create `.gitignore`

```
# Dependencies
node_modules/
vendor/

# Build output
dist/
.output/
_site/
.astro/
.next/

# WordPress
wp-content/uploads/
*.sql
*.tar.gz
*.zip

# OS
.DS_Store
Thumbs.db
desktop.ini

# Editor
.idea/
.vscode/settings.json
*.swp
*.swo

# Env
.env
.env.local
.env.*.local

# Heavy assets — these belong in Google Drive, not Git
*.psd
*.ai
*.fig
*.sketch
*.mp4
*.mov
*.pdf
*.zip
raw-assets/

# Local config
wp-config-local.php
local-config.php
```

### 6.7 Create `README.md`

```markdown
# [Client Name] — Website

## Quick start

Clone this repo:

```bash
git clone https://github.com/<destination>/<client>-site.git
cd <client>-site
```

Context docs are in `docs/`. Read `docs/client-overview.md` first.

## Structure

```
docs/          Client context — overview, playbook, brand, design system
skills/        Lightweight client-facing skills
src/           Website codebase
```

## Working day to day

Pull before you start:

```bash
git pull
```

Push when you finish a piece of work. Commit messages: `feat:`, `fix:`, `docs:`, `chore:`.

Heavy assets (images, recordings, PDFs) stay in Google Drive — do not commit them here.
```

## Step 7: Initial Commit and Push — Code Repo

```bash
cd ~/Documents/Projects/<client>/<client>-site
git add .
git commit -m "chore: initial scaffold — docs, skills, src structure"
git push
```

**Windows** (substitute `Set-Location` and backslash paths as appropriate).

## Step 8: Initial Commit and Push — Prototype Repo

Create a `README.md` in the prototype repo:

```markdown
# [Client Name] — Prototypes

HTML/CSS prototypes for the [Client Name] website. One folder per page or ad group.

## Structure

Each prototype lives in its own folder:

```
homepage/
  index.html
  assets/
service-physio/
  index.html
  assets/
```

Prototypes are pushed here automatically by the `lp-prototype` and `html-prototype` skills.

## Installing

```bash
git clone https://github.com/<destination>/<client>-prototype.git
```
```

Then commit and push:

```bash
cd ~/Documents/Projects/<client>/<client>-prototype
git add README.md
git commit -m "chore: initial scaffold"
git push
```

## Step 9: Verify

Run:

```bash
gh repo view <destination>/<client>-site
gh repo view <destination>/<client>-prototype
git -C ~/Documents/Projects/<client>/<client>-site status
git -C ~/Documents/Projects/<client>/<client>-prototype status
```

Both should show as clean (nothing uncommitted). Both should be visible on GitHub.

Tell the user:

> "Both repos are live:
> - `github.com/<destination>/<client>-site` — code repo with docs/ scaffold
> - `github.com/<destination>/<client>-prototype` — prototype repo
>
> Local clones are at `~/Documents/Projects/<client>/`. Anyone else joining the project runs `repo-install` to clone their copy."

If you pulled content from existing `client_profile.md` or `playbook.md`, note which docs were populated vs which are stubs.
