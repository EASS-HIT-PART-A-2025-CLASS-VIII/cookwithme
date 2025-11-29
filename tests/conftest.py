import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import database

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

database.engine = test_engine

from app.main import app

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.drop_all(bind=test_engine)
    SQLModel.metadata.create_all(bind=test_engine)
    yield

@pytest.fixture
def client():
    return TestClient(app)