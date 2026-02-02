# Technical Specification — Production‑Ready Banking REST Service (Python)

## Purpose
Deliver a production‑ready banking REST API that demonstrates AI‑assisted development, robust testing, containerization, structured logging, health checks, and operational readiness.

## Scope
Implement a minimal, coherent banking domain with authentication, account management, transactions, transfers, cards, statements, and health checks. A partial implementation is acceptable if clearly documented and tested.

## Constraints
- Do not modify `FDE_Tech_Assessment_(T2).md`.
- No secrets committed to the repo.
- SQLite is required for development; architecture must be portable to Postgres.
- Ubuntu 24.04 compatibility is required.
- Clean, conventional commit history.

## Tech Stack
- **Language:** Python 3.12
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Database:** SQLite (dev), portable to Postgres
- **Validation:** Pydantic v2
- **Testing:** pytest + httpx + coverage
- **Lint/Format/Type:** ruff + black + mypy
- **Logging:** structlog (JSON logs)
- **Server:** uvicorn (dev), gunicorn + uvicorn workers (prod)
- **Containerization:** Docker + docker‑compose (multi‑stage build)

## Architecture
```
app/
  api/           # routers (REST endpoints)
  core/          # config, logging, security, settings
  db/            # DB session, models, migrations
  services/      # business logic
  schemas/       # Pydantic request/response models
  main.py
tests/
  unit/
  integration/
```

## API Design
Base path: `/v1`

### Authentication
- `POST /v1/auth/signup` — create user and account holder profile
- `POST /v1/auth/login` — return JWT access token

Notes:
- Passwords hashed using bcrypt/argon2 (no plaintext storage).
- JWT includes `sub` (user id) and `jti` (token id) for auditing.

### Account Holders
- `GET /v1/account-holders` — list account holders (pagination)
- `GET /v1/account-holders/{id}` — retrieve by id

### Accounts
- `POST /v1/accounts` — create account for holder
- `GET /v1/accounts/{id}` — retrieve account details

### Transactions
- `POST /v1/transactions` — create deposit/withdrawal

### Transfers
- `POST /v1/transfers` — transfer between accounts

### Cards
- `POST /v1/cards` — issue a card for an account
- `GET /v1/cards/{id}` — retrieve card details

### Statements
- `GET /v1/statements/{account_id}` — statement summary + transactions

### Health
- `GET /v1/health` — readiness check, includes DB connectivity

### Common Behaviors
- Pagination for list endpoints: `?limit=` and `?offset=`.
- Error envelope: `{ "error": { "code": "...", "message": "...", "details": {...} } }`.
- Consistent status codes: 200/201/204 for success, 400/401/403/404/409 for client errors, 500 for server errors.

## Data Model (MVP)
- **User**: `id`, `email`, `hashed_password`, `created_at`
- **AccountHolder**: `id`, `user_id`, `first_name`, `last_name`, `dob`, `created_at`
- **Account**: `id`, `holder_id`, `type`, `currency`, `balance`, `status`, `created_at`
- **Transaction**: `id`, `account_id`, `type`, `amount`, `currency`, `created_at`
- **Transfer**: `id`, `from_account_id`, `to_account_id`, `amount`, `currency`, `created_at`
- **Card**: `id`, `account_id`, `type`, `last4`, `status`, `created_at`

Constraints:
- Balances never go below zero for withdrawal/transfer.
- Transfers are atomic and recorded as two transactions.
- Monetary amounts stored as integers in minor units (e.g., cents).

## Logging & Monitoring
- Use structlog JSON logs with fields: `timestamp`, `level`, `event`, `request_id`, `user_id` (if available), `route`, `method`, `status_code`, `duration_ms`.
- Correlation ID middleware generates/propagates `X-Request-Id`.
- Exceptions logged with stack traces and structured context.

## Health & Readiness
- `GET /v1/health` checks: app ok + database connectivity (simple `SELECT 1`).
- On startup, service must verify DB connectivity and fail fast if unhealthy.

## Configuration
Environment variables (validated):
- `APP_ENV` (dev/test/prod)
- `DATABASE_URL`
- `JWT_SECRET` (required in production; app fails fast if unset)
- `LOG_LEVEL`
- `CORS_ORIGINS`

Notes:
- `JWT_SECRET` must be explicitly set when `APP_ENV` is `prod`/`production`.

## Testing Strategy (Test-Driven Development (TDD))
- Red‑Green‑Refactor for each feature.
- Unit tests for service/business logic.
- Integration tests for API endpoints and DB behavior.
- Coverage report with minimum 92% target.

## Containerization
- Multi‑stage Dockerfile.
- `docker-compose.yml` for local dev, SQLite volume mounted.

## Documentation Deliverables
- `README.md` with setup, env vars, run/test, API usage.
- `SECURITY.md` with security considerations.
- `ROADMAP.md` for future improvements.
- `AI_USAGE.md` documenting AI prompts, iterations, and learnings.

## Bonus Deliverables (Test client + simple frontend)
### Test client application (integration demo flow)
- Location: `tests/integration/test_demo_flow.py`
- Flow: signup → login → create two accounts → deposit → transfer → statement.
- Endpoints used:
  - `POST /v1/auth/signup`
  - `POST /v1/auth/login`
  - `POST /v1/accounts`
  - `POST /v1/transactions` (deposit)
  - `POST /v1/transfers`
  - `GET /v1/statements/{account_id}`
- Checks:
  - Auth tokens returned and used for protected routes.
  - Deposit increases balance.
  - Transfer decreases source and increases destination.
  - Statement includes expected transactions.

### CLI demo client (interactive + config-driven)
- Location: `scripts/demo_client.py`
- Interactive mode prompts for base URL, user info, and amounts.
- Config mode accepts a JSON sequence of steps.

### Simple frontend interface (static)
- Location: `frontend/` (static HTML/JS/CSS).
- Minimal screens: signup/login, multi-user selector, token expiry display,
  refresh prompt + manual refresh button, create account, deposit, withdrawal,
  transfer, statement view.
- Auth: store access + refresh tokens in memory only (avoid localStorage).
- Deployment: serve from same origin or configure CORS.

## Future Frontend (recommended upgrade)
Use a production-grade Vite + React client:
- Typed API client (OpenAPI or hand-typed models).
- Auth state management with in-memory tokens and refresh handling.
- Environment-based `BASE_URL` and build-time config.
- CI build + lint; deploy as static assets behind a reverse proxy.

## Git Workflow
- Conventional commits (e.g., `feat:`, `fix:`, `test:`, `docs:`).
- Small, frequent commits tied to completed tests.
- Do not commit generated secrets or `.env` files.
