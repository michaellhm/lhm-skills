---
name: wp-project-setup
description: "Initialize the canonical folder structure for a new WordPress website project. Use this when the user says 'new project', 'set up project folders', 'initialize website project', 'create project structure', or 'start fresh'. Creates all required directories and placeholder files for the phased build workflow."
---

# Project Setup

Create the canonical folder structure for a new WordPress website project. This structure is the foundation for the entire phased build workflow.

## Step 1: Confirm Project Location

Ask the user where to create the project:

- Use the `AskUserQuestion` tool: "Where should I create the project folder?"
  - **Current directory** — create folders here
  - **New subfolder** — ask for the project/client name and create `./project-name/`

## Step 2: Read the Canonical Structure

Read `${CLAUDE_PLUGIN_ROOT}/references/folder-structure.md` to get the exact folder structure.

## Step 3: Create the Folder Structure

Create these directories:

```
/client/
/seo/
/seo/page_briefs/
/content/
/content/services/
/content/locations/
/design/
/wp/
/wp/theme/
/wp/blocks/
/qa/
/ops/
```

## Step 4: Create Starter Files

Create these minimal starter files:

### `/client/client_profile.md`
```markdown
---
business_name: ""
industry: ""
website: ""
primary_contact: ""
---

# Client Profile

> This file is the source of truth for client context. All skills read this file before starting work.

## Business Overview


## Target Audience


## Services / Offerings


## Locations / Service Areas


## Goals & Objectives


## Competitors

```

### `/client/constraints.md`
```markdown
# Project Constraints

## Budget


## Timeline


## Technical Requirements


## Compliance / Regulatory


## Existing Assets

```

### `/client/clarifications.md`
```markdown
# Clarifications Log

Running log of questions asked and answers received during the project.

| Date | Question | Answer | Source |
|------|----------|--------|--------|

```

### `/wp/wp_state.md`
```markdown
# WordPress Build State

Tracks the current state of the WordPress installation.

## Environment

- **URL**:
- **WP Version**:
- **PHP Version**:
- **Theme**:
- **Status**: Not started

## Pages Built

| Page | Content File | Status | WP Post ID |
|------|-------------|--------|------------|

## Plugins Installed

| Plugin | Purpose | Status |
|--------|---------|--------|

## Build Log

| Date | Action | Notes |
|------|--------|-------|

```

## Step 5: Confirm

Tell the user:

> Project structure created. Here's what's next:
>
> 1. **Phase A: Client Intake** — Add client information to `/client/client_profile.md`
>    - You can do this manually or run the **Client Context Intake** skill to extract facts from transcripts/notes
> 2. The build progresses through phases B (SEO) → C (Content) → D (Design) → E (Build) → F (Ops)
>
> Run the **Client Context Intake** skill when you're ready to start Phase A.
