import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlmodel import Session, select

from app.auth_jwt import SECRET_KEY, ALGORITHM
from app.database import engine
from app.models import User, UserRole


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def register_user(client, email: str, password: str, name: str = "Test User"):
    res = client.post(
        "/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert res.status_code in (201, 409)
    return res


def login_user(client, email: str, password: str) -> str:
    res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def promote_user_to_admin(email: str):
    """Promote an existing user to admin in the test DB."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        assert user is not None, "User must exist before promotion"
        user.role = UserRole.admin  # enum
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_user_and_token(client):
    email = f"user_{uuid.uuid4().hex[:10]}@example.com"
    password = "StrongPass123!"
    register_user(client, email, password, name="Test User")
    token = login_user(client, email, password)
    return token


def create_admin_and_token(client):
    email = f"admin_{uuid.uuid4().hex[:10]}@example.com"
    password = "StrongPass123!"
    register_user(client, email, password, name="Admin User")
    promote_user_to_admin(email)  # ✅ make DB role admin
    token = login_user(client, email, password)
    return token


def create_expired_token(sub: str = "999", role: str = "admin"):
    payload = {
        "sub": sub,
        "role": role,
        "name": "Expired User",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ----------------------------
# Tests
# ----------------------------

def test_admin_endpoint_requires_token(client):
    """POST /recipes without token → 401"""
    recipe = {
        "title": "NoAuth",
        "ingredients": ["A"],
        "instructions_md": "## test",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/x.jpg",
    }

    res = client.post("/recipes", json=recipe)
    assert res.status_code == 401


def test_admin_endpoint_user_forbidden(client):
    """User token on admin endpoint → 403"""
    user_token = create_user_and_token(client)

    recipe = {
        "title": "Forbidden",
        "ingredients": ["A"],
        "instructions_md": "## test",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/x.jpg",
    }

    res = client.post("/recipes", json=recipe, headers=auth_headers(user_token))
    assert res.status_code == 403


def test_admin_can_create_recipe(client):
    """Admin (DB role) can POST /recipes → 201"""
    admin_token = create_admin_and_token(client)

    recipe = {
        "title": "AdminCreated",
        "ingredients": ["A"],
        "instructions_md": "## test",
        "time_minutes": 10,
        "difficulty": "Easy",
        "image_url": "https://example.com/x.jpg",
    }

    res = client.post("/recipes", json=recipe, headers=auth_headers(admin_token))
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "AdminCreated"


def test_expired_token_rejected(client):
    """Expired JWT on protected route → 401"""
    expired_token = create_expired_token(role="admin")

    res = client.get("/favorites", headers=auth_headers(expired_token))
    assert res.status_code == 401


def test_user_can_access_protected_route(client):
    """Valid user token can access /favorites"""
    user_token = create_user_and_token(client)

    res = client.get("/favorites", headers=auth_headers(user_token))
    assert res.status_code == 200


def test_token_contains_role_claim():
    """JWT payload contains role (claim exists)"""
    token = jwt.encode(
        {
            "sub": "1",
            "role": "admin",
            "name": "Admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    decoded = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False},
    )

    assert decoded["role"] == "admin"
    assert "sub" in decoded