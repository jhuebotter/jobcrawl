import pytest

def test_read_entities_empty(client):
    response = client.get("/api/entities/")
    assert response.status_code == 200
    assert response.json() == []

def test_filter_entities_by_tag(client):
    # Create a tag
    tag_response = client.post("/api/tags/", json={"name": "tech"})
    tag_id = tag_response.json()["id"]

    # Create an entity
    entity_response = client.post("/api/entities/autocomplete", json={"name": "TestCo", "city": "Testville", "kind": "Industry"})
    entity_id = entity_response.json()["id"]

    # Link them
    client.post(f"/api/entities/{entity_id}/tags/{tag_id}")

    # Test filtering
    response = client.get("/api/entities/?tag=tech")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "TestCo"

    response = client.get("/api/entities/?tag=finance")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_export(client):

    # Create an entity

    client.post("/api/entities/autocomplete", json={"name": "ExportCo", "city": "Exportville"})



    # Test JSON export

    response = client.get("/api/export/?format=json")

    assert response.status_code == 200

    assert "ExportCo" in response.text



    # Test CSV export

    response = client.get("/api/export/?format=csv")

    assert response.status_code == 200

    assert "ExportCo" in response.text
