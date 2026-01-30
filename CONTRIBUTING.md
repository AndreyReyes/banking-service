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

## Commit hygiene

- Keep commits focused to one logical change; prefer 3–5 files max.
- Commit after each testable slice or passing test.
- If a change spans subsystems, split into separate commits or PRs.
- Use a separate commit for tests before implementation (TDD).

## Tests and quality checks

Run the full local checks before opening a PR:

```bash
ruff check .
pytest
```

Notes:
- Black and mypy are intentionally deferred until cleanup (see `ROADMAP.md`).

## TDD expectation

Write a failing test before implementing new behavior. Add unit tests for
services and integration tests for endpoints where appropriate.

Suggested commit order:
- `test:` add failing test
- `feat:` or `fix:` implement behavior
- `docs:` update docs if behavior changed

## Pull requests

PRs should include:
- A clear summary of behavior changes
- Test evidence (commands run)
- Any docs updates required

PR sizing guidelines:
- Prefer <300 lines diff per PR; split larger work.
- Keep PRs to one feature or fix; avoid multi-domain bundles.

See the PR template for the checklist.
