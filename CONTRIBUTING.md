# Contributing

Thanks for contributing to the banking service. This project follows a
trunk-based workflow with short-lived branches and small, frequent commits.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Workflow

- Create a short-lived branch from `master`.
- Keep changes small and focused.
- Open a PR early and iterate quickly.
- Merge via PR once checks pass.

Branch naming:
- `feat/<topic>`
- `fix/<topic>`
- `docs/<topic>`
- `chore/<topic>`

## Commit messages

Use conventional commits:
- `feat: add account freeze endpoint`
- `fix: prevent overdraft race`
- `docs: clarify setup steps`
- `test: cover transfer reversal`

## Tests and quality checks

Run the full local checks before opening a PR:

```bash
ruff check .
black --check .
mypy .
pytest
```

## TDD expectation

Write a failing test before implementing new behavior. Add unit tests for
services and integration tests for endpoints where appropriate.

## Pull requests

PRs should include:
- A clear summary of behavior changes
- Test evidence (commands run)
- Any docs updates required

See the PR template for the checklist.
