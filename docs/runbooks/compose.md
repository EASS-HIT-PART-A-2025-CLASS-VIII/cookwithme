# Runbook — Docker Compose (CookWithMe)

This runbook explains how to run the full stack locally using Docker Compose:
- FastAPI backend
- Streamlit frontend
- Redis
- Worker 

---

## Prerequisites

- Docker + Docker Compose installed
- `.env` exists at repository root

Example `.env`:
```env
DATABASE_URL=postgresql://postgres:<PASSWORD>@<PROJECT>.supabase.co:6543/postgres?sslmode=require

JWT_SECRET=change_me
JWT_EXPIRE_MINUTES=60

REDIS_URL=redis://redis:6379/0

SEED_DATA=false
```

---

## 🚀 Start the stack

From repository root:
```bash
docker compose up --build
```

**Open:**
- Backend swagger: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501

**Start in background:**
```bash
docker compose up -d --build
docker compose ps
```

---

## 🛑 Stop and cleanup

**Stop containers:**
```bash
docker compose down
```

**Full reset** (removes volumes too):
```bash
docker compose down -v
```

---

## 🌱 Seed data

### Strategy

Seed runs only if:
- `SEED_DATA=true`
- and DB has no recipes yet

### Run seed 

1. Set `SEED_DATA=true` in `.env`
2. Start stack:
```bash
   docker compose up --build
```
3. Afterwards set `SEED_DATA=false`

---

## ✅ Verify Redis

**Check Redis is up:**
```bash
docker compose ps
```

**Ping Redis:**
```bash
docker compose exec redis redis-cli ping
```

**Inspect keys:**
```bash
docker compose exec redis redis-cli keys '*'
```

---

## ✅ Verify backend health
```bash
curl -s http://localhost:8000/docs > /dev/null && echo OK
```

**Check logs:**
```bash
docker compose logs -f backend
```

---

## ✅ Verify frontend connectivity

Frontend calls backend using internal DNS:
- `API_BASE_URL=http://backend:8000`

**If frontend fails to fetch:**
```bash
docker compose logs -f frontend
```

---

## 🔧 Worker

If using a worker service:
```bash
docker compose logs -f worker
```

---

## 🧪 Run tests in Docker 

**If you have a test service/container:**
```bash
docker compose run --rm backend-test
```

**Or run in backend container:**
```bash
docker compose exec backend pytest -q
```

---

## 🐛 Troubleshooting

### 1) Recommendations endpoint fails with Redis connection refused

**Symptom:**
- backend logs: `Error 111 connecting to localhost:6379`

**Cause:**
- backend is trying `localhost` inside container (wrong)

**Fix:**
- Set `REDIS_URL=redis://redis:6379/0`
- Ensure backend uses that env var

---

### 2) /auth/login crashes with bcrypt errors

**Fix:**
- Pin bcrypt / passlib versions in requirements.txt
- Rebuild images:
```bash
  docker compose build --no-cache
  docker compose up
```

---

### 3) Static files not loading (images)

When accessing the application from a browser, static files must always be referenced via:

- `http://localhost:8000/static/...`

Docker internal hostnames (e.g. `backend`) are not accessible from the browser.

---

## 🎬 Demo Script
```bash
#!/usr/bin/env bash
set -e

echo "1) Starting stack..."
docker compose up -d --build

echo "2) Waiting for backend..."
until curl -s http://localhost:8000/docs >/dev/null; do
  sleep 1
done
echo "✅ Backend OK."

echo ""
echo "🌐 Open these URLs:"
echo "   - Backend:  http://localhost:8000/docs"
echo "   - Frontend: http://localhost:8501"

echo ""
echo "📋 Demo flow:"
echo "   - Login as admin"
echo "   - Create recipe"
echo "   - View recipes list"
echo "   - Add favorite"
echo "   - Open AI Recommendations"

echo ""
echo "✅ Done."
```

**Save as:** `scripts/demo.sh`

**Make executable:**
```bash
chmod +x scripts/demo.sh
```

**Run:**
```bash
./scripts/demo.sh
```