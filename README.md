# 🍽️ CookWithMe — Recipe Management REST API

CookWithMe is a clean, fully-tested **backend REST API** built with **FastAPI** and **SQLModel** for managing cooking recipes.

The project was developed as part of an academic backend assignment (EX1) and demonstrates **proper API design, data validation, separation of concerns, and automated testing**.

---

## 📖 Overview

CookWithMe provides a realistic backend setup for recipe management:

- REST API using **FastAPI**
- Database modeling with **SQLModel**
- SQLite persistence
- Full **CRUD** operations
- Strong validation using **Pydantic** (via SQLModel)
- Automated tests with **pytest**
- Clean separation between **production** and **test** databases

---

## ✨ Main Features

### 🧩 API
- Full CRUD endpoints under `/recipes`
- JSON-based request & response models
- Proper HTTP status codes (201, 404, 422, etc.)

### ✅ Validation
- Field validation handled automatically by **Pydantic**
- Minimum length checks for text fields
- Enum validation for difficulty levels
- Invalid payloads rejected with `422`

### 🗄️ Database
- SQLite persistence for production use
- **In-memory SQLite** used during testing
- Absolute isolation between test DB and production DB
- Automatic table creation via SQLModel metadata

### 🧪 Testing
- 20 automated tests using **pytest**
- Covers:
  - Create
  - Read (all / by ID)
  - Update
  - Delete
  - Validation & error cases
- Each test runs on a clean, isolated database

---

### 🌱 Optional Seed Data

The project includes an **optional database seed script** that inserts sample recipes
(e.g. Falafel, Margherita Pizza, Pasta alla Vodka, Greek Salad, Shakshuka).

- Executed manually for demonstration purposes
- Not used during automated tests
- Keeps production, demo, and test data fully separated

By default, the API starts with an empty database.

The seed script is **not executed automatically** and is intended
for **manual demo purposes only**.

To insert sample recipes locally:

```bash
python seed/seed_data.py
```
When running with **Docker**, the seed can be executed inside the running container using the following command:

```bash
docker exec -e PYTHONPATH=/app <container_id> python seed/seed_data.py
```
**Note:** Automated tests and production startup always begin with a clean, empty database.

---

### 🐳 Docker Support

- Dockerfile included
- Enables running the API in an isolated environment
- No local Python setup required

---

## 📂 Project Structure

```text
cookwithme/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── crud.py
│   └── database.py
│
├── seed/
│   └── seed_data.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   ├── test_delete.py
│   └── test_validation.py
│
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## 🧪 Automated Tests

**Run all tests:**

```bash
pytest -q
```
Expected output:

> 20 passed in X.XXs

* **✅ Tests use an in-memory database**
* **✅ Production DB is never touched**
* **✅ No seed data is loaded**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/recipes` | Create recipe |
| **GET** | `/recipes` | Get all recipes |
| **GET** | `/recipes/{id}` | Get by ID |
| **PUT** | `/recipes/{id}` | Update recipe |
| **DELETE** | `/recipes/{id}` | Delete recipe |

---

## 🚀 Run Locally

1.  **(Optional) Create virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the API:**
    ```bash
    uvicorn app.main:app --reload
    ```
4.  **Open Swagger UI:**
    👉 `http://127.0.0.1:8000/docs`

---

## 🐳 Run with Docker (Optional)

1.  **Build the image:**
    ```bash
    docker build -t cookwithme .
    ```
2.  **Run the container:**
    ```bash
    docker run -p 8000:8000 cookwithme
    ```
3.  **Access Swagger UI:**
    👉 `http://127.0.0.1:8000/docs`

---

## 👤 Author

**Yahav Ben Hur**
📧 yahavbenhur@gmail.com
