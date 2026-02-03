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

APP_ENV="dev"
MODE="native"

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
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
    export APP_ENV="${APP_ENV}"
    export DATABASE_URL="${DATABASE_URL:-sqlite:///./data/banking.db}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    export JWT_SECRET="${JWT_SECRET:-dev_insecure_secret_change_me}"
    uvicorn app.main:app --reload
    ;;
  docker)
    docker build -t banking-service:local .
    docker run --rm -p 8000:8000 \
      -e APP_ENV="${APP_ENV}" \
      -e DATABASE_URL="${DATABASE_URL:-sqlite:///./data/banking.db}" \
      -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
      -e JWT_SECRET="${JWT_SECRET:-dev_insecure_secret_change_me}" \
      -v banking_data:/app/data \
      banking-service:local
    ;;
  compose)
    export APP_ENV="${APP_ENV}"
    docker compose up --build
    ;;
  *)
    echo "Invalid --mode value: ${MODE}" >&2
    usage
    exit 1
    ;;
esac
