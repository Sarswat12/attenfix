#!/bin/sh
# entrypoint.sh - run migrations and start the server
set -e

# Ensure FLASK_APP is set for flask CLI
if [ -z "$FLASK_APP" ]; then
  export FLASK_APP=run.py
fi

# Run database migrations if alembic is configured
if [ -f "/app/migrations/env.py" ]; then
  echo "Running database migrations..."
  # Try to run alembic upgrade head (if alembic.ini exists)
  if [ -f "/app/alembic.ini" ] || [ -d "/app/migrations" ]; then
    python -m flask db upgrade || echo "alembic upgrade failed or not configured"
  fi
fi

# Start gunicorn (the CMD in Dockerfile provides arguments)
exec "$@"
