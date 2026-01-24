from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import apply_migrations, configure_test_db


def _setup_app(tmp_path: Path, monkeypatch) -> TestClient:
    database_url = configure_test_db(tmp_path, monkeypatch, "errors")
    apply_migrations(database_url)
    app = create_app()
    return TestClient(app)


def test_validation_error_envelope(tmp_path: Path, monkeypatch) -> None:
    with _setup_app(tmp_path, monkeypatch) as client:
        response = client.post(
            "/v1/auth/signup",
            json={
                "password": "supersecure123",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "dob": "1990-01-01",
            },
        )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"]
    assert isinstance(payload["error"].get("details"), list)


def test_auth_error_envelope(tmp_path: Path, monkeypatch) -> None:
    with _setup_app(tmp_path, monkeypatch) as client:
        response = client.get("/v1/auth/me")

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "unauthorized"
    assert payload["error"]["message"] == "Unauthorized"
