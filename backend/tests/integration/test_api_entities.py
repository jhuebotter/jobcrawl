import pytest


def test_read_entities_empty(client):
    """Test reading entities when database is empty returns empty list."""
    response = client.get("/api/entities/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_entity_autocomplete(client):
    """Test creating a new entity via autocomplete endpoint with curation."""
    entity_data = {
        "name": "TestCo",
        "city": "Testville",
        "country": "Test Country",
        "type": "Company",
        "description": "Test company description",
        "tags": ["tech"],
    }
    response = client.post("/api/entities/autocomplete", json=entity_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestCo"
    assert data["city"] == "Testville"
    assert data["country"] == "Test Country"
    assert data["type"] == "Company"
    assert data["description"] == "Test company description"


def test_read_entity_by_id(client):
    """Test retrieving a single entity by its ID."""
    # Create entity first
    entity_data = {
        "name": "ReadTest Corp",
        "city": "ReadCity",
        "country": "Read Country",
        "type": "Company",
        "description": "Test entity for reading",
    }
    create_response = client.post("/api/entities/autocomplete", json=entity_data)
    entity_id = create_response.json()["id"]

    # Read it back
    response = client.get(f"/api/entities/{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ReadTest Corp"
    assert data["id"] == entity_id


def test_update_entity(client):
    """Test updating an existing entity's information."""
    # Create entity first
    entity_data = {
        "name": "UpdateTest Corp",
        "city": "UpdateCity",
        "country": "Update Country",
        "type": "Company",
        "description": "Original description",
    }
    create_response = client.post("/api/entities/autocomplete", json=entity_data)
    entity_id = create_response.json()["id"]

    # Update it
    update_data = {"name": "Updated Corp", "description": "Updated description"}
    response = client.put(f"/api/entities/{entity_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Corp"
    assert data["description"] == "Updated description"
    assert data["city"] == "UpdateCity"  # Unchanged fields remain


def test_star_entity(client):
    """Test starring an entity."""
    # Create entity first
    entity_data = {
        "name": "StarTest Corp",
        "city": "StarCity",
        "country": "Star Country",
        "type": "Company",
        "description": "Test entity for starring",
    }
    create_response = client.post("/api/entities/autocomplete", json=entity_data)
    entity_id = create_response.json()["id"]

    # Star it
    response = client.post(f"/api/entities/{entity_id}/star")
    assert response.status_code == 204

    # Check it's starred by filtering
    response = client.get("/api/entities/?starred=true")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 1
    assert entities[0]["id"] == entity_id


def test_unstar_entity(client):
    """Test unstarring an entity."""
    # Create and star entity first
    entity_data = {
        "name": "UnstarTest Corp",
        "city": "UnstarCity",
        "country": "Unstar Country",
        "type": "Company",
        "description": "Test entity for unstarring",
    }
    create_response = client.post("/api/entities/autocomplete", json=entity_data)
    entity_id = create_response.json()["id"]

    # Star it
    client.post(f"/api/entities/{entity_id}/star")

    # Unstar it
    response = client.delete(f"/api/entities/{entity_id}/star")
    assert response.status_code == 204

    # Check it's not starred
    response = client.get("/api/entities/?starred=true")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 0


def test_filter_entities_by_tag(client):
    """Test filtering entities by tag association."""
    # Create tags
    tech_tag_response = client.post("/api/tags/", json={"name": "tech"})
    tech_tag_id = tech_tag_response.json()["id"]

    ai_tag_response = client.post("/api/tags/", json={"name": "AI"})
    ai_tag_id = ai_tag_response.json()["id"]

    # Create entities with different tags
    entity1_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "Tech Corp",
            "city": "FilterCity",
            "country": "Filter Country",
            "type": "Company",
            "description": "Tech company",
            "tags": ["tech"],
        },
    )
    entity1_id = entity1_response.json()["id"]

    entity2_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "AI Corp",
            "city": "FilterCity",
            "country": "Filter Country",
            "type": "Company",
            "description": "AI company",
            "tags": ["AI"],
        },
    )
    entity2_id = entity2_response.json()["id"]

    entity3_response = client.post(
        "/api/entities/autocomplete",
        json={
            "name": "TechAI Corp",
            "city": "FilterCity",
            "country": "Filter Country",
            "type": "Company",
            "description": "Tech and AI company",
            "tags": ["tech", "AI"],
        },
    )
    entity3_id = entity3_response.json()["id"]

    # Link tags to entities
    client.post(f"/api/entities/{entity1_id}/tags/{tech_tag_id}")
    client.post(f"/api/entities/{entity2_id}/tags/{ai_tag_id}")
    client.post(f"/api/entities/{entity3_id}/tags/{tech_tag_id}")
    client.post(f"/api/entities/{entity3_id}/tags/{ai_tag_id}")

    # Test filtering by single tag
    response = client.get("/api/entities/?tag=tech")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 2  # Tech Corp and TechAI Corp
    entity_names = [e["name"] for e in entities]
    assert "Tech Corp" in entity_names
    assert "TechAI Corp" in entity_names

    # Test filtering by multiple tags (should use OR logic)
    response = client.get("/api/entities/?tag=tech&tag=AI")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 3  # All entities should be returned (any of tech OR AI)
    entity_names = [e["name"] for e in entities]
    assert "Tech Corp" in entity_names
    assert "AI Corp" in entity_names
    assert "TechAI Corp" in entity_names

    # Test filtering by non-existent tag
    response = client.get("/api/entities/?tag=finance")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_filter_options(client):
    """Test getting all unique filter options"""
    # Create some test data
    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "FilterTest University",
            "city": "Test City",
            "country": "Test Country",
            "type": "University",
            "description": "Test university",
            "tags": ["education", "research"],
        },
    )

    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "FilterTest Company",
            "city": "Another City",
            "country": "Another Country",
            "type": "Company",
            "description": "Test company",
            "tags": ["business"],
        },
    )

    # Test the filter options endpoint
    response = client.get("/api/filters")
    assert response.status_code == 200
    data = response.json()

    # Check that all expected keys are present
    assert "types" in data
    assert "tags" in data
    assert "cities" in data
    assert "countries" in data

    # Check that our test data appears in the options
    assert "University" in data["types"]
    assert "Company" in data["types"]
    assert "education" in data["tags"]
    assert "research" in data["tags"]
    assert "business" in data["tags"]
    assert "Test City" in data["cities"]
    assert "Another City" in data["cities"]
    assert "Test Country" in data["countries"]
    assert "Another Country" in data["countries"]


