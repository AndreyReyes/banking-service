from pathlib import Path

from fastapi.testclient import TestClient

from app.core import config as app_config
from app.db import session as db_session
from app.main import create_app


def _configure_test_db(tmp_path: Path, monkeypatch) -> str:
    db_file = tmp_path / "health.db"
    database_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    app_config.get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    return database_url


def test_health_endpoint_returns_expected_schema(tmp_path: Path, monkeypatch) -> None:
    _configure_test_db(tmp_path, monkeypatch)
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
    assert "timestamp" in payload
