from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import config as app_config
from app.core import security
from app.db import session as db_session
from app.db.models import User


def configure_test_db(tmp_path: Path, monkeypatch, name: str) -> str:
    db_file = tmp_path / f"{name}.db"
    database_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    app_config.get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    return database_url


def apply_migrations(database_url: str) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "app/db/migrations")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def signup(client: TestClient, email: str, password: str) -> None:
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


def login(client: TestClient, email: str, password: str) -> dict:
    response = client.post(
        "/v1/auth/login",
        headers={"X-Device-Id": "device-xyz"},
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def create_user(session: Session, email: str, password: str) -> User:
    user = User(email=email, hashed_password=security.hash_password(password))
    session.add(user)
    session.flush()
    return user
