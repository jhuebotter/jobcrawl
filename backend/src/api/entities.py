from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Entity as EntityModel, Tag as TagModel, Starred
from backend.src.models.validation import Entity, EntityCreate
from backend.src.core.curation import CurationManager
from backend.src.core.agent import Agent
from typing import List

router = APIRouter()

# This is a placeholder for the actual agent initialization
agent = Agent()
curation_manager = CurationManager(agent)

@router.post("/entities/autocomplete", response_model=Entity)
async def autocomplete_entity(entity_data: EntityCreate, db: Session = Depends(get_db)):
    # The curation manager now handles the enrichment and saving logic.
    # Note: The enrich_and_save_entity is an async function.
    new_entity = await curation_manager.enrich_and_save_entity(entity_data.model_dump())
    
    # For the purpose of this example, we assume the curation manager
    # returns a Pydantic model that needs to be converted to a dictionary
    # before being saved to the database.
    entity_dict = new_entity.model_dump()
    
    # Convert HttpUrl to string if necessary
    if 'website' in entity_dict and entity_dict['website'] is not None:
        entity_dict['website'] = str(entity_dict['website'])

    db_entity = EntityModel(**entity_dict, created_at="now", updated_at="now")
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.get("/entities/", response_model=List[Entity])
def read_entities(
    skip: int = 0,
    limit: int = 100,
    tag: str = None,
    city: str = None,
    kind: str = None,
    starred: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(EntityModel)
    if tag:
        query = query.join(EntityModel.tags).filter(TagModel.name == tag)
    if city:
        query = query.filter(EntityModel.city == city)
    if kind:
        query = query.filter(EntityModel.kind == kind)
    if starred is not None:
        if starred:
            query = query.join(EntityModel.starred_entry)
        else:
            query = query.outerjoin(EntityModel.starred_entry).filter(Starred.entity_id == None)
    
    entities = query.offset(skip).limit(limit).all()
    return entities

@router.put("/entities/{entity_id}", response_model=Entity)
def update_entity(entity_id: int, entity: EntityCreate, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    update_data = entity.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entity, key, value)
    
    db_entity.updated_at = "now"
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.post("/entities/{entity_id}/star", status_code=204)
def star_entity(entity_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    starred_entry = db.query(Starred).filter(Starred.entity_id == entity_id).first()
    if not starred_entry:
        db.add(Starred(entity_id=entity_id))
        db.commit()
    
    return Response(status_code=204)

@router.delete("/entities/{entity_id}/star", status_code=204)
def unstar_entity(entity_id: int, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    starred_entry = db.query(Starred).filter(Starred.entity_id == entity_id).first()
    if starred_entry:
        db.delete(starred_entry)
        db.commit()
    
    return Response(status_code=204)
