import pytest

def test_read_entities_empty(client):
    response = client.get("/api/entities/")
    assert response.status_code == 200
    assert response.json() == []

def test_export_empty(client):
    response = client.get("/api/export/?format=json")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/api/export/?format=csv")
    assert response.status_code == 200
    assert "id,name" in response.text # Check for header
