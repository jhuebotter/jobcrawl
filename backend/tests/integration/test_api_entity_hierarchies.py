import pytest


def test_create_entity_hierarchy(client):
    """Test creating a parent-child relationship between entities."""
    # Create parent entity
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "Parent Corp",
            "city": "HierarchyCity",
            "country": "Hierarchy Country",
            "type": "Company",
            "description": "Parent entity",
        },
    )
    parent_id = parent_response.json()["id"]

    # Create child entity
    child_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "Child Corp",
            "city": "HierarchyCity",
            "country": "Hierarchy Country",
            "type": "Company",
            "description": "Child entity",
        },
    )
    child_id = child_response.json()["id"]

    # Create hierarchy relationship
    hierarchy_data = {"parent_id": parent_id, "child_id": child_id}
    response = client.post("/api/entity-hierarchies/", json=hierarchy_data)
    assert response.status_code == 200
    data = response.json()
    assert data["parent_id"] == parent_id
    assert data["child_id"] == child_id


def test_read_entity_hierarchies(client):
    """Test reading the list of entity hierarchies."""
    # Create entities and hierarchy first
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "ReadParent Corp",
            "city": "ReadHierarchyCity",
            "country": "ReadHierarchy Country",
            "type": "Company",
            "description": "Parent entity for reading",
        },
    )
    parent_id = parent_response.json()["id"]

    child_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "ReadChild Corp",
            "city": "ReadHierarchyCity",
            "country": "ReadHierarchy Country",
            "type": "Company",
            "description": "Child entity for reading",
        },
    )
    child_id = child_response.json()["id"]

    client.post(
        "/api/entity-hierarchies/", json={"parent_id": parent_id, "child_id": child_id}
    )

    # Read hierarchies
    response = client.get("/api/entity-hierarchies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(h["parent_id"] == parent_id and h["child_id"] == child_id for h in data)


def test_read_single_entity_hierarchy(client):
    """Test reading a single entity hierarchy by ID."""
    # Create entities and hierarchy first
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "SingleParent Corp",
            "city": "SingleHierarchyCity",
            "country": "SingleHierarchy Country",
            "type": "Company",
            "description": "Parent entity for single reading",
        },
    )
    parent_id = parent_response.json()["id"]

    child_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "SingleChild Corp",
            "city": "SingleHierarchyCity",
            "country": "SingleHierarchy Country",
            "type": "Company",
            "description": "Child entity for single reading",
        },
    )
    child_id = child_response.json()["id"]

    hierarchy_response = client.post(
        "/api/entity-hierarchies/", json={"parent_id": parent_id, "child_id": child_id}
    )
    hierarchy_id = hierarchy_response.json()["id"]

    # Read single hierarchy
    response = client.get(f"/api/entity-hierarchies/{hierarchy_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == hierarchy_id
    assert data["parent_id"] == parent_id
    assert data["child_id"] == child_id


def test_delete_entity_hierarchy(client):
    """Test deleting an entity hierarchy relationship."""
    # Create entities and hierarchy first
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DeleteParent Corp",
            "city": "DeleteHierarchyCity",
            "country": "DeleteHierarchy Country",
            "type": "Company",
            "description": "Parent entity for deletion",
        },
    )
    parent_id = parent_response.json()["id"]

    child_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DeleteChild Corp",
            "city": "DeleteHierarchyCity",
            "country": "DeleteHierarchy Country",
            "type": "Company",
            "description": "Child entity for deletion",
        },
    )
    child_id = child_response.json()["id"]

    hierarchy_response = client.post(
        "/api/entity-hierarchies/", json={"parent_id": parent_id, "child_id": child_id}
    )
    hierarchy_id = hierarchy_response.json()["id"]

    # Delete hierarchy
    response = client.delete(f"/api/entity-hierarchies/{hierarchy_id}")
    assert response.status_code == 200

    # Verify it's gone
    response = client.get(f"/api/entity-hierarchies/{hierarchy_id}")
    assert response.status_code == 404


def test_create_duplicate_hierarchy_fails(client):
    """Test that creating duplicate hierarchy relationships fails."""
    # Create entities and hierarchy first
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DuplicateParent Corp",
            "city": "DuplicateHierarchyCity",
            "country": "DuplicateHierarchy Country",
            "type": "Company",
            "description": "Parent entity for duplicate testing",
        },
    )
    parent_id = parent_response.json()["id"]

    child_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "DuplicateChild Corp",
            "city": "DuplicateHierarchyCity",
            "country": "DuplicateHierarchy Country",
            "type": "Company",
            "description": "Child entity for duplicate testing",
        },
    )
    child_id = child_response.json()["id"]

    client.post(
        "/api/entity-hierarchies/", json={"parent_id": parent_id, "child_id": child_id}
    )

    # Try to create the same hierarchy again
    response = client.post(
        "/api/entity-hierarchies/", json={"parent_id": parent_id, "child_id": child_id}
    )
    assert response.status_code == 400


def test_create_hierarchy_with_nonexistent_entity_fails(client):
    """Test that creating a hierarchy with non-existent entities fails."""
    # Create one entity
    parent_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "ExistParent Corp",
            "city": "ExistCity",
            "country": "Exist Country",
            "type": "Company",
            "description": "Existing parent entity",
        },
    )
    parent_id = parent_response.json()["id"]

    # Try to create hierarchy with non-existent child
    hierarchy_data = {
        "parent_id": parent_id,
        "child_id": 99999,  # Non-existent entity ID
    }
    response = client.post("/api/entity-hierarchies/", json=hierarchy_data)
    assert response.status_code == 404
