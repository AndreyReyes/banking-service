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

## Run the app

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```
