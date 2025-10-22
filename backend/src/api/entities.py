from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Entity as EntityModel
from backend.src.models.validation import Entity, EntityCreate
from backend.src.core.curation import curation_agent
from typing import List

router = APIRouter()

@router.post("/entities/autocomplete", response_model=Entity)
def autocomplete_entity(entity_data: EntityCreate, db: Session = Depends(get_db)):
    enriched_entity = curation_agent.enrich_entity(entity_data.model_dump())
    if not enriched_entity:
        raise HTTPException(status_code=400, detail="Invalid entity data")

    duplicate = curation_agent._find_duplicate(db, enriched_entity)
    if duplicate:
        raise HTTPException(status_code=409, detail="Duplicate entity found")

    # Convert HttpUrl to string before creating the SQLAlchemy model
    entity_dict = enriched_entity.model_dump()
    if 'website' in entity_dict and entity_dict['website'] is not None:
        entity_dict['website'] = str(entity_dict['website'])

    new_entity = EntityModel(**entity_dict, created_at="now", updated_at="now")
    db.add(new_entity)
    db.commit()
    db.refresh(new_entity)
    return new_entity

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

@router.put("/entities/{entity_id}", response_model=Entity)
def update_entity(entity_id: int, entity: EntityCreate, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # For now, we'll just return the existing entity without updating.
    # The full update logic will be implemented in a later phase.
    return db_entity
