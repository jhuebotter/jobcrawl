import pytest
from unittest.mock import patch
from backend.src.core.agent import Agent
from backend.tests.conftest import override_get_db, engine
from backend.src.main import create_app
from backend.src.core.db import Base
from backend.src.api import tags, runs
from fastapi.testclient import TestClient

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

@pytest.fixture
def agent_with_db(client): # client fixture sets up the db
    db = next(override_get_db())
    try:
        yield Agent(), db
    finally:
        db.close()

@patch("backend.src.core.scraping.Scraper.retrieve_content")
@patch("backend.src.core.scraping.Scraper.get_page_content")
@patch("backend.src.core.provider.LLMProvider.generate")
def test_golden_path(mock_generate, mock_get_page_content, mock_retrieve_content, agent_with_db, client):
    agent, db = agent_with_db
    # Mock the external services
    mock_retrieve_content.return_value = ["http://example.com/test"]
    mock_get_page_content.return_value = "This is a test page about Test Corp."
    mock_generate.side_effect = [
        "test query", # For search query generation
        '{"name": "Test Corp", "summary": "A test company.", "website": "http://example.com", "city": "Testville", "country": "Testland", "confidence": 0.9}'
    ]

    # Run the agent
    agent.start_run(db=db, tags=["test"], cities=["testville"], institution_types=["test"])

    # Check the results in the database
    response = client.get("/api/entities/")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 1
    assert entities[0]["name"] == "Test Corp"
    assert entities[0]["summary"] == "A test company."
