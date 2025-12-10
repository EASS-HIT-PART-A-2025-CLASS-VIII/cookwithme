#!/bin/sh
set -e

export PYTHONPATH=/app

echo "⏳ Initializing database..."
python -c "from app.database import init_db; init_db()"

echo "🌱 Running seed data..."
python seed/seed_data.py

echo "🚀 Starting API..."
exec "$@"