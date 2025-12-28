import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")

# allow tests without env
if not DATABASE_URL:
    DATABASE_URL = "sqlite://"

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

def init_db():
    import app.models
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session