from pathlib import Path

from fastapi.testclient import TestClient

from app.core import config as app_config
from app.db import session as db_session
from app.main import create_app
from tests.integration.utils import configure_test_db


def test_auto_migrate_creates_schema(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AUTO_MIGRATE", "1")
    configure_test_db(tmp_path, monkeypatch, "auto-migrate")
    app_config.get_settings.cache_clear()
    db_session.get_engine.cache_clear()

    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "demo@example.com",
                "password": "supersecure123",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "dob": "1990-01-01",
            },
        )
        assert response.status_code == 201
