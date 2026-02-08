import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


def _build_engine():
    """
    - Production: DATABASE_URL -> Postgres (Supabase) 
    - Tests/Local: ברירת מחדל sqlite://
      * check_same_thread=False כי TestClient עובד עם threads
      * StaticPool ל-sqlite:// כדי לשמור DB אחד בזיכרון לכל הבקשות בטסטים
    """
    database_url = os.getenv("DATABASE_URL") or "sqlite://"

    connect_args = {}
    engine_kwargs = {"echo": False}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if database_url in ("sqlite://", "sqlite:///:memory:"):
            engine_kwargs["poolclass"] = StaticPool

    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)


engine = _build_engine()


def init_db():
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
