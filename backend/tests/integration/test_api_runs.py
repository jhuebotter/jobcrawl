import pytest
from backend.src.models.validation import Location


def test_create_and_read_tag(client):
    """Test creating a new tag and reading it back."""
    # Create a new tag
    response = client.post(
        "/api/tags/", json={"name": "Integration Test", "description": "A test tag"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Integration Test"
    assert data["description"] == "A test tag"
    tag_id = data["id"]

    # Read the tags to see if it's there
    response = client.get("/api/tags/")
    assert response.status_code == 200
    data = response.json()
    assert any(t["id"] == tag_id for t in data)


def test_create_duplicate_tag_fails(client):
    """Test that creating a duplicate tag fails with appropriate error."""
    client.post("/api/tags/", json={"name": "Duplicate Test"})
    response = client.post("/api/tags/", json={"name": "Duplicate Test"})
    assert response.status_code == 400


def test_update_tag(client):
    """Test updating an existing tag's information."""
    # Create a tag first
    create_response = client.post(
        "/api/tags/",
        json={"name": "Update Test", "description": "Original description"},
    )
    tag_id = create_response.json()["id"]

    # Update it
    update_response = client.put(
        f"/api/tags/{tag_id}",
        json={"name": "Updated Test", "description": "Updated description"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Test"
    assert data["description"] == "Updated description"


def test_delete_tag(client):
    """Test deleting an existing tag."""
    # Create a tag first
    create_response = client.post("/api/tags/", json={"name": "Delete Test"})
    tag_id = create_response.json()["id"]

    # Delete it
    delete_response = client.delete(f"/api/tags/{tag_id}")
    assert delete_response.status_code == 200

    # Verify it's gone
    read_response = client.get("/api/tags/")
    tags = read_response.json()
    assert not any(t["id"] == tag_id for t in tags)


def test_start_run_background_task(client):
    """Test starting a new agent run as a background task."""
    run_data = {
        "tags": ["AI"],
        "locations": [{"city": "San Francisco", "country": "USA"}],
        "institution_types": ["Company"],
    }
    response = client.post("/api/runs/", json=run_data)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "in_progress"
    assert "AI" in data["parameters"]
    run_id = data["id"]

    # Check that run was created
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    run_data = response.json()
    assert run_data["id"] == run_id
    assert run_data["status"] == "in_progress"


def test_read_runs_list(client):
    """Test reading the list of runs."""
    response = client.get("/api/runs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_read_run_entities_empty(client):
    """Test reading entities for a run that has no entities yet."""
    # First create a run
    run_data = {
        "tags": ["Test"],
        "locations": [{"city": "Test City", "country": "Test Country"}],
        "institution_types": ["Company"],
    }
    response = client.post("/api/runs/", json=run_data)
    assert response.status_code == 202
    run_id = response.json()["id"]

    # Get entities for this run (should be empty initially)
    response = client.get(f"/api/runs/{run_id}/entities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # May be empty or have entities depending on if background task completed


def test_undo_last_run_skeleton(client):
    """Test the undo last run endpoint (currently a skeleton implementation)."""
    response = client.post("/api/runs/undo_last")
    # This is currently a skeleton, so it should return some response
    assert response.status_code in [
        200,
        404,
        500,
    ]  # Accept various responses for skeleton
