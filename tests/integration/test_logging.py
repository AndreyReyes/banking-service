import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.core import config as app_config
from app.db import session as db_session
from app.main import create_app


def _configure_test_db(tmp_path: Path, monkeypatch) -> None:
    db_file = tmp_path / "logging.db"
    database_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    app_config.get_settings.cache_clear()
    db_session.get_engine.cache_clear()


def _extract_request_log(stdout: str) -> dict:
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("event") == "request.completed":
            return payload
    raise AssertionError("request.completed log entry not found")


def test_request_id_generated_and_logged(tmp_path: Path, monkeypatch, capsys) -> None:
    _configure_test_db(tmp_path, monkeypatch)
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/v1/health")

    assert response.headers.get("X-Request-Id")
    captured = capsys.readouterr()
    payload = _extract_request_log(captured.out)
    assert payload["request_id"] == response.headers["X-Request-Id"]
    assert payload["status_code"] == 200
    assert payload["method"] == "GET"
    assert payload["path"] == "/v1/health"
