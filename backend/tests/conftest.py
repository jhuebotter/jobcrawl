import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.src.main import app
from backend.src.core.db import Base, get_db

# Ensure all models are registered on Base before create_all()
import backend.src.models.schema as _models  # noqa: F401

# Use a single, shared in-memory connection
TEST_DB_URL = "sqlite://"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

# Override the global SessionLocal and engine to use the test ones
from backend.src.core import db as db_module

db_module.SessionLocal = TestingSessionLocal
db_module.engine = engine


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply dependency override once
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def _testing_env():
    # prevent prod DB initializer from running during tests
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)


@pytest.fixture(scope="function", autouse=True)
def _reset_db():
    # clean slate per test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
