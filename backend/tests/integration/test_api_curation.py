import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.src.main import app
from backend.src.models.schema import Entity, Person

client = TestClient(app)

def test_autocomplete_entity(db: Session):
    response = client.post(
        "/api/entities/autocomplete",
        json={"name": "Test Corp", "website": "http://testcorp.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Corp"
    assert data["summary"] is not None

def test_get_review_queue(db: Session):
    # Create an entity and a person that needs review
    entity = Entity(name="Review Corp", city="Review City", country="RC", kind="Tech", confidence=0.8, run_id=1)
    db.add(entity)
    db.commit()
    db.refresh(entity)

    person = Person(entity_id=entity.id, name="John Doe", role="Tester", review_status="needs_review", run_id=1)
    db.add(person)
    db.commit()

    response = client.get("/api/review_queue/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Review Corp"