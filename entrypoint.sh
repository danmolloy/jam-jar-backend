#!/bin/sh
set -e

# Wait for Postgres if DB_HOST and DB_PORT defined
if [ -n "$DB_HOST" ] && command -v nc >/dev/null 2>&1; then
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  until nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
    sleep 1
  done
fi

# Ensure logs directory exists for Django file logging in DEBUG
mkdir -p /app/logs

# Run migrations and collectstatic in non-debug
python manage.py migrate --noinput

if [ "$DEBUG" != "True" ] && [ "$DEBUG" != "true" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"



