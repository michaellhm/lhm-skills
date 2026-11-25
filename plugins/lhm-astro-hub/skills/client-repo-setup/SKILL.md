---
name: client-repo-setup
description: "Create the single GitHub repo for a new Astro website client and scaffold it with README.md, brain/, skills/ and site/. Use this when the user says 'set up the repo', 'create the client repo', 'init the client repo', 'new client repo', 'set up GitHub for this client', 'client-repo-setup', or is starting a new Astro website project. Runs at project start, before the prototype, because the brand style guide is written into brain/ at the prototype stage. Creates one private repo named after the client slug, never a separate prototype repo, and refuses to overwrite anything that already exists."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill's narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.

# Client Repo Setup

Create the one GitHub repo a client's whole website project lives in, and scaffold it.

```
<client-slug>/
  README.md              written for an AI assistant
  AGENTS.md CLAUDE.md GEMINI.md   short pointers for ChatGPT (Codex), Claude and Gemini
  brain/                 ten notes: Overview, Profile, Project, Services, Staff,
                         What We Do, Who We Serve, Brand, Content Rules, Change Log
  skills/                the client's own skills (installed later)
  site/                  the Astro website (Cloudflare Pages builds from here)
```

One repo holds both the brain and the site, so the client's AI project needs one GitHub connection. Run this at project start, before the sitemap and prototype.

The rule: **Git syncs code. Drive syncs everything else. They never overlap.** The repo lives at `~/Documents/Projects/<client>/<slug>/` (Mac) or `C:\Users\<you>\Documents\Projects\<client>\<slug>\` (Windows), outside any Drive-synced folder.

## Before Starting

Read `LEARNED.md` in this skill folder and apply any entries.

## Step 1: Check GitHub access

```bash
gh auth status
```

If it fails or says not logged in, stop. Tell the user: "GitHub CLI is not authenticated. Run `gh auth login`, then run client-repo-setup again." Do not continue.

## Step 2: Confirm details with the user

Ask, and wait for the answers. Never assume a default for any of them.

1. **GitHub owner:** the username or org the repo goes under.
2. **Client name and slug:** the display name, and the slug (lowercase, hyphens only, e.g. `woodlands-physio`). Suggest the slug from the client's knowledge record, but confirm it.
3. **Operating system:** Mac or Windows, for the path.
4. **Drive check:** show the target path and ask "Is this path outside your Google Drive / OneDrive sync folder?" If the answer is no or not sure, stop. Do not create anything until it is confirmed.

## Step 3: Create the repo

```bash
gh repo create <owner>/<slug> --private
```

If it fails because the repo already exists, or for any other reason, stop and report the exact error. Do not carry on against a repo you did not just create without the user's say-so.

## Step 4: Clone it

```bash
mkdir -p ~/Documents/Projects/<client>
cd ~/Documents/Projects/<client>
gh repo clone <owner>/<slug>
```

On Windows, use `New-Item -ItemType Directory -Force` and `Set-Location` under `$env:USERPROFILE\Documents\Projects\<client>`.

## Step 5: Run the scaffold

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/client-repo-setup/scripts/scaffold_client_repo.py \
  --root ~/Documents/Projects/<client>/<slug> \
  --client-name "<Client Name>" \
  --client-slug <slug>
```

The script fills `{{client_name}}`, `{{client_slug}}` and the scaffold date. If any target file already exists it refuses, lists every existing path and writes nothing. If that happens, tell the user which files exist. Never delete or overwrite them. Either stop, or (only if the user agrees) add just the missing files by hand.

After it runs, replace `OWNER` in `README.md` with the real GitHub owner.

Every brain note starts with empty `> gap: not yet captured` sections. They are filled later from the client's own material, and never guessed. Do not edit the gap lines here.

## Step 6: Commit and push to `main`

```bash
cd ~/Documents/Projects/<client>/<slug>
git add .
git commit -m "chore: scaffold client repo"
git push origin main
```

All later work during staging pushes straight to `main`. There are no round or review branches.

## Step 7: Record the repo URL

Per the routing contract, add the repo URL (`https://github.com/<owner>/<slug>`) to the client's canonical overview in the shared LHM Knowledge vault, under its Systems and files links, and read the note back to confirm. If the overview does not exist or the vault is unavailable, say so plainly. Do not create a blank profile or a fallback note.

## Step 8: Add default collaborators (with confirmation)

Offer to add the standard LHM project collaborators with **write** access. Invite `GrumpyGeorgie` directly. For Kristalyn and Jaimee, use only confirmed GitHub usernames. Never guess a username from an email address. If a username is unknown, record the invitation as a follow-up.

```bash
gh api --method PUT repos/<owner>/<slug>/collaborators/<username> -f permission=push
```

## Step 9: Verify and report

```bash
gh repo view <owner>/<slug>
git -C ~/Documents/Projects/<client>/<slug> status
```

The working tree should be clean and the repo visible on GitHub. Tell the user the repo URL, the local path, and which collaborator invitations are still pending. Say that the next step is the sitemap.
