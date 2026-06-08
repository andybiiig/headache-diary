#!/bin/sh
set -eu

echo "Applying database migrations..."
alembic upgrade head

echo "Starting development server with hot-reload..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --app-dir /app/src
