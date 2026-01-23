# Implementation Plan — TDD Checkpoints

This plan maps `MILESTONES.md` into test‑first execution steps and commit gates.

## Quality gates (apply to every checkpoint)
- Tests are written first (red → green → refactor).
- Unit tests for service logic; integration tests for API endpoints.
- Structured JSON logging and health checks remain green.
- Run: `pytest`, plus lint/type checks as configured.

## Phase 1 — Project scaffolding & developer experience
**Checkpoint: Repo baseline**
- Tests to write:
  - Smoke test for test runner discovery.
- Implementation steps:
  - Setup app skeleton, test config, lint/format tooling.
  - Configure settings for dev/test.
- Commit gate:
  - `pytest` passes.

## Phase 2 — Production readiness foundations
**Checkpoint: Health and readiness endpoint**
- Tests to write:
  - `/v1/health` returns 200 and expected schema.
- Implementation steps:
  - Add health router and app wiring.
- Commit gate:
  - Health integration tests green.

**Checkpoint: Database wiring (SQLite) + migrations**
- Tests to write:
  - DB session creation and connectivity.
  - Alembic migration applies to empty DB.
- Implementation steps:
  - SQLAlchemy engine/session, Alembic config.
  - Enable WAL + busy timeout for SQLite.
- Commit gate:
  - DB tests green and migrations run.

**Checkpoint: Structured logging foundation**
- Tests to write:
  - Request ID generated/propagated.
  - Log fields include `request_id` and `status_code`.
- Implementation steps:
  - Structlog config + middleware.
- Commit gate:
  - Logging tests green.

## Phase 3 — Core domain + business capabilities
**Checkpoint: Domain models + validation rules**
- Tests to write:
  - Pydantic validation for key schemas.
  - Model constraints where applicable.
- Implementation steps:
  - SQLAlchemy models and Pydantic schemas (no endpoints).
- Commit gate:
  - Unit tests green.

**Checkpoint: Signup**
- Tests to write:
  - Create user and account holder.
  - Password hashing verified.
- Implementation steps:
  - Auth service + signup endpoint.
- Commit gate:
  - Integration tests green.

**Checkpoint: Authentication**
- Tests to write:
  - Login returns JWT.
  - Protected route rejects unauthenticated.
  - Refresh token rotation works and revokes old tokens.
  - Sensitive actions write audit log with IP and device ID.
- Implementation steps:
  - JWT issuance + dependency.
  - Refresh token persistence + rotation.
  - Audit logging for auth and sensitive actions.
- Commit gate:
  - Auth tests green.

**Checkpoint: Account holders CRUD**
- Tests to write:
  - Create/read/list holder.
  - Authorization enforced.
- Implementation steps:
  - Service + routers for holders.
- Commit gate:
  - Integration tests green.

**Checkpoint: Accounts**
- Tests to write:
  - Create/view/list accounts.
  - Ownership checks enforced.
- Implementation steps:
  - Account service + routers.
- Commit gate:
  - Integration tests green.

**Checkpoint: Transactions**
- Tests to write:
  - Deposit/withdrawal affects balance.
  - Negative balances prevented.
- Implementation steps:
  - Transaction service + router.
- Commit gate:
  - Integration tests green.

**Checkpoint: Money transfer**
- Tests to write:
  - Transfer debits/credits correctly.
  - Atomicity on failure.
- Implementation steps:
  - Transfer service + router.
- Commit gate:
  - Integration tests green.

**Checkpoint: Cards**
- Tests to write:
  - Issue card + status checks.
- Implementation steps:
  - Card service + router.
- Commit gate:
  - Integration tests green.

**Checkpoint: Statements**
- Tests to write:
  - Statement includes summary + transactions.
- Implementation steps:
  - Statement service + router.
- Commit gate:
  - Integration tests green.

## Phase 4 — Correctness & safety guarantees
**Checkpoint: Error handling production pass**
- Tests to write:
  - Error envelope for validation and auth.
  - Proper HTTP status codes.
- Implementation steps:
  - Global exception handlers + error mapping.
- Commit gate:
  - Error tests green.

## Phase 5 — Operational deliverables
**Checkpoint: Containerization + env configs**
- Tests to write:
  - Container builds.
  - Compose starts health endpoint.
- Implementation steps:
  - Dockerfile, docker-compose, env validation.
- Commit gate:
  - Container smoke test green.

**Checkpoint: Test coverage checkpoint**
- Tests to write:
  - Add missing tests to reach target.
- Implementation steps:
  - Increase coverage thresholds.
- Commit gate:
  - Coverage target met.

**Checkpoint: Documentation + AI usage report**
- Tests to write:
  - N/A (docs only).
- Implementation steps:
  - Write README, SECURITY, ROADMAP, AI_USAGE.
- Commit gate:
  - Docs complete and consistent.

## Dependencies and ordering
- Health endpoint requires minimal app setup.
- DB wiring before models/services.
- Logging before auth to capture early requests.
- Auth before protected resources.
- Transfers require accounts + transactions.
