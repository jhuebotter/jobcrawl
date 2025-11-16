import pytest
from unittest.mock import patch
from backend.src.core.agent import agent
from sqlalchemy.orm import Session
from backend.src.core.db import get_db

# This test uses the client fixture from conftest.py, which handles the test database.
def test_golden_path(client):
    # Get a db session from the overridden dependency
    db: Session = next(get_db())

    with patch("backend.src.core.scraping.Scraper.retrieve_content") as mock_retrieve, \
         patch("backend.src.core.scraping.Scraper.get_page_content") as mock_get_content, \
         patch("backend.src.core.provider.LLMProvider.generate") as mock_generate:

        # Mock the external services
        mock_retrieve.return_value = ["http://example.com/test"]
        mock_get_content.return_value = "This is a test page about Test Corp."
        mock_generate.side_effect = [
            "test query",  # For search query generation
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
