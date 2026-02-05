#!/usr/bin/env sh
set -e

echo "⏳ Initializing database..."
python -c "from app.database import init_db; init_db()"

echo "🌱 Running seed if needed (safe)..."
python -c "from app.seed.seed_data import run_seed; run_seed()"

# worker / custom command
if [ "$#" -gt 0 ]; then
  echo "🧰 Running command: $*"
  exec "$@"
fi

echo "🚀 Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000