from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import configure_test_db


def test_frontend_static_assets_served(tmp_path: Path, monkeypatch) -> None:
    configure_test_db(tmp_path, monkeypatch, "frontend-static")
    app = create_app()

    with TestClient(app) as client:
        index_response = client.get("/")
        assert index_response.status_code == 200
        assert "Banking Service Demo" in index_response.text

        script_response = client.get("/app.js")
        assert script_response.status_code == 200
        assert "const state" in script_response.text
