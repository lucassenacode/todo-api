#!/usr/bin/env bash
set -e

echo "Starting entrypoint…"

# espere o Postgres (opcional se já usa healthcheck no compose)
# until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
#   echo "Postgres ainda não respondeu, tentando de novo…"
#   sleep 2
# done

if [ "${MIGRATE_ON_START:-true}" = "true" ]; then
  echo "Running Alembic migrations…"
  alembic upgrade head
  echo "Migrations OK."
else
  echo "Skipping migrations (MIGRATE_ON_START=false)."
fi

echo "Executing CMD: $*"
exec "$@"
