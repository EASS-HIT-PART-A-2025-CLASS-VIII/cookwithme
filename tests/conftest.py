import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import database
from app.main import app
from app.models import User, UserRole

# ------------------------
# Test database (SQLite in-memory)
# ------------------------

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

database.engine = test_engine


@pytest.fixture(autouse=True)
def setup_db():
    """Create clean DB before every test"""
    SQLModel.metadata.drop_all(bind=test_engine)
    SQLModel.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def client():
    if hasattr(database, "get_session"):
        def override_get_session():
            with Session(test_engine) as session:
                yield session

        app.dependency_overrides[database.get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ------------------------
# Auth helpers
# ------------------------

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def register_user(client: TestClient, email: str, password: str, name="Test User"):
    res = client.post(
        "/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert res.status_code in (201, 409)
    return res


def login_user(client: TestClient, email: str, password: str) -> str:
    res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def promote_user_to_admin(email: str):
    """Promote existing user to admin directly in DB"""
    with Session(database.engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        assert user is not None
        user.role = UserRole.admin
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


# ------------------------
# Fixtures: tokens & headers
# ------------------------

@pytest.fixture
def user_token(client: TestClient) -> str:
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    register_user(client, email, password, "User")
    return login_user(client, email, password)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"
    register_user(client, email, password, "Admin")
    promote_user_to_admin(email)
    return login_user(client, email, password)


@pytest.fixture
def user_headers(user_token: str):
    return auth_headers(user_token)


@pytest.fixture
def admin_headers(admin_token: str):
    return auth_headers(admin_token)