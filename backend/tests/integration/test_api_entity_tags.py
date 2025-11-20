import pytest


def test_add_tag_to_entity(client):
    """Test adding a tag to an existing entity."""
    # Create a tag
    tag_response = client.post("/api/tags/", json={"name": "test-tag"})
    tag_id = tag_response.json()["id"]

    # Create an entity
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "TagTest Corp",
            "city": "TagCity",
            "country": "Tag Country",
            "type": "Company",
            "description": "Entity for tag testing",
        },
    )
    entity_id = entity_response.json()["id"]

    # Add tag to entity
    response = client.post(f"/api/entities/{entity_id}/tags/{tag_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tags"]) > 0
    assert any(tag["id"] == tag_id for tag in data["tags"])


def test_remove_tag_from_entity(client):
    """Test removing a tag from an entity."""
    # Create a tag
    tag_response = client.post("/api/tags/", json={"name": "remove-tag"})
    tag_id = tag_response.json()["id"]

    # Create an entity
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "RemoveTag Corp",
            "city": "RemoveCity",
            "country": "Remove Country",
            "type": "Company",
            "description": "Entity for tag removal testing",
        },
    )
    entity_id = entity_response.json()["id"]

    # Add tag to entity first
    client.post(f"/api/entities/{entity_id}/tags/{tag_id}")

    # Remove tag from entity
    response = client.delete(f"/api/entities/{entity_id}/tags/{tag_id}")
    assert response.status_code == 200
    data = response.json()
    assert not any(tag["id"] == tag_id for tag in data["tags"])


def test_add_duplicate_tag_to_entity_idempotent(client):
    """Test that adding the same tag to an entity multiple times is idempotent."""
    # Create a tag
    tag_response = client.post("/api/tags/", json={"name": "duplicate-tag"})
    tag_id = tag_response.json()["id"]

    # Create an entity
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DuplicateTag Corp",
            "city": "DuplicateCity",
            "country": "Duplicate Country",
            "type": "Company",
            "description": "Entity for duplicate tag testing",
        },
    )
    entity_id = entity_response.json()["id"]

    # Add tag to entity twice
    client.post(f"/api/entities/{entity_id}/tags/{tag_id}")
    response = client.post(f"/api/entities/{entity_id}/tags/{tag_id}")
    assert response.status_code == 200  # Should succeed idempotently


def test_remove_nonexistent_tag_from_entity_idempotent(client):
    """Test that removing a tag that isn't associated with an entity is idempotent."""
    # Create a tag
    tag_response = client.post("/api/tags/", json={"name": "nonexistent-tag"})
    tag_id = tag_response.json()["id"]

    # Create an entity
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "NoTag Corp",
            "city": "NoTagCity",
            "country": "NoTag Country",
            "type": "Company",
            "description": "Entity with no tags",
        },
    )
    entity_id = entity_response.json()["id"]

    # Try to remove tag that was never added
    response = client.delete(f"/api/entities/{entity_id}/tags/{tag_id}")
    assert response.status_code == 200  # Should succeed idempotently
