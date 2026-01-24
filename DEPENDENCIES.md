# Dependencies

This document explains why each dependency is included for a production-grade
banking service. Versions are pinned in `requirements.txt` and dev/test tooling
is managed in `requirements-dev.txt`.

## Runtime dependencies

- **FastAPI**: High-performance REST framework with strong async support and
  Pydantic integration for validated request/response models.
- **Uvicorn**: Production-grade ASGI server for FastAPI with HTTP/1.1 support
  and efficient event loop handling.
- **Pydantic**: Robust data validation and serialization for schemas, settings,
  and API contracts.
- **Pydantic Settings**: Typed environment configuration with defaults and
  validation to prevent misconfiguration in production.
- **Structlog**: Structured JSON logging to support observability, correlation
  IDs, and consistent log fields across services.
- **SQLAlchemy**: Mature ORM and SQL toolkit that keeps SQLite and Postgres
  portability while enabling explicit transactions.
- **Alembic**: Schema migration management to safely evolve the database over
  time with auditability.

## Development and testing tools

- **Pytest**: Reliable test runner with rich fixtures for unit and integration
  testing.
- **pytest-cov**: Coverage enforcement via pytest to gate CI and local runs.
- **HTTPX**: Modern HTTP client used for integration tests against the FastAPI
  app.
- **Coverage**: Test coverage reporting to enforce quality gates.
- **Ruff**: Fast linting to catch correctness and style issues early.
- **Black**: Opinionated formatter to ensure consistent code style.
- **Mypy**: Static type checking for safer refactors and clearer interfaces.
