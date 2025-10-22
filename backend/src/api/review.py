from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Person as PersonModel, Entity as EntityModel
from backend.src.models.validation import Entity
from typing import List

router = APIRouter()

@router.get("/review_queue/", response_model=List[Entity])
def read_review_queue(db: Session = Depends(get_db)):
    # For now, the review queue is just people with a 'needs_review' status.
    people_to_review = db.query(PersonModel).filter(PersonModel.review_status == "needs_review").all()
    entities = [p.entity for p in people_to_review if p.entity]
    return entities

@router.post("/review_queue/{entity_id}/approve", response_model=dict)
def approve_merge(entity_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    # Full approve logic will be implemented in a later phase.
    return {"message": f"Merge approved for entity {entity_id}"}

@router.post("/review_queue/{entity_id}/reject", response_model=dict)
def reject_merge(entity_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    # Full reject logic will be implemented in a later phase.
    return {"message": f"Merge rejected for entity {entity_id}"}
