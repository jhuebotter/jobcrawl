from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Entity as EntityModel, Tag as TagModel
from backend.src.models.validation import Entity
from typing import List

router = APIRouter()

@router.post("/entities/{entity_id}/tags/{tag_id}", response_model=Entity)
def add_tag_to_entity(entity_id: int, tag_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Idempotent: if already linked, do nothing
    if any(tag.id == tag_id for tag in db_entity.tags):
        return db_entity

    db_entity.tags.append(db_tag)
    db.commit()
    db.refresh(db_entity)
    return db_entity
