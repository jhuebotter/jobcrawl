import pytest


def test_read_entities_skeleton(client):
    response = client.get("/api/entities/")
    assert response.status_code == 200


def test_update_entity_skeleton(client):
    # This will fail because the entity doesn't exist
    response = client.put("/api/entities/1", json={"name": "Test"})
    assert response.status_code == 404


def test_autocomplete_entity_skeleton(client):
    response = client.post("/api/entities/autocomplete", json={"name": "Test"})
    assert response.status_code == 422


def test_read_runs_skeleton(client):
    response = client.get("/api/runs/")
    assert response.status_code == 200


def test_undo_last_run_skeleton(client):
    response = client.post("/api/runs/undo_last")
    assert response.status_code == 200


def test_read_review_queue_skeleton(client):
    response = client.get("/api/review_queue/")
    assert response.status_code == 404


def test_approve_merge_skeleton(client):
    response = client.post("/api/review_queue/1/approve")
    assert response.status_code == 404


def test_reject_merge_skeleton(client):
    response = client.post("/api/review_queue/1/reject")
    assert response.status_code == 404


def test_export_skeleton(client):
    response = client.get("/api/export/?format=json")
    assert response.status_code == 200
