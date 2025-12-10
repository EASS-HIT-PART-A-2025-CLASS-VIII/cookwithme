# 🍽️ CookWithMe — Full Stack Recipe Management

CookWithMe is a recipe management system featuring a **FastAPI backend** and a modern **Streamlit frontend**.

The project was developed as part of an academic assignment to demonstrate **proper API design, data validation, separation of concerns, and full-stack integration**.

---

## 📖 Overview

CookWithMe provides a complete solution for managing cooking recipes:

- **Backend:** REST API using **FastAPI**, **SQLModel**, and SQLite.
- **Frontend:** Interactive web interface built with **Streamlit**.
- **Features:** Image uploads, auto-validation, and responsive recipe cards.
- **Reliability:** Comprehensive automated testing with **pytest**.

---

## ✨ Main Features

### 🧩 API (Backend)
- Full **CRUD** endpoints under `/recipes`.
- **Image Handling:** Supports Base64 image storage and processing via **Pillow**.
- Strong validation using **Pydantic** (enums, length checks).
- Proper HTTP status codes (201, 404, 422).

### 🖥️ UI (Frontend)
- **Visual Recipe Book:** View recipes as designed cards with difficulty badges.
- **Interactive Forms:** Add and edit recipes with real-time feedback.
- **Image Uploads:** Drag-and-drop support for recipe photos.
- **Filtering:** Filter recipes by difficulty level.

### 🗄️ Database
- **SQLite** persistence for production use.
- **In-memory SQLite** used during automated testing (absolute isolation).
- Automatic table creation via SQLModel metadata.

---

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
Run the server in one terminal:
```bash
uvicorn app.main:app --reload
```

*API is now running at: `http://127.0.0.1:8000`*

### 3. Start the Frontend (UI)
Open a **new terminal** (with the venv activated) and run:
```bash
streamlit run streamlit_app.py
```

👉 **The UI will open in your browser automatically.**

---

## 🌱 Seed Data

The project includes a seed script that populates the database with sample recipes (e.g., Falafel, Pizza, Pasta).

* **Local Development:** Run manually with:
```bash
python seed/seed_data.py
```
* **Docker:** Runs **automatically** on container startup.

---

## 🧪 Testing

The project includes a comprehensive test suite:

* ✅ Tests use an in-memory database
* ✅ Production DB is never touched
* ✅ Seed data is NOT loaded during tests

**Run all tests:**
```bash
pytest -q
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes` | Create recipe (with image support) |
| GET | `/recipes` | Get all recipes |
| GET | `/recipes/{id}` | Get by ID |
| PUT | `/recipes/{id}` | Update recipe |
| DELETE | `/recipes/{id}` | Delete recipe |

---

## 🐳 Run with Docker

The project includes a `Dockerfile` and `entrypoint.sh` for a production-ready setup.

**When running in Docker:**
1. The database is initialized automatically.
2. **Seed data is loaded automatically** (so you start with a populated DB).
3. The API starts on port 8000.

### Build and Run

1. Build the image:
```bash
docker build -t cookwithme .
```

2. Run the container:
```bash
docker run -p 8000:8000 cookwithme
```

The API will start and automatically load sample data.

3. Run the UI (Locally):

Since the Dockerfile currently runs the API, run the UI locally to connect to it:
```bash
streamlit run streamlit_app.py
```

---

## 👤 Author

**Yahav Ben Hur**  
📧 yahavbenhur@gmail.com
