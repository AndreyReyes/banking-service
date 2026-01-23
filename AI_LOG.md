# AI Usage Log

## FDE tech assessment instructions

### Prompts and iterations

- Requested creation and commit of `FDE_Tech_Assessment_(T2).md`, then clarified repo state after deleting local and remote git history.
- Asked for a production-ready stack choice; selected Python, then requested a technical specification.
- Added a TDD requirement and asked for a Git workflow.
- Requested the technical specification in both plain and Markdown formats.

### How AI was used

- Generated a production-ready Python stack recommendation aligned with the assessment requirements.
- Produced a structured technical specification for the project, including TDD requirements.
- Suggested a practical Git workflow and conventional commit guidance.
- Summarized repository status and next steps after re-initializing git.

### Outcomes achieved

- Created `FDE_Tech_Assessment_(T2).md` in the project root and committed it as the initial commit.
- Established a clear technical specification and workflow guidance for the banking service assignment.

## Banking service technical specification and rules

### Summary of prompts and iterations

- Refine the technical specification and capture requirements in a new markup file.
- Create Cursor rules for TDD, JSON logging, SQLite safety, and Ubuntu 24.04.
- Build TDD milestone checkpoints and convert them to a checklist grouped by category.
- Draft architecture and implementation plan documents with DB schema and diagrams.
- Update architecture and plan for secure session management, refresh tokens, and audit logs.
- Stage and commit documentation changes with appropriate messages.

### How AI was used

- Structured and expanded the technical spec into concrete API, data model, and ops guidance.
- Authored project rules to enforce testing, logging, DB safety, and startup health checks.
- Organized milestone checkpoints into trackable phases and mapped them to TDD gates.
- Produced architecture and implementation plan docs including schema and flows.
- Assisted with clean, conventional commits for documentation deliverables.

### Things achieved

- Added `TECHNICAL_SPEC.md` with the refined spec.
- Added `.cursor/rules/banking.mdc` enforcing project rules.
- Added `MILESTONES.md` and linked it from `README.md`.
- Added `ARCHITECTURE.md` and `IMPLEMENTATION_PLAN.md` with schema and diagrams.
- Updated architecture to include refresh token rotation and centralized audit logs.

## Phase 1: Project scaffolding & developer experience

### Summary of prompts and iterations

- Requested Phase 1 implementation using the architecture and implementation plan.
- Required TDD-first changes with process documentation in `AI_LOG.md`.
- Asked to install dependencies, run tests, pin versions, and document library choices.

### How AI was used

- Created a test-first scaffold and then implemented the minimal FastAPI app.
- Added dev tooling configuration (pytest, ruff, black, mypy) and CI workflow.
- Documented setup instructions and environment expectations.
- Installed dependencies, pinned versions, and captured rationale in `DEPENDENCIES.md`.

### Challenges encountered and solutions

- Repository ignores `.env.example` via global ignore rules; documented env vars in `README.md` instead.
- System `python` command unavailable; used `python3` for environment setup.

### Manual intervention required

- None during implementation; dependencies were installed and tests executed by the AI.

### Things achieved

- Added app skeleton with `create_app()` and core config/logging stubs.
- Added smoke test for test runner discovery (TDD baseline).
- Added `pyproject.toml` tooling config plus `requirements.txt` and `requirements-dev.txt`.
- Added GitHub Actions CI workflow for lint/format/type/test checks.
- Expanded `.gitignore` and updated `README.md` with setup and test instructions.
- Marked the Phase 1 milestone as complete in `MILESTONES.md`.
- Added pinned dependency versions, a dependency rationale doc, and a Tech Stack table.
- Fixed test import path and confirmed `pytest` passes.
