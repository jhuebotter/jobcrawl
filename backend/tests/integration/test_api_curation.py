import pytest

def test_autocomplete_entity(client):
    entity_data = {"name": "Test Autocomplete", "website": "http://autocomplete.com"}
    response = client.post("/api/entities/autocomplete", json=entity_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Autocomplete"

def test_autocomplete_duplicate(client):
    entity_data = {"name": "Test Duplicate", "website": "http://duplicate.com"}
    client.post("/api/entities/autocomplete", json=entity_data)
    response = client.post("/api/entities/autocomplete", json=entity_data)
    assert response.status_code == 409

def test_review_queue_empty(client):
    response = client.get("/api/review_queue/")
    assert response.status_code == 200
    assert response.json() == []
