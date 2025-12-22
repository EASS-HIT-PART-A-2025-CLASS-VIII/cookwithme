from sqlmodel import SQLModel, create_engine, Session
import os

# 📁 מיקום קבוע לדאטה בתוך הקונטיינר (מחובר ל-Docker volume)
DATA_DIR = "/app/data"
DB_PATH = os.path.join(DATA_DIR, "recipes.db")

# יוצרים תיקייה אם לא קיימת
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def init_db():
    import app.models  # חשוב לטעינת הטבלאות
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session