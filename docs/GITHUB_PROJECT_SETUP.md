
# AI Coding Assistant Guide: GitHub Projects Setup

You are setting up GitHub Projects management for this repository.

The reusable setup files already exist:

- `docs/templates/github-project-kanban-playbook.md`
- `scripts/apply_github_project_style.sh`

## Goal

Use the reusable GitHub Project setup to configure common project-management fields, then adapt the Project only where this repository needs project-specific
classification.

## Rules

- Read `docs/templates/github-project-kanban-playbook.md` before making changes.
- Do not create duplicate repository labels for planning metadata.
- Use GitHub Project fields for `Status`, `Priority`, `Size`, `Evidence`, `Assignees`, and `Milestone`.
- Keep the reusable setup generic.
- Do not add project-specific fields like `Area`, `Type`, `Platform`, or `Release` until this repo’s needs are clear.
- Do not assume fields from another project should be copied here.

## Required Inputs

Before applying setup, confirm or discover:

- GitHub owner
- Repository name
- GitHub Project number
- Whether the Project was created from the repository UI using Kanban/Board template

If the Project does not exist yet, tell the user to create it from the repository `Projects` tab first.

## Setup Steps

1. Verify GitHub CLI auth:

```bash
gh auth status
```

The account must have repo and project scopes.

2. Ensure the helper is executable:

```bash
chmod +x scripts/apply_github_project_style.sh
```

3. Apply the common reusable setup:

```bash
scripts/apply_github_project_style.sh <owner> <project-number>
```

4. Verify fields:

```bash
gh project field-list <project-number> --owner <owner> --format json
```

Expected common fields:

- Status: Backlog, Ready, In progress, In review, Done
- Priority: P0, P1, P2
- Size: XS, S, M, L, XL
- Evidence: Not Started, Tests Added, Docs Updated, Demo Verified, CI Passed

## Project-Specific Fields

After the common setup is applied, inspect this repository’s docs, roadmap, architecture, package structure, and planned milestones.

Only then recommend project-specific fields.

Examples:

- Backend/API project: Area = API, Auth, Database, CI
- Frontend project: Area = UI, Routing, State, Design, CI
- AI project: Area = Data, Model, Eval, Prompting, Serving
- Library project: Area = Core, CLI, Docs, Tests, Release

If useful, add fields such as:

- Area
- Type
- Platform
- Release
- Environment

But do not add them to the reusable helper script.

## Issue Creation Rules

When creating GitHub Issues:

Each issue must include:

## Goal

## Acceptance Criteria

## Verification

Before moving an issue to Ready, ensure:

- It has an assignee.
- It has a milestone if milestone planning is active.
- It has Priority.
- It has Size.
- It has Evidence = Not Started.
- It has any required project-specific fields.

## Status Rules

- Backlog: valid idea, not ready.
- Ready: scoped, assigned, and has acceptance criteria.
- In progress: actively being worked on.
- In review: implementation done, waiting for review/checks.
- Done: verified.

## Completion Report

After setup, report:

- Project URL
- Fields created or updated
- Whether project-specific fields were added
- Number of issues added to the Project
- Any assumptions made
- Verification commands run


And the short prompt for a new AI assistant would be:

```text
Use the existing GitHub Projects setup files in this repo:
- docs/templates/github-project-kanban-playbook.md
- scripts/apply_github_project_style.sh

Apply only the common reusable setup first. Then inspect this repo and recommend any project-specific fields separately. Do not copy project-specific fields from another
repo unless they fit this repo.
```
