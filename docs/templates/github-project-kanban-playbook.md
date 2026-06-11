# Reusable GitHub Project Kanban Setup

This playbook captures the project-management setup used for this repository so it
can be reused in future projects.

## When To Use

Use this setup when starting a private or public repository that should follow a
lightweight company-style workflow:

- GitHub Issues hold task details.
- GitHub Projects holds planning metadata.
- Project fields, not labels, track planning metadata.
- Every ready task has an explicit assignee.

## Prerequisites

- GitHub CLI is authenticated with `repo`, `project`, and `workflow` scopes.
- The target GitHub repository exists.
- Issues are enabled on the repository.
- You know the owner login and Project number.

Verify auth:

```bash
gh auth status
```

## Create The Project

Create the Project from the repository UI:

1. Open the repository on GitHub.
2. Go to `Projects`.
3. Create a new Project.
4. Choose the Kanban or Board template.
5. Link the Project to the repository.

After creation, note the Project URL. The number at the end is the Project number:

```text
https://github.com/users/<owner>/projects/<project-number>
```

## Apply Standard Fields And Colors

Run the reusable helper from the repo root:

```bash
scripts/apply_github_project_style.sh <owner> <project-number>
```

Example:

```bash
scripts/apply_github_project_style.sh NAT23042004 4
```

The helper keeps the Kanban template fields and adds or styles only the common
fields that should transfer cleanly between projects:

- `Status`: Backlog, Ready, In progress, In review, Done
- `Priority`: P0, P1, P2
- `Size`: XS, S, M, L, XL
- `Evidence`: Not Started, Tests Added, Docs Updated, Demo Verified, CI Passed

The helper does not remove existing project-specific fields.

## Field Ownership

Use Project fields as project-management metadata:

- `Status`: workflow state.
- `Priority`: planning priority.
- `Size`: rough implementation size.
- `Evidence`: proof required before closing.
- `Assignees`: direct owner.
- `Milestone`: delivery target.
- `Estimate`: rough effort estimate when the team uses estimates.
- `Start date`: planned start date when date planning is useful.
- `Target date`: planned completion date when date planning is useful.

Do not create custom labels for `priority:*`, `size:*`, evidence values, or owner
names. Use labels only for normal GitHub issue triage when needed.

## Optional Project-Specific Fields

Add project-specific fields only after the common setup is working. Good examples:

- `Area`: component, product surface, team, or domain boundary.
- `Type`: feature, bug, research, documentation, security, or test work.
- `Customer`, `Platform`, `Environment`, or `Release`: only when they are useful
  for that project's planning.

Do not put project-specific fields in the reusable helper. Each new project should
choose its own values.

## Status Rules

- `Backlog`: valid idea, not ready for implementation.
- `Ready`: scoped, accepted, and assigned.
- `In progress`: implementation started.
- `In review`: implementation complete and waiting for review or cleanup.
- `Done`: verified and documented.

## Assignee Rules

- `Backlog`: assignee optional.
- `Ready`: assignee required.
- `In progress`: assignee required and should match the active implementer.
- `In review`: assignee remains the implementer; reviewers belong on the pull
  request or built-in `Reviewers` field.
- `Done`: assignee remains for accountability.

For solo projects, assign issues to yourself. For team projects, assign the person
who owns delivery before moving the task to `Ready`.

## Suggested First Issues

For a new technical project, start with:

1. Establish truthful project foundation and CI.
2. Define product requirements and non-goals.
3. Define architecture and first implementation milestone.
4. Add a minimal runnable package or app skeleton.
5. Add first feature-slice implementation issue.
6. Add generated fixture or smoke-test issue.
7. Review foundation baseline before first push or release.

## Verification

After setup, verify:

```bash
gh project field-list <project-number> --owner <owner> --format json
gh project item-list <project-number> --owner <owner> --format json --limit 20
gh issue list -R <owner>/<repo> --state open --json number,title,assignees
```

The Project should show colored field values, issues should have assignees before
they are `Ready`, and repository labels should not duplicate common Project fields.
