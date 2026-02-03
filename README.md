# Banking Service

## TLDR

```bash
sudo ./scripts/install_prereqs.sh
./scripts/setup_env.sh
./scripts/run_app.sh --env dev --mode native
```

## Implementation Plan

This project is built using incremental Test-Driven Development (TDD)
milestones and quality gates.

See [MILESTONES.md](./MILESTONES.md) for the full test checkpoint + commit plan.
See [DEPENDENCIES.md](./DEPENDENCIES.md) for dependency rationale.
See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.
See [WORKFLOW.md](./WORKFLOW.md) for the git workflow.
See [API.md](./API.md) for API endpoints and docs entrypoints.
See [LICENSE](./LICENSE) for usage and evaluation-only terms.

## Commit hygiene

- Keep commits focused to one logical change; prefer 3–5 files max.
- Commit after each passing test or functional slice.
- Split cross-cutting work into separate commits or PRs.
- Follow TDD: commit failing tests before implementation.

## Tech Stack

| Component | Library/Tool | Purpose | Version |
| --- | --- | --- | --- |
| Language | Python | Runtime | 3.12 |
| API Framework | FastAPI | REST API layer | 0.128.0 |
| ASGI Server | Uvicorn | Application server | 0.40.0 |
| Validation | Pydantic | Schemas and data validation | 2.12.5 |
| Settings | Pydantic Settings | Environment configuration | 2.12.0 |
| Logging | Structlog | JSON structured logging | 25.5.0 |
| ORM | SQLAlchemy | DB access + portability | 2.0.46 |
| Migrations | Alembic | Schema migrations | 1.18.1 |
| Testing | Pytest | Test runner | 9.0.2 |
| Coverage Plugin | pytest-cov | Coverage gate for tests | 7.0.0 |
| HTTP Client | HTTPX | Integration testing | 0.28.1 |
| Coverage | Coverage.py | Coverage reporting | 7.13.1 |
| Linting | Ruff | Linting | 0.14.14 |
| Formatting | Black | Code formatting | 26.1.0 |
| Typing | Mypy | Static type checks | 1.19.1 |

## Setup

On a minimal Ubuntu install, ensure `python3-venv` is available first:

```bash
sudo ./scripts/install_prereqs.sh
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Or run the setup helper:

```bash
./scripts/setup_env.sh
```

## Environment

Set environment variables before running the app or tests:

- `APP_ENV` (dev/test/prod)
- `DATABASE_URL`
- `LOG_LEVEL`
- `AUTO_MIGRATE` (defaults to true in dev, false in test/prod)
- `JWT_SECRET` (required in production; app fails fast if unset)
- `CORS_ORIGINS`

Notes:
- In production (`APP_ENV=prod`/`production`), `JWT_SECRET` must be set to a non-default value.
- In production, `AUTO_MIGRATE` must be disabled (defaults to false).

### Dev vs production behavior
- **dev** (default when `APP_ENV` is unset):
  - `AUTO_MIGRATE=true` by default to apply Alembic migrations on startup.
  - Intended for local development and demo usage.
- **test**:
  - Used by the test suite (set in tests) to keep behavior predictable.
  - `AUTO_MIGRATE=false` unless explicitly enabled for a test.
- **prod/production**:
  - Requires a non-default `JWT_SECRET`.
  - `AUTO_MIGRATE` must be disabled (enforced).

### Where to set it
- Local shell: `export APP_ENV=dev` (or `prod`) before running `uvicorn`.
- Docker: pass `-e APP_ENV=dev` (or `prod`) in `docker run` / compose.
- CI or deployment: set `APP_ENV` in your environment or secrets manager.

## Tests

```bash
pytest
```

Coverage is enforced at 92% for the `app` package. For optional Docker smoke
tests, set `RUN_DOCKER_TESTS=1` and ensure Docker + Docker Compose are
installed.

## CI/CD

GitHub Actions runs on pushes and PRs to `master` with these checks:

```bash
ruff check .
pytest
```

Notes:
- Black and mypy are intentionally deferred until cleanup (see `ROADMAP.md`).

Docker requirements:
- Docker Engine 29.1.5+ (tested on Ubuntu 24.04).
- Docker Compose v5.0.1+ via `docker compose`.

## Run the app

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Or use the run helper:

```bash
./scripts/run_app.sh --env dev --mode native
```

Modes and environments supported:
- `--env dev|test|prod|production`
- `--mode native|docker|compose`

## Run with Docker

```bash
docker build -t banking-service:local .
docker run --rm -p 8000:8000 \
  -e APP_ENV=dev \
  -e DATABASE_URL=sqlite:///./data/banking.db \
  -e LOG_LEVEL=INFO \
  -e JWT_SECRET=dev_insecure_secret_change_me \
  -v banking_data:/app/data \
  banking-service:local
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Deploy to Render (GitHub)

This repo includes a `render.yaml` Blueprint for a Docker-based deployment that
serves both the API and the static frontend from the same service.

### Steps
- In Render, create a new service from this GitHub repo and select the
  `render.yaml` Blueprint to run the Docker-based service.
- Configure required secrets:
  - `JWT_SECRET` (must be a non-default value in production).
- The Blueprint configures a persistent disk at `/app/data` and sets
  `DATABASE_URL=sqlite:////app/data/banking.db`.
- After the first deploy, open the Render shell for the service and run:
  - `alembic upgrade head`

### Notes
- `AUTO_MIGRATE` is disabled in production for safety; migrations are run
  manually via the Render shell.
- The health check path is `/v1/health`.

### Automated migrations (production)
If you are using Render's Python runtime (non-Docker) and do not have shell
access, configure the start command to run migrations before the server:
- Start command:
  - `sh -c "PYTHONPATH=/opt/render/project/src alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`
- Keep `APP_ENV=production` and `AUTO_MIGRATE=false` so only this explicit
  startup step runs migrations.

## Bonus: Demo client + frontend

This project includes a demo flow that exercises the API end-to-end, plus a
minimal frontend for showcasing the flow.

### Integration demo flow (test client)
- Target file: `tests/integration/test_demo_flow.py`
- Flow: signup → login → create two accounts → deposit → transfer → statement
- Run:
  - `pytest tests/integration/test_demo_flow.py`

### CLI demo client (interactive + config-driven)
- Target file: `scripts/demo_client.py`
- Interactive mode prompts for base URL, user details, and amounts
- Config mode accepts a JSON sequence of steps with `save_as` references
- Run:
  - `python scripts/demo_client.py --interactive`
  - `python scripts/demo_client.py --config scripts/demo_flow.json`

### Simple frontend interface
- Target folder: `frontend/` (static HTML/JS/CSS)
- Features: signup/login, multi-user selector, token expiry display, refresh prompt,
  create account, deposit, withdrawal, transfer, view statement
- Run (same-origin, no CORS):
  - `uvicorn app.main:app --reload`
  - Open `http://localhost:8000` (frontend served by API)
- Run (separate static server):
  - `python -m http.server --directory frontend 8081`
  - Open `http://localhost:8081` and set base URL to the API
- Notes: tokens are stored in memory only for the demo (including refresh tokens);
  use same-origin proxy or enable CORS as needed
