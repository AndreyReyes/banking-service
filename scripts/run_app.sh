#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/run_app.sh --env dev|test|prod --mode native|docker|compose

Examples:
  ./scripts/run_app.sh --env dev --mode native
  ./scripts/run_app.sh --env test --mode native
  ./scripts/run_app.sh --env prod --mode docker
  ./scripts/run_app.sh --env dev --mode compose
EOF
}

generate_jwt_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 32
    return 0
  fi
  python - <<'PY'
import base64
import os
print(base64.b64encode(os.urandom(32)).decode("utf-8"))
PY
}

run_prod_migrations_native() {
  echo "Running database migrations for prod..."
  alembic upgrade head
}

run_prod_migrations_docker() {
  echo "Running database migrations in Docker for prod..."
  docker run --rm \
    -e APP_ENV="${APP_ENV}" \
    -e DATABASE_URL="${DATABASE_URL}" \
    -e LOG_LEVEL="${LOG_LEVEL}" \
    -e JWT_SECRET="${JWT_SECRET}" \
    -v banking_data:/app/data \
    banking-service:local \
    alembic upgrade head
}

ensure_prod_jwt_secret() {
  if [[ "${APP_ENV}" =~ ^(prod|production)$ ]] && [ "${JWT_SECRET}" = "dev_insecure_secret_change_me" ]; then
    if [ -t 0 ]; then
      read -r -p "JWT_SECRET is not set for prod. Generate one now? [y/N] " reply
      if [[ "${reply}" =~ ^[Yy]$ ]]; then
        JWT_SECRET="$(generate_jwt_secret)"
        export JWT_SECRET
        echo "Generated JWT_SECRET for this session."
        return 0
      fi
    fi
    echo "JWT_SECRET must be set to a non-default value for prod." >&2
    echo "Set JWT_SECRET and re-run, or allow this script to generate one." >&2
    exit 1
  fi
}

APP_ENV="dev"
MODE="native"
CURRENT_USER="${SUDO_USER:-${USER}}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --env)
      APP_ENV="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! "${APP_ENV}" =~ ^(dev|test|prod|production)$ ]]; then
  echo "Invalid --env value: ${APP_ENV}" >&2
  exit 1
fi

case "${MODE}" in
  native)
    if [ ! -d ".venv" ]; then
      echo "Missing .venv. Run ./scripts/setup_env.sh first." >&2
      exit 1
    fi
    mkdir -p "./data"
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
    export APP_ENV="${APP_ENV}"
    export DATABASE_URL="${DATABASE_URL:-sqlite:///./data/banking.db}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    export JWT_SECRET="${JWT_SECRET:-dev_insecure_secret_change_me}"
    ensure_prod_jwt_secret
    if [[ "${APP_ENV}" =~ ^(prod|production)$ ]]; then
      run_prod_migrations_native
      uvicorn app.main:app
    elif [ "${APP_ENV}" = "test" ]; then
      uvicorn app.main:app
    else
      uvicorn app.main:app --reload
    fi
    ;;
  docker)
    if ! command -v docker >/dev/null 2>&1; then
      echo "Docker is not installed. Run ./scripts/install_docker.sh or use --mode native." >&2
      exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
      echo "Cannot access Docker daemon. Add your user to the docker group or use sudo." >&2
      echo "Suggested: sudo usermod -aG docker ${CURRENT_USER} && newgrp docker" >&2
      exit 1
    fi
    DATABASE_URL="${DATABASE_URL:-sqlite:///./data/banking.db}"
    LOG_LEVEL="${LOG_LEVEL:-INFO}"
    export JWT_SECRET="${JWT_SECRET:-dev_insecure_secret_change_me}"
    ensure_prod_jwt_secret
    docker build -t banking-service:local .
    if [[ "${APP_ENV}" =~ ^(prod|production)$ ]]; then
      run_prod_migrations_docker
    fi
    docker run --rm -p 8000:8000 \
      -e APP_ENV="${APP_ENV}" \
      -e DATABASE_URL="${DATABASE_URL}" \
      -e LOG_LEVEL="${LOG_LEVEL}" \
      -e JWT_SECRET="${JWT_SECRET}" \
      -v banking_data:/app/data \
      banking-service:local
    ;;
  compose)
    if ! command -v docker >/dev/null 2>&1; then
      echo "Docker is not installed. Run ./scripts/install_docker.sh or use --mode native." >&2
      exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
      echo "Cannot access Docker daemon. Add your user to the docker group or use sudo." >&2
      echo "Suggested: sudo usermod -aG docker ${CURRENT_USER} && newgrp docker" >&2
      exit 1
    fi
    export APP_ENV="${APP_ENV}"
    docker compose up --build
    ;;
  *)
    echo "Invalid --mode value: ${MODE}" >&2
    usage
    exit 1
    ;;
esac
