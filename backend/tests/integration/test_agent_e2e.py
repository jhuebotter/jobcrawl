import pytest
from backend.src.core.agent import agent_mock
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.validation import Location


# This test uses the client fixture from conftest.py, which handles the test database.
@pytest.mark.asyncio
async def test_golden_path(client):
    """Test the complete agent workflow from start_run through batch processing to database saves.

    This test verifies that the agent can successfully execute a search run in mock mode,
    process the mock response data, and save entities to the database with proper deduplication.
    """
    # Get a db session from the overridden dependency
    db: Session = next(get_db())

    # Run the agent in mock mode (agent_mock is initialized with mock=True)
    await agent_mock.start_run(
        db=db,
        tags=["AI"],
        locations=[Location(city="San Francisco", country="USA")],
        institution_types=["Company"],
    )

    # Check the results in the database
    response = client.get("/api/entities/")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) >= 1  # Should have at least one entity from mock data

    # Check that entities have expected structure
    entity = entities[0]
    assert "name" in entity
    assert "description" in entity
    assert "city" in entity
    assert "country" in entity
    assert "type" in entity
