"""Shared pytest fixtures."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["USE_AI_STUB"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"

from database import Base, get_db
from main import app
from models import User, Task, TaskStatus
from services.auth import hash_password

TEST_DB_URL = "sqlite://"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@test.com",
        username="testadmin",
        hashed_password=hash_password("adminpass"),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db):
    user = User(
        email="user@test.com",
        username="testuser",
        hashed_password=hash_password("userpass"),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    resp = client.post("/auth/token", data={"username": "testadmin", "password": "adminpass"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def user_token(client, regular_user):
    resp = client.post("/auth/token", data={"username": "testuser", "password": "userpass"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
