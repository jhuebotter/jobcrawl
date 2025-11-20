import pytest


def test_create_entity_alias(client):
    """Test creating an alias for an existing entity."""
    # Create an entity first
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "AliasTest Corp",
            "city": "AliasCity",
            "country": "Alias Country",
            "type": "Company",
            "description": "Entity for alias testing",
        },
    )
    entity_id = entity_response.json()["id"]

    # Create an alias
    alias_data = {"entity_id": entity_id, "alias": "AliasTest Inc"}
    response = client.post("/api/entity-aliases/", json=alias_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alias"] == "AliasTest Inc"
    assert data["entity_id"] == entity_id


def test_read_entity_aliases(client):
    """Test reading the list of entity aliases."""
    # Create an entity and alias first
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "ReadAlias Corp",
            "city": "ReadCity",
            "country": "Read Country",
            "type": "Company",
            "description": "Entity for reading aliases",
        },
    )
    entity_id = entity_response.json()["id"]

    client.post(
        "/api/entity-aliases/", json={"entity_id": entity_id, "alias": "ReadAlias Inc"}
    )

    # Read aliases
    response = client.get("/api/entity-aliases/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(alias["alias"] == "ReadAlias Inc" for alias in data)


def test_read_single_entity_alias(client):
    """Test reading a single entity alias by ID."""
    # Create an entity and alias first
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "SingleAlias Corp",
            "city": "SingleCity",
            "country": "Single Country",
            "type": "Company",
            "description": "Entity for single alias reading",
        },
    )
    entity_id = entity_response.json()["id"]

    alias_response = client.post(
        "/api/entity-aliases/",
        json={"entity_id": entity_id, "alias": "SingleAlias Inc"},
    )
    alias_id = alias_response.json()["id"]

    # Read single alias
    response = client.get(f"/api/entity-aliases/{alias_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alias_id
    assert data["alias"] == "SingleAlias Inc"


def test_delete_entity_alias(client):
    """Test deleting an entity alias."""
    # Create an entity and alias first
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DeleteAlias Corp",
            "city": "DeleteCity",
            "country": "Delete Country",
            "type": "Company",
            "description": "Entity for alias deletion",
        },
    )
    entity_id = entity_response.json()["id"]

    alias_response = client.post(
        "/api/entity-aliases/",
        json={"entity_id": entity_id, "alias": "DeleteAlias Inc"},
    )
    alias_id = alias_response.json()["id"]

    # Delete alias
    response = client.delete(f"/api/entity-aliases/{alias_id}")
    assert response.status_code == 200

    # Verify it's gone
    response = client.get(f"/api/entity-aliases/{alias_id}")
    assert response.status_code == 404


def test_create_duplicate_alias_fails(client):
    """Test that creating duplicate aliases fails."""
    # Create an entity and alias first
    entity_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DuplicateAlias Corp",
            "city": "DuplicateCity",
            "country": "Duplicate Country",
            "type": "Company",
            "description": "Entity for duplicate alias testing",
        },
    )
    entity_id = entity_response.json()["id"]

    client.post(
        "/api/entity-aliases/",
        json={"entity_id": entity_id, "alias": "DuplicateAlias Inc"},
    )

    # Try to create the same alias again
    response = client.post(
        "/api/entity-aliases/",
        json={"entity_id": entity_id, "alias": "DuplicateAlias Inc"},
    )
    assert response.status_code == 400


def test_create_alias_for_nonexistent_entity_fails(client):
    """Test that creating an alias for a non-existent entity fails."""
    alias_data = {
        "entity_id": 99999,  # Non-existent entity ID
        "alias": "NonExistent Corp",
    }
    response = client.post("/api/entity-aliases/", json=alias_data)
    assert response.status_code == 404
