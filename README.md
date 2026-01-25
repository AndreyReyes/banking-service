# Banking Service

## Implementation Plan

This project is built using incremental TDD milestones and quality gates.

See [MILESTONES.md](./MILESTONES.md) for the full test checkpoint + commit plan.
See [DEPENDENCIES.md](./DEPENDENCIES.md) for dependency rationale.

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
- `JWT_SECRET` (required in production; app fails fast if unset)
- `CORS_ORIGINS`

Notes:
- In production (`APP_ENV=prod`/`production`), `JWT_SECRET` must be set to a non-default value.

## Tests

```bash
pytest
```

Coverage is enforced at 92% for the `app` package. For optional Docker smoke
tests, set `RUN_DOCKER_TESTS=1` and ensure Docker + Docker Compose are
installed.

Docker requirements:
- Docker Engine 29.1.5+ (tested on Ubuntu 24.04).
- Docker Compose v5.0.1+ via `docker compose`.

## Run the app

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

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

## Bonus: Demo client + frontend

This project includes specs for a demo flow that exercises the API end-to-end,
plus a minimal frontend for showcasing the flow.

### Integration demo flow (test client)
- Target file: `tests/integration/test_demo_flow.py`
- Flow: signup → login → create two accounts → deposit → transfer → statement
- Run (when implemented):
  - `pytest tests/integration/test_demo_flow.py`

### CLI demo client (interactive + config-driven)
- Target file: `scripts/demo_client.py`
- Interactive mode prompts for base URL, user details, and amounts
- Config mode accepts a JSON sequence of steps
- Run (when implemented):
  - `python scripts/demo_client.py --interactive`
  - `python scripts/demo_client.py --config scripts/demo_flow.json`

### Simple frontend interface
- Target folder: `frontend/` (static HTML/JS/CSS)
- Features: signup/login, create account, deposit, transfer, view statement
- Notes: keep tokens in memory; use same-origin proxy or enable CORS as needed
