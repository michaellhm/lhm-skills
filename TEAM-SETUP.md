# LHM Skills — Team Setup

How to install the LHM plugin suite, keep it updated, and feed the weekly skill-improvement loop.

## 1. Install the marketplace (once)

You need read access to this GitHub repo, then:

```bash
claude plugin marketplace add michaellhm/lhm-skills
```

Install the hubs you use (all is fine):

```bash
claude plugin install lhm-marketing-hub@lhm-marketing-skills
claude plugin install lhm-wordpress-hub@lhm-marketing-skills
claude plugin install lhm-gmb-hub@lhm-marketing-skills
claude plugin install lhm-content-engine@lhm-marketing-skills
claude plugin install lhm-client-updates-hub@lhm-marketing-skills
claude plugin install lhm-learn@lhm-marketing-skills
claude plugin install lhm-skill-ops@lhm-marketing-skills
```

In the Claude desktop app, add the marketplace from Settings → Plugins instead — same repo.

## 2. Install Task Observer (once)

Task Observer captures the observations that drive the weekly review:

```bash
git clone --depth 1 https://github.com/rebelytics/one-skill-to-rule-them-all ~/.claude/skills/task-observer
```

It logs silently to `skill-observations/log.md` in each workspace as you work. You don't need to do anything day-to-day.

## 3. Set up your weekly sync routine (once)

Everyone runs `sync-observations` weekly so the team review can see your logs. Create a local scheduled routine (in Claude Code, just ask: *"schedule /sync-observations to run every Friday at 4pm locally"*), or run it by hand on Fridays:

```bash
claude -p "/sync-observations"
```

Your logs land in `observations/<you>/` in this repo. That's your entire contribution to the loop.

## 4. The weekly review (Michael's machine only)

One routine runs `weekly-skill-review` each Sunday evening. It reads everyone's observations, applies the clear improvements to skills on a branch, and opens a PR. **Nothing changes until Michael merges the PR.**

## 5. Getting updates

After a review PR merges, plugin versions are bumped. Claude Code refreshes marketplaces automatically; to force it:

```bash
claude plugin marketplace update lhm-marketing-skills
```

## How updates flow (summary)

```
you work → Task Observer logs locally
Friday    → your routine syncs logs to observations/<you>/
Sunday    → weekly-skill-review PRs the skill updates
Monday    → Michael reviews & merges → versions bump
next day  → everyone's plugins auto-update
```

Want to propose a skill change directly? Skip the loop: branch, edit the skill, bump its version in `.claude-plugin/marketplace.json` and the plugin's `plugin.json`, open a PR.
