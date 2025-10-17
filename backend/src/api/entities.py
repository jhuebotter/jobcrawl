from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Entity as EntityModel
from backend.src.models.validation import Entity
from typing import List

router = APIRouter()

@router.get("/entities/", response_model=List[Entity])
def read_entities(
    skip: int = 0,
    limit: int = 100,
    tag: str = None,
    city: str = None,
    type: str = None,
    starred: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(EntityModel)
    if tag:
        query = query.filter(EntityModel.tags.any(name=tag))
    if city:
        query = query.filter(EntityModel.city == city)
    if type:
        query = query.filter(EntityModel.kind == type)
    if starred is not None:
        query = query.filter(EntityModel.starred_entry != None if starred else EntityModel.starred_entry == None)
    
    entities = query.offset(skip).limit(limit).all()
    return entities
