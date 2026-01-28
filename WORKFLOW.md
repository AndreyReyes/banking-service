# Git Workflow

This repo uses a trunk-based workflow with short-lived branches. The default
branch is `master`.

## Goals

- Small, frequent commits
- Parallel development with minimal merge pain
- CI gates on every change

## Daily flow

```bash
git checkout master
git pull --rebase
git checkout -b feat/my-change
```

Work in small slices and commit often:

```bash
git status
git add <files>
git commit -m "feat: add deposit validation"
```

Rebase if your branch diverges:

```bash
git fetch origin
git rebase origin/master
```

Open a PR early and keep it small. Merge once CI passes.

## Concurrent development

For multiple developers:
- Require PRs for `master`
- Require CI checks (lint/format/type/test)
- Keep branches short-lived (hours/days, not weeks)
- Prefer rebase over long-running merge commits

## Suggested GitHub settings (when ready)

- Branch protection on `master`
- Require status checks to pass
- Require PR reviews (1+)
- Enable auto-merge (optional)

## Local-only rule for now

All workflow and CI files can be prepared locally without any GitHub changes
until you are ready to push.
