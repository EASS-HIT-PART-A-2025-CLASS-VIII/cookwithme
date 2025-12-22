#!/bin/sh
set -e

export PYTHONPATH=/app

echo "⏳ Initializing database..."
python -c "from app.database import init_db; init_db()"

echo "🌱 Running seed data..."
python -m app.seed.seed_data

echo "🚀 Starting API..."
exec "$@"