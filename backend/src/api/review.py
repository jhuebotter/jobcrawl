from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Person as PersonModel
from backend.src.models.validation import Entity
from typing import List

router = APIRouter()

@router.get("/review_queue/", response_model=List[Entity])
def read_review_queue(db: Session = Depends(get_db)):
    # For now, the review queue is just people with a 'needs_review' status.
    people_to_review = db.query(PersonModel).filter(PersonModel.review_status == "needs_review").all()
    entities = [p.entity for p in people_to_review if p.entity]
    return entities
