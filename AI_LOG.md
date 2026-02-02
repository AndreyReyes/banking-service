# AI Usage Log

Each section below was created by a separate agent following the standard phase
prompt shown in `AI_USAGE_REPORT.md` (lines 75–78), which asked for regression
testing (when applicable), implementation, and an appended AI usage summary.

## FDE tech assessment instructions

### Prompts and iterations

- Requested creation and commit of `FDE_Tech_Assessment_(T2).md`, then clarified repo state after deleting local and remote git history.
- Asked for a production-ready stack choice; selected Python, then requested a technical specification.
- Added a Test-Driven Development (TDD) requirement and asked for a Git workflow.
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

## Phase 2: Production readiness foundations

### Summary of prompts and iterations

- Requested Phase 2 implementation using the architecture and implementation plan.
- Required TDD-first changes and logging of the process in `AI_LOG.md`.
- Asked to mark completed milestones after implementation.
- Requested a setup script and README run instructions for the app.

### How AI was used

- Wrote failing integration tests for health, database wiring, and logging.
- Implemented health/readiness routing, SQLite session management, and Alembic setup.
- Added structured request logging with request ID propagation and startup DB health checks.
- Added a setup helper script and documented how to run the app in `README.md`.

### Challenges encountered and solutions

- `pytest` was not available in the environment; noted the missing dependency so tests can be rerun after installing dev requirements.

### Manual intervention required

- Install `pytest` (or `requirements-dev.txt`) and rerun `python3 -m pytest`.

### Things achieved

- Added `/v1/health` endpoint with UTC timestamp and DB connectivity checks.
- Implemented SQLite engine/session wiring with WAL and busy timeout.
- Added Alembic configuration and an initial empty migration.
- Implemented request logging middleware with `request_id`, `method`, `path`, `status_code`, and `duration_ms`.
- Marked Phase 2 production readiness milestones as complete in `MILESTONES.md`.
- Added `scripts/setup_env.sh` and README instructions to run the API.

## Phase 3: Core domain + business capabilities

### Summary of prompts and iterations
- Requested Phase 3 implementation using architecture/plan with regression testing first.
- Required TDD-first implementation and updates to `MILESTONES.md` and `AI_LOG.md`.
- Raised security issues around `JWT_SECRET` validation and bcrypt password length handling.
- Asked for documentation updates in `README.md`, `TECHNICAL_SPEC.md`, and `ARCHITECTURE.md`.
- Requested continuation to complete remaining Phase 3 endpoints and tests.

### How AI was used
- Ran regression tests in a new virtual environment and implemented new failing tests first.
- Built core domain models, schemas, services, routers, and migrations for accounts, transactions, transfers, cards, and statements.
- Added protected routes with ownership checks and updated authentication dependencies.
- Implemented password length validation to avoid bcrypt errors and added security documentation.
- Updated milestones and documentation to reflect new behavior and requirements.

### Challenges encountered and solutions
- System Python was externally managed (PEP 668); created a venv to run tests and install dependencies.
- Bcrypt threw on >72 byte passwords; added schema validation and defensive checks in security helpers.
- SQLAlchemy `session.begin()` conflicted with autobegin; switched to `begin_nested()` for transfers.

### Manual intervention required
- None. All environment setup, tests, and changes were performed by the AI.

### Things achieved
- Added core domain tables and migrations for accounts, transactions, transfers, and cards.
- Implemented account holders CRUD, account creation/listing, transactions, transfers, cards, and statements endpoints.
- Added comprehensive integration tests for core resources and unit tests for password validation.
- Enforced production `JWT_SECRET` validation and documented it in `README.md`, `TECHNICAL_SPEC.md`, `ARCHITECTURE.md`, and `SECURITY.md`.
- Marked Phase 3 milestones complete and confirmed full test suite passes.
- Fixed audit logging for failed logins, tightened transaction create validation, and prevented same-account transfers with new tests.
- Ensured expired refresh tokens persist revocation updates with a refresh flow test.

## Phase 4: Correctness & safety guarantees

### Summary of prompts and iterations
- Requested Phase 4 implementation with regression testing first and TDD workflow.
- Asked to append process documentation to `AI_LOG.md` and update milestones after tests pass.
- Required a final summary of prompts, AI usage, challenges, manual steps, and outcomes.
- Asked to follow `README.md` setup to resolve the pytest environment issue.

### How AI was used
- Added failing integration tests for standardized error envelopes on validation and auth failures.
- Implemented global exception handlers to return the consistent error envelope.
- Wired exception handling into app startup to cover all routes.
- Used `README.md` setup steps to create a venv, install dev deps, and run regression tests.
- Fixed validation error serialization using `jsonable_encoder`.

### Challenges encountered and solutions
- Validation error payload contained a non-JSON-serializable `ValueError`; encoded errors for safe JSON output.

### Manual intervention required
- None.

### Things achieved
- Added error envelope integration tests covering validation and unauthorized access.
- Implemented centralized exception handling with consistent error payloads.
- Resolved test failure and confirmed full test suite passes.
- Marked the Phase 4 milestone complete in `MILESTONES.md`.

## Phase 5: Operational deliverables

### Summary of prompts and iterations
- Requested Phase 5 implementation with regression testing first and TDD workflow.
- Asked to implement operational deliverables and update milestones when tests pass.
- Required updates to `AI_LOG.md` with a detailed summary of AI usage and outcomes.

### How AI was used
- Ran regression tests in a fresh venv, then added failing containerization tests.
- Implemented Docker packaging and docker-compose configuration aligned with the
  operational checklist.
- Added coverage enforcement to pytest and updated documentation for new tooling.

### Challenges encountered and solutions
- Docker smoke tests require Docker/Compose; tests are skipped unless
  `RUN_DOCKER_TESTS=1` is set to avoid false failures in non-Docker environments.
- Docker Compose health checks were flaking on cold starts; switched the test to
  wait for container health (`docker compose --wait`) before hitting `/v1/health`.

### Manual intervention required
- None. Optional: set `RUN_DOCKER_TESTS=1` with Docker installed to run container
  smoke tests.

### Things achieved
- Added multi-stage `Dockerfile`, `docker-compose.yml`, and `.dockerignore`.
- Added containerization integration tests for Dockerfile/compose validation plus
  optional build/health smoke tests.
- Enforced 92% coverage gate via `pytest-cov` and updated `DEPENDENCIES.md`.
- Updated `README.md` with Docker run/compose instructions and coverage notes.
- Updated coverage target in `TECHNICAL_SPEC.md`.
- Confirmed Docker `29.1.5` and Docker Compose `v5.0.1` are installed and
  documented as supported versions.
- Ran container smoke tests successfully with `RUN_DOCKER_TESTS=1` and the full
  test suite passing.
- Marked Phase 5 operational milestones complete in `MILESTONES.md`.

## Phase 5: Checkpoint: Bonus demo deliverables

### Summary of prompts and iterations
- Requested regression testing before Phase 5 bonus work and TDD-first changes.
- Asked for demo flow test, CLI demo client, and simple frontend deliverables.
- Required milestones updates and appended AI usage documentation.

### How AI was used
- Ran regression tests in a fresh venv and created a demo flow integration test.
- Implemented a config-driven and interactive CLI demo client and sample flow JSON.
- Built a minimal static frontend for the signup/login/account/transfer/statement flow.
- Updated README usage instructions and milestone checkboxes.

### Challenges encountered and solutions
- `pytest` was not found initially; created a venv and installed dev requirements.
- Running only the new test failed the coverage gate; resolved by running full suite.

### Manual intervention required
- None.

### Things achieved
- Added `tests/integration/test_demo_flow.py` covering the end-to-end demo flow.
- Added `scripts/demo_client.py` with interactive and JSON config modes plus
  `scripts/demo_flow.json` sample steps.
- Added static demo UI under `frontend/` with HTML/JS/CSS.
- Documented demo usage in `README.md` and marked bonus milestones complete.

## Phase 5: Frontend multi-user sessions + token refresh UX

### Summary of prompts and iterations
- Requested frontend updates for multi-user sessions, token expiry display,
  refresh controls, withdrawal actions, and keep-alive prompt behavior.
- Asked for documentation updates across root markdown files and workflow alignment.

### How AI was used
- Implemented multi-user in-memory token state, refresh handling, and UI updates
  for user-specific actions in the demo frontend.
- Added a keep-alive modal triggered three minutes before token expiry.
- Updated README, implementation plan, architecture, and technical spec to match.
- Ran the full test suite to confirm coverage and integration tests stayed green.

### Challenges encountered and solutions
- Ensured token refresh UX stayed demo-only by keeping all tokens in memory.

### Manual intervention required
- None.

### Things achieved
- Added user selectors across user-specific actions, token expiry display, and
  refresh controls in `frontend/`.
- Added withdrawal action support in the demo UI.
- Updated root docs to reflect the new frontend behavior and workflow guidance.