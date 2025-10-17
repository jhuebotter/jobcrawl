import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.main import create_app
from backend.src.core.db import Base
from backend.src.api import tags, runs

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def app():
    Base.metadata.create_all(bind=engine)
    app = create_app()
    app.dependency_overrides[tags.get_db] = override_get_db
    app.dependency_overrides[runs.get_db] = override_get_db
    yield app
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)