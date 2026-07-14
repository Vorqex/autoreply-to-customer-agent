#!/usr/bin/env bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting AutoReply AI backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
