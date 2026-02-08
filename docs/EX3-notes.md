markdown# EX3 Notes — CookWithMe

## Overview

CookWithMe is a local full-stack microservices project built as the final EX3 assignment.

The system includes:
- **FastAPI backend** — recipes, reviews, highlights, favorites, authentication
- **Streamlit frontend** — user interface for browsing recipes, favorites, highlights, and AI recommendations
- **PostgreSQL (Supabase)** — main persistence layer via `DATABASE_URL`
- **Redis** — caching + idempotency for recommendations
- **Async recommendation logic** — Redis-backed, safe to retry

Everything runs locally using **Docker Compose**.

---

## Architecture

### Services

#### 1. Backend (FastAPI)
- REST API built with FastAPI + SQLModel
- JWT authentication
- Role-based authorization (`admin` / `user`)
- Reads/writes data to PostgreSQL (Supabase)
- Uses Redis for:
  - Recommendation cache
  - Idempotency / safety on repeated calls

#### 2. Frontend (Streamlit)
- Connects to backend via `API_BASE_URL`
- JWT stored in Streamlit `session_state`
- Main features:
  - Login / Register
  - Browse recipes
  - Favorites
  - Highlights
  - AI-based recommendations

#### 3. Redis
- Cache layer for recommendations
- Prevents duplicate recomputation
- Used defensively (backend fails gracefully if Redis unavailable)

#### 4. Worker (Async Refresh Service)
- Runs as a separate Docker service
- Periodically executes `scripts/refresh.py`
- Uses Redis for:
  - distributed locking
  - idempotency
- Safe to restart (no duplicate work)
---

## Persistence & Database

### Database
- Uses **PostgreSQL via Supabase**
- Configured by `DATABASE_URL`
- SQLModel used as ORM

### Important behavior
- Whether running via:
  - `uvicorn` locally, or
  - `docker compose up`
- If `DATABASE_URL` points to Supabase → **all data is stored in Supabase**

This is intentional and documented.

### API Contract Testing
Schemathesis can be run against the OpenAPI spec to validate API contracts and edge cases:
schemathesis run http://localhost:8000/openapi.json
---

## Seeding Strategy

### Goal
Seed initial recipes **once**, without duplicating data on every run.

### Implementation
- Seed logic is executed on startup.
- Seed runs **only if**:
  - `SEED_DATA=true`
  - AND the database is empty (`select(Recipe).limit(1)`)

### Recommended usage
- Run once with `SEED_DATA=true`
- Afterwards:
  - Either set `SEED_DATA=false`
  - Or leave it enabled (seed is idempotent)

---
### Refresh Job Evidence

Example worker log:
```text
[2026-02-05T18:12:03Z] 🔄 Refresh ran | views=42 recipes=18
```

## Manual execution 

The refresh job can also be executed manually, outside Docker.

### Run once
```bash
python scripts/refresh.py
```

### Run in loop mode
```bash
python scripts/refresh.py --loop
```

This is useful for local development and debugging without Docker Compose.

---

## Testing Strategy

### Running tests

Run all backend tests locally:
```bash
pytest -q
```

Run tests inside Docker:
```bash
docker compose exec backend pytest -q
```

## Authentication & Security (Session 11)

### Password Handling
- Passwords are hashed using `passlib + bcrypt`
- Minimum length enforced

### JWT Tokens
Issued by `/auth/login` with payload:
- `sub` — user ID
- `role` — `admin` or `user`
- `name` — display name
- `exp` — expiration timestamp

### Role-based Authorization
Admin-only endpoints:
- Create / Update / Delete recipes
- Create / Delete highlights

User endpoints:
- Favorites
- Reviews (delete only own reviews)

### Enforcement
- `get_current_user` validates token
- `require_admin` blocks non-admin users

## Demo Script

A guided local demo is provided:

scripts/demo.sh

The script:
- Starts the full Docker Compose stack
- Waits for backend readiness
- Guides the reviewer through the core flows
---

## Security Tests

The test suite includes:
- ❌ Missing token → 401
- ❌ Expired token → 401
- ❌ User token on admin endpoint → 403
- ✅ Valid user token → allowed on user endpoints
- ✅ Admin role present in JWT payload

These tests live in `test_security.py`.

### Authorization Guards

Protected endpoints enforce role-based access control:

- Admin-only routes are guarded by `require_admin`
- User routes validate ownership (e.g. deleting own reviews only)

Authorization is enforced at request time and verified by automated tests.

---

## Redis & Recommendations

### Usage
Redis is used for:
- Caching recommendation results
- Preventing duplicate work via idempotency keys

### Behavior
- Backend checks Redis before recomputing recommendations
- If cache exists → return cached result
- If Redis is unavailable → backend fails gracefully

### Keys
- `reco_cache:*` — cached recommendations
- TTL applied to avoid stale data

---

## Enhancement Features

Implemented enhancements (non-complex, graded positively):
- Favorites per user
- Ratings + average rating per recipe
- Highlights
- AI recommendations
- Search/filter logic (frontend)

Each enhancement is covered by API or integration tests.

---

### Backend Test Coverage

### Backend Tests
- CRUD for recipes
- Validation errors (422)
- Not-found errors (404)
- Authorization & role enforcement
- Token expiration behavior

### Database
- Tests run on **in-memory SQLite**
- Uses `StaticPool`
- Schema reset before every test

---

## Docker & Local Execution

### Required services
- backend
- frontend
- redis
- worker (async refresh service)

All started via:
```bash
docker compose up --build
```

---

## 🔧 Environment

`.env` file controls:
- `DATABASE_URL`
- `JWT_SECRET`
- `SEED_DATA`
- Redis connection

---

## ⚠️ Known Limitations

- Supabase storage URLs require valid bucket permissions
- Redis is optional; when unavailable, the backend degrades gracefully without caching.
- No external cloud deployment — local only (by design)

---