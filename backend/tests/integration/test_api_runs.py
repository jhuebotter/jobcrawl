import pytest

def test_create_and_read_tag(client):
    # Create a new tag
    response = client.post("/api/tags/", json={"name": "Integration Test", "description": "A test tag"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Integration Test"
    tag_id = data["id"]

    # Read the tags to see if it's there
    response = client.get("/api/tags/")
    assert response.status_code == 200
    data = response.json()
    assert any(t["id"] == tag_id for t in data)

def test_create_duplicate_tag(client):
    client.post("/api/tags/", json={"name": "Duplicate Test"})
    response = client.post("/api/tags/", json={"name": "Duplicate Test"})
    assert response.status_code == 400

def test_start_run(client):
    response = client.post("/api/runs/", json={"parameters": "tags:test,cities:testville,types:test"})
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "in_progress"
    assert "tags:test" in data["parameters"]

def test_read_runs(client):
    response = client.get("/api/runs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
