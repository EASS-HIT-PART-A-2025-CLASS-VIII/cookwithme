# 🍽️ CookWithMe — Full Stack Recipe Management

CookWithMe is a recipe management system featuring a **FastAPI backend** and a modern **Streamlit frontend**.

The project was developed as part of an academic assignment to demonstrate **proper API design, data validation, separation of concerns, and full-stack integration**.

---

## 📖 Overview

CookWithMe provides a complete solution for managing cooking recipes.
This platform is designed to present my personal, original recipes. 


## ✨ Main Features

### 🧩 Backend & Database
- FastAPI + SQLModel REST API
- Full CRUD for recipes, reviews, and highlights
- PostgreSQL (Supabase) in production
- SQLite (in-memory) for tests only
- Strong validation with Pydantic

### 🖥️ Frontend (Streamlit)
- Visual recipe book with card-based layout
- Add, edit, and delete recipes (admin only)
- Image uploads with preview
- Star-based reviews
- Instagram-style cooking highlights
- Filter recipes by difficulty

## ➕ Extra Features

* ⭐ **Star ratings & averages** – Users can rate recipes (1–5 stars), with average rating displayed per recipe
* 🎬 **Instagram-style highlights** - Short cooking videos and stories
* 🔍 **Smart filtering** - Search recipes by name 
* 🎯 **Smart filtering** - Difficulty-based filtering 

### 🔐 Authentication & Authorization
- JWT-based authentication
- User roles: **admin** and **user**
- Admin-only access to recipe and highlight management
- Users can add and delete their own reviews
- Admins can delete any review
- Favorites are stored per user

## 🔄 Background Services

### Redis
Redis is used for:
- Caching AI recommendation results
- Preventing duplicate recomputation
- Distributed locking and idempotency

### Background Worker
A background worker periodically runs an async refresh job:
- Executes `scripts/refresh.py`
- Uses Redis for locking and retries
- Safe to restart (no duplicate work)


## 🚀 Run Locally

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (Backend + Frontend)
pip install -r requirements.txt
```

### 2. Start the Backend (API)
Open **Terminal 1** and start the FastAPI backend:
```bash
export $(cat .env | xargs)
uvicorn app.main:app --reload
```

*API is now running at: `http://127.0.0.1:8000`*

#### Note:  
When running locally (without Docker), the backend still connects to the same
PostgreSQL (Supabase) database via the `DATABASE_URL` environment variable.
This ensures full data persistence across environments.

### 3. Start the Frontend (UI)
Open a **new terminal** (with the venv activated) and run:
```bash
streamlit run streamlit_app.py
```

👉 **The UI will open in your browser automatically.**

---

### 🌱 Seed Data

A seed script is included to populate the database with initial recipes.
Seed data is loaded automatically on startup when `SEED_DATA=true`.

---

## 🧪 Testing

The project includes a comprehensive test suite:

* ✅ Isolated in-memory database tests (no production DB access)

### Running Tests

#### Option 1: Using Docker (recommended)
```bash
docker compose run --rm backend-test
```

### Option 2: Local (requires DATABASE_URL)
```bash
export DATABASE_URL=sqlite://
pytest -q
```

---

## 📡 API Endpoints

### 🍲 Recipes
| Method | Endpoint | Description |
|------|--------|------------|
| POST | `/recipes` | Create recipe (with image support) |
| GET | `/recipes` | Get all recipes |
| GET | `/recipes/{id}` | Get recipe by ID |
| PUT | `/recipes/{id}` | Update recipe |
| DELETE | `/recipes/{id}` | Delete recipe |

### ⭐ Reviews
| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/recipes/{id}/reviews` | Get recipe reviews |
| POST | `/recipes/{id}/reviews` | Add a review to a recipe |

### 🎬 Highlights
| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/highlights` | Get cooking highlights |
| POST | `/highlights` | Create highlight |
| DELETE | `/highlights/{id}` | Delete highlight |

### ❤️ Favorites
| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/favorites` | Get user's favorite recipes |
| POST | `/favorites/{recipe_id}` | Add recipe to favorites |
| DELETE | `/favorites/{recipe_id}` | Remove recipe from favorites |

### 🔐 Authentication
| Method | Endpoint | Description |
|------|--------|------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and receive JWT |

---

## 🐳 Run with Docker Compose 

The project includes Dockerfiles and `docker-compose.yml` for a production-like environment,
including the FastAPI backend, Streamlit frontend, Redis, and an optional background worker.
The database is initialized automatically and seed data is loaded on first run.


### Environment Variables

Create a `.env` file:
```env
DATABASE_URL=postgresql://postgres:<PASSWORD>@<PROJECT>.supabase.co:6543/postgres?sslmode=require
```
### Run
```
docker compose up --build
docker compose run --rm backend-test
```

### Services
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501
- Redis: internal service (cache & locks)
- Worker: background refresh service
---


## 👨‍🍳 Personal Note

This project serves not only as a full-stack engineering assignment, but also as a digital recipe book containing my own original recipes, developed and refined over the years.
All recipes, photos, and cooking methods included here are my original creations and are protected by copyright.  
They are shared for viewing and inspiration only, and may not be copied, redistributed, or used commercially without permission.

---

## 👤 Author

**Yahav Ben Hur**  
📧 yahavbenhur@gmail.com
