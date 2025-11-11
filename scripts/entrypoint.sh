#!/usr/bin/env bash
set -e

echo "Starting entrypoint..."

if [ "${MIGRATE_ON_START:-true}" = "true" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
  echo "Migrations OK."
else
  echo "Skipping migrations (MIGRATE_ON_START=false)."
fi

exec "$@"
