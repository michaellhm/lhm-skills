---
name: repo-org-migration
description: "Move an existing client website repository from a personal GitHub account into the LHM GitHub organisation (lhmorg) without breaking its hosting. Use this when the user says 'move this repo to lhmorg', 'migrate the repo to the org', 'transfer the client repo', 'repo migration', 'move my repos across', 'repo-org-migration', or is working through the GitHub organisation migration list. Covers pre-checks, GitHub Transfer, team access, private visibility, reconnecting Cloudflare/Vercel/GitHub Actions deploys, a test deployment, the live-site check and the handoff record. One repository at a time."
---

## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill's narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.

# Repo Org Migration

Move one client website repository into `lhmorg` with GitHub's **Transfer** function, then prove the site still deploys. This is the process verified on the Alpha Sports Med pilot (October 2026). Never create a replacement repository and copy code across: Transfer keeps history, issues, Actions secrets and a redirect from the old URL.

Work on **one repository at a time**. Do not start the next until the current one has a successful post-migration deployment and a live-site check.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-org-migration/LEARNED.md`.

Confirm `gh auth status` works and the signed-in account is a member of `lhmorg`. If not, stop and ask the user to run `gh auth login`.

## Approval boundaries

These steps change shared infrastructure. Ask before each one, for each repository, and wait for an explicit yes:

- the Transfer itself
- changing visibility to private
- reconnecting or re-authorising a hosting integration
- any test commit pushed to the default branch

Read-only checks (Step 1) need no approval. Never delete a repository, a Cloudflare/Vercel project or a deployment as part of this skill. Archive only when the owner asks.

## Step 1: Pre-checks (read-only)

Set `SRC=<owner>/<repo>` and run:

```bash
gh api repos/$SRC --jq '{private, default_branch, admin: .permissions.admin, archived}'
gh secret list -R $SRC
ls .github/workflows 2>/dev/null; gh api repos/$SRC/contents/.github/workflows --jq '.[].name' 2>/dev/null
gh api repos/$SRC/contents/vercel.json --jq .name 2>/dev/null
gh api repos/$SRC/contents/wrangler.toml --jq .name 2>/dev/null
```

Record in the migration checklist:

1. **Client and purpose.** Confirm the repository belongs to a current LHM client and what it serves (main site, landing pages, prototype). Ask the owner when unsure. Two repositories for one client can serve different domains: compare them before calling either superseded.
2. **Transfer rights.** `admin` must be `true`. Write access is not enough: GitHub only lets owners/admins transfer. If false, ask the owner to transfer it themselves or grant admin.
3. **How it deploys.** One of:
   - **GitHub Actions + Wrangler** (workflow calling `wrangler pages deploy`). Secrets such as `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` move with the repository.
   - **Cloudflare Pages Git integration** (project connected to the repository in the Cloudflare dashboard). The Cloudflare GitHub app must be installed on `lhmorg` with access to the repository.
   - **Vercel** (`vercel.json` or a Vercel project). The Vercel GitHub app must be installed on `lhmorg` **before** the transfer, or deploys stop.
   - **Other** (GitHub Pages, SFTP, none). Note it and check with the owner.
4. **Live URLs** to check afterwards: production domain, `*.pages.dev`/`*.vercel.app` preview, and two or three key pages.
5. **Baseline.** `curl -s -o /dev/null -w '%{http_code}'` on each URL so you can compare after.

If any blocker is open (no admin, Vercel app missing on lhmorg), stop and report it. Do not transfer.

## Step 2: Transfer

With approval:

```bash
gh api -X POST repos/$SRC/transfer -f new_owner=lhmorg
```

(Or GitHub web: Settings, Danger Zone, Transfer.) Then verify:

```bash
gh repo view lhmorg/<repo> --json nameWithOwner,visibility,defaultBranchRef
curl -sI https://github.com/$SRC | head -3   # expect a 301 to the new location
gh secret list -R lhmorg/<repo>               # same secrets as before
```

Update any local clone: `git remote set-url origin https://github.com/lhmorg/<repo>.git`.

## Step 3: Team access

`lhmorg` members get the organisation's default permission (currently read). Check:

```bash
gh api orgs/lhmorg/members --jq '.[].login'
gh api repos/lhmorg/<repo>/collaborators --jq '.[] | {login, role: .role_name}'
```

Admins should be Michael and the person migrating. Give extra write access only when the owner asks. Do not add members to the organisation as part of this skill.

## Step 4: Visibility

Client repositories in `lhmorg` are private. With approval:

```bash
gh repo edit lhmorg/<repo> --visibility private --accept-visibility-change-consequences
```

Note for the handoff: on GitHub Free, private repositories share 2,000 Actions minutes a month across the organisation. Record the typical deploy duration so usage can be tracked as more repositories move.

## Step 5: Reconnect hosting (only if needed)

- **Actions + Wrangler:** usually nothing to do. Confirm Actions is enabled (`gh api repos/lhmorg/<repo>/actions/permissions`).
- **Cloudflare Pages Git integration:** in the Cloudflare dashboard, open the Pages project, Settings, Builds. Confirm it still points at `lhmorg/<repo>`. If it shows the old owner or an error, reconnect through the Cloudflare GitHub app (already installed on lhmorg for all repositories).
- **Vercel:** open the project, Settings, Git. Reconnect to `lhmorg/<repo>` if needed.

Change only what is broken.

## Step 6: Test deployment

Prefer a manual workflow run, which needs no code change:

```bash
gh workflow run <workflow-file> -R lhmorg/<repo> --ref <default-branch>
gh run watch -R lhmorg/<repo> $(gh run list -R lhmorg/<repo> -L1 --json databaseId --jq '.[0].databaseId')
```

For Git-integration hosting with no manual trigger, retry the latest deployment from the host dashboard. Push a small test commit only with approval. A deploy counts only when the run or deployment reports success; record its ID.

Repeat this test after Step 4 if visibility changed after the first test.

## Step 7: Live-site check

Re-run the Step 1 baseline URLs. Every URL must return the same status as before (normally 200), and the page should show the latest content. If anything fails, stop, report the exact error and the last good state. Do not move to the next repository.

## Step 8: Record and hand off

1. Tick the repository in the migration checklist with: new URL, deploy method, test run/deployment ID, URLs checked, visibility, date.
2. Post a short handback on the migration task in BasicOps (through `lhm-project-hub:basicops-task-manager`): what moved, deploy proof, live check, anything left (for example the old Cloudflare project to remove later, an Actions-minutes note, or a repository to archive).
3. Note any reusable lesson in this skill's `LEARNED.md`.

## Done means

The repository is in `lhmorg`, private, with correct access; a post-migration deployment succeeded; the live site was checked; the checklist and BasicOps handback record the evidence.
