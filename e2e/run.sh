#!/usr/bin/env bash
set -euo pipefail

E2E_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$E2E_DIR")"

cleanup() {
  echo "Tearing down docker compose..."
  docker compose -f "$E2E_DIR/docker-compose.yml" down -v --remove-orphans
}

docker compose -f "$E2E_DIR/docker-compose.yml" down -v --remove-orphans 2>/dev/null || true

trap cleanup EXIT

echo "Starting docker compose..."
docker compose -f "$E2E_DIR/docker-compose.yml" up -d --build --wait

echo "Running e2e tests..."
cd "$ROOT_DIR"
uv run --with pytest --with pytest-asyncio pytest -vv --maxfail 1 e2e/