def test_filter_entities_by_type(client):
    """Test filtering entities by entity type."""
    # Create entities of different types
    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "Company Entity",
            "city": "TypeCity",
            "country": "Type Country",
            "type": "Company",
            "description": "Company type entity",
        },
    )

    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "Lab Entity",
            "city": "TypeCity",
            "country": "Type Country",
            "type": "Research Lab",
            "description": "Lab type entity",
        },
    )

    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "NGO Entity",
            "city": "TypeCity",
            "country": "Type Country",
            "type": "NGO",
            "description": "NGO type entity",
        },
    )

    # Filter by single type
    response = client.get("/api/entities/?type=Company")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 1
    assert entities[0]["name"] == "Company Entity"

    # Filter by multiple types (should use OR logic)
    response = client.get("/api/entities/?type=Company&type=Research%20Lab")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 2  # Should return both Company and Research Lab entities
    entity_names = [e["name"] for e in entities]
    assert "Company Entity" in entity_names
    assert "Lab Entity" in entity_names


def test_filter_entities_by_location(client):
    """Test filtering entities by city and country."""
    # Create entities in different locations
    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "SF Entity",
            "city": "San Francisco",
            "country": "USA",
            "type": "Company",
            "description": "San Francisco entity",
        },
    )

    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "NY Entity",
            "city": "New York",
            "country": "USA",
            "type": "Company",
            "description": "New York entity",
        },
    )

    # Filter by city
    response = client.get("/api/entities/?city=San Francisco")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 1
    assert entities[0]["name"] == "SF Entity"

    # Filter by country
    response = client.get("/api/entities/?country=USA")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 2


def test_export_entities_json(client):
    """Test exporting entities in JSON format."""
    # Create an entity
    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "ExportCo",
            "city": "Exportville",
            "country": "Export Country",
            "type": "Company",
            "description": "Test entity for export",
        },
    )

    # Test JSON export
    response = client.get("/api/export/?format=json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "ExportCo" in str(data)


def test_export_entities_csv(client):
    """Test exporting entities in CSV format."""
    # Create an entity
    client.post(
        "/api/entities/autocomplete",
        json={
            "name": "CSVCo",
            "city": "CSVville",
            "country": "CSV Country",
            "type": "Company",
            "description": "Test entity for CSV export",
        },
    )

    # Test CSV export
    response = client.get("/api/export/?format=csv")
    assert response.status_code == 200
    csv_content = response.text
    assert "CSVCo" in csv_content
    assert "name,city,country" in csv_content  # Check headers are present
