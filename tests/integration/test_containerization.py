import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = PROJECT_ROOT / "Dockerfile"
COMPOSE_PATH = PROJECT_ROOT / "docker-compose.yml"


def test_dockerfile_is_multistage() -> None:
    assert DOCKERFILE_PATH.exists(), "Dockerfile is missing"
    contents = DOCKERFILE_PATH.read_text(encoding="utf-8")
    from_lines = [line for line in contents.splitlines() if line.strip().lower().startswith("from ")]
    assert len(from_lines) >= 2, "Dockerfile should use multi-stage builds"
    assert "as builder" in contents.lower(), "Dockerfile should include a builder stage"
    assert "as runtime" in contents.lower(), "Dockerfile should include a runtime stage"


def test_compose_has_healthcheck_and_env_config() -> None:
    assert COMPOSE_PATH.exists(), "docker-compose.yml is missing"
    contents = COMPOSE_PATH.read_text(encoding="utf-8")
    assert "services:" in contents, "docker-compose.yml should define services"
    assert "healthcheck:" in contents, "docker-compose.yml should include a healthcheck"
    assert "/v1/health" in contents, "Healthcheck should hit /v1/health"
    assert "DATABASE_URL" in contents, "docker-compose.yml should define DATABASE_URL"
    assert "JWT_SECRET" in contents, "docker-compose.yml should define JWT_SECRET"


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def _docker_compose_available() -> bool:
    if not _docker_available():
        return False
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            cwd=PROJECT_ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return True


@pytest.mark.skipif(
    os.getenv("RUN_DOCKER_TESTS") != "1" or not _docker_available(),
    reason="Set RUN_DOCKER_TESTS=1 and install Docker to run",
)
def test_container_builds() -> None:
    subprocess.run(
        ["docker", "build", "-t", "banking-service:local", "."],
        cwd=PROJECT_ROOT,
        check=True,
    )


@pytest.mark.skipif(
    os.getenv("RUN_DOCKER_TESTS") != "1" or not _docker_compose_available(),
    reason="Set RUN_DOCKER_TESTS=1 and install Docker Compose to run",
)
def test_compose_starts_health_endpoint() -> None:
    env = {**os.environ, "COMPOSE_PROJECT_NAME": "banking_service_test"}
    subprocess.run(
        ["docker", "compose", "up", "-d", "--build", "--wait", "--wait-timeout", "30"],
        cwd=PROJECT_ROOT,
        check=True,
        env=env,
    )
    try:
        with urlopen("http://localhost:8000/v1/health", timeout=2) as response:
            assert response.status == 200
    finally:
        subprocess.run(["docker", "compose", "down", "-v"], cwd=PROJECT_ROOT, env=env, check=False)
