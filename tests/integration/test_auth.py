from datetime import date
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.core import config as app_config
from app.core import security
from app.db import session as db_session
from app.db.models import AuditLog, RefreshToken, User
from app.main import create_app


def _configure_test_db(tmp_path: Path, monkeypatch) -> str:
    db_file = tmp_path / "auth.db"
    database_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    app_config.get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    return database_url


def _apply_migrations(database_url: str) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "app/db/migrations")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def _signup(client: TestClient, email: str, password: str) -> None:
    response = client.post(
        "/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "first_name": "Ada",
            "last_name": "Lovelace",
            "dob": "1990-01-01",
        },
    )
    assert response.status_code == 201


def test_signup_creates_user_and_holder(tmp_path: Path, monkeypatch) -> None:
    database_url = _configure_test_db(tmp_path, monkeypatch)
    _apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        _signup(client, "ada@example.com", "supersecure123")

    SessionLocal = db_session.get_sessionmaker()
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == "ada@example.com").one()
        assert user.hashed_password != "supersecure123"
        assert security.verify_password("supersecure123", user.hashed_password)


def test_login_returns_tokens_and_me_requires_auth(tmp_path: Path, monkeypatch) -> None:
    database_url = _configure_test_db(tmp_path, monkeypatch)
    _apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        _signup(client, "ada@example.com", "supersecure123")

        login_response = client.post(
            "/v1/auth/login",
            headers={"X-Device-Id": "device-123"},
            json={"email": "ada@example.com", "password": "supersecure123"},
        )

        assert login_response.status_code == 200
        login_payload = login_response.json()
        assert login_payload["access_token"]
        assert login_payload["refresh_token"]

        me_response = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {login_payload['access_token']}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "ada@example.com"

        unauthenticated = client.get("/v1/auth/me")
        assert unauthenticated.status_code == 401


def test_failed_login_persists_audit_log(tmp_path: Path, monkeypatch) -> None:
    database_url = _configure_test_db(tmp_path, monkeypatch)
    _apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/auth/login",
            headers={"X-Device-Id": "device-abc"},
            json={"email": "missing@example.com", "password": "supersecure123"},
        )

    assert response.status_code == 401

    SessionLocal = db_session.get_sessionmaker()
    with SessionLocal() as session:
        audit_log = (
            session.query(AuditLog)
            .filter(AuditLog.event_type == "login", AuditLog.status == "failure")
            .one()
        )
        assert audit_log.meta["email"] == "missing@example.com"


def test_signup_rejects_overlong_password(tmp_path: Path, monkeypatch) -> None:
    database_url = _configure_test_db(tmp_path, monkeypatch)
    _apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "ada@example.com",
                "password": "a" * 73,
                "first_name": "Ada",
                "last_name": "Lovelace",
                "dob": "1990-01-01",
            },
        )

    assert response.status_code == 422


def test_refresh_rotates_token_and_logs_audit(tmp_path: Path, monkeypatch) -> None:
    database_url = _configure_test_db(tmp_path, monkeypatch)
    _apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        _signup(client, "ada@example.com", "supersecure123")

        login_response = client.post(
            "/v1/auth/login",
            headers={"X-Device-Id": "device-xyz"},
            json={"email": "ada@example.com", "password": "supersecure123"},
        )
        login_payload = login_response.json()
        refresh_token = login_payload["refresh_token"]

        refresh_response = client.post(
            "/v1/auth/refresh",
            headers={"X-Device-Id": "device-xyz"},
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200
        rotated_payload = refresh_response.json()
        assert rotated_payload["refresh_token"] != refresh_token

        reuse_response = client.post(
            "/v1/auth/refresh",
            headers={"X-Device-Id": "device-xyz"},
            json={"refresh_token": refresh_token},
        )
        assert reuse_response.status_code == 401

    SessionLocal = db_session.get_sessionmaker()
    with SessionLocal() as session:
        refresh_rows = (
            session.query(RefreshToken)
            .join(User)
            .filter(User.email == "ada@example.com")
            .all()
        )
        assert any(token.revoked_at is not None for token in refresh_rows)

        audit_logs = (
            session.query(AuditLog)
            .join(User)
            .filter(User.email == "ada@example.com", AuditLog.event_type == "login")
            .all()
        )
        assert audit_logs
        assert audit_logs[0].device_id == "device-xyz"
