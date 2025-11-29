from sqlmodel import SQLModel, create_engine
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'recipes.db')}"

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    import app.models
    SQLModel.metadata.create_all(engine)