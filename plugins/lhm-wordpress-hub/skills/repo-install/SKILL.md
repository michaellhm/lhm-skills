---
name: repo-install
description: "Clone a client project repository onto a new machine or for a new team member. Use this when the user says 'install the repo', 'clone the client project', 'set up my machine for [client]', 'pull down the client repo', 'clone the repos', 'install the client site locally', 'get the client repo', 'repo-install', or needs to access a client project that already has repos set up. Sets up the correct local folder structure and clones the code and/or prototype repos. Also use when someone already has the repo and just needs to pull the latest."
---

# Repo Install

Clone a client project repository onto a machine, or pull the latest if the repo already exists. This implements Section 6 of the Client Repo Workflow SOP.

The rule: repos must live at `~/Documents/Projects/<client>/` (Mac) or `C:\Users\<you>\Documents\Projects\<client>\` (Windows) — outside any Drive-synced folder.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-install/LEARNED.md`.

## Step 1: Gather Details

Use `AskUserQuestion` with these questions:

**Question 1 — Operating system:**

Options:
- Mac
- Windows

**Question 2 — Which repo(s) do you need?**

Options:
- "Code repo only (`<client>-site`)"
- "Prototype repo only (`<client>-prototype`)"
- "Both"

**Question 3 — Client slug and GitHub destination:**
> "What's the client slug and the GitHub username/org where the repos live? (e.g. client: `woodlands-physio`, destination: `lhm-digital`)"

(Two fields — detect from context if obvious, but confirm.)

## Step 2: Set the Local Path

Based on OS:

| OS | Path |
|----|------|
| Mac | `~/Documents/Projects/<client>/` |
| Windows | `C:\Users\<username>\Documents\Projects\<client>\` |

Warn before creating:

> "Repos will be cloned to `<path>`. This must be outside Google Drive and OneDrive. If your Documents folder is cloud-synced, stop and choose a different location."

## Step 3: Clone or Pull

### 3a — Check if the repo already exists locally

Check whether `<path>/<client>-site` and/or `<path>/<client>-prototype` already exist as Git repos.

**If the folder exists and is a Git repo:** do a pull, not a re-clone.

```bash
# Code repo — pull
cd ~/Documents/Projects/<client>/<client>-site
git pull

# Prototype repo — pull
cd ~/Documents/Projects/<client>/<client>-prototype
git pull
```

**Windows:**

```powershell
Set-Location "$env:USERPROFILE\Documents\Projects\<client>\<client>-site"
git pull
```

Tell the user: "Repo already cloned — pulled latest. If you need a fresh clone, delete the folder first."

### 3b — If the folder does not exist: clone

**Mac:**

```bash
mkdir -p ~/Documents/Projects/<client>
cd ~/Documents/Projects/<client>

# Clone code repo (if requested)
git clone https://github.com/<destination>/<client>-site.git

# Clone prototype repo (if requested)
git clone https://github.com/<destination>/<client>-prototype.git
```

**Windows:**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\Projects\<client>"
Set-Location "$env:USERPROFILE\Documents\Projects\<client>"

# Clone code repo (if requested)
git clone https://github.com/<destination>/<client>-site.git

# Clone prototype repo (if requested)
git clone https://github.com/<destination>/<client>-prototype.git
```

If clone fails (permission denied, repo not found): report the exact error. Common causes:
- Not authenticated: run `gh auth login` or `git credential` setup
- Wrong repo name or destination: double-check the slug and org name
- Repo not yet created: run `repo-init` first

## Step 4: Verify

For the code repo, check that the four context docs came down:

```bash
ls ~/Documents/Projects/<client>/<client>-site/docs/
```

Expected files:
- `client-overview.md`
- `playbook.md`
- `brand-style.md`
- `design-system.md`

If any are missing: the repo may not have been scaffolded yet. Tell the user to check with whoever ran `repo-init`.

**Windows:**

```powershell
Get-ChildItem "$env:USERPROFILE\Documents\Projects\<client>\<client>-site\docs"
```

## Step 5: Confirm

Tell the user:

> "Install complete. Local path: `~/Documents/Projects/<client>/`
>
> Repos cloned:
> - `<client>-site` ✓ — docs/ context files verified
> - `<client>-prototype` ✓ (if requested)
>
> In Claude Code, open `~/Documents/Projects/<client>/<client>-site` as your working directory to start a session. The context docs in `docs/` load automatically because they're in the repo."

If this was a pull (not a clone), confirm: "Pulled latest — you're up to date."

## Working from Here

Once installed, Claude Code sessions should be opened with the **code repo** (`<client>-site`) as the working directory. The context docs in `docs/` are committed with the code, so Claude has the full client context without a Drive hookup.

Before each session: `git pull` to get the latest. After each session: `git push` so the team sees the changes.
