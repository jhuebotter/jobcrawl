from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import (
    Entity as EntityModel,
    Tag as TagModel,
    Starred,
    EntityTag as EntityTagModel,
)
from backend.src.models.validation import (
    Entity,
    EntityCreate,
    EntityUpdate,
    EntityResponse,
)
from backend.src.core.curation import CurationManager
from backend.src.core.agent import Agent
from typing import List, Optional
from datetime import datetime, timezone

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
    if "website" in entity_dict and entity_dict["website"] is not None:
        entity_dict["website"] = str(entity_dict["website"])

    # Convert type to string
    if "type" in entity_dict and hasattr(entity_dict["type"], "value"):
        entity_dict["type"] = entity_dict["type"].value

    # Handle tags separately - create Tag objects from tag names
    tag_names = entity_dict.pop("tags", []) or []
    tag_objects = []
    for tag_name in tag_names:
        # Find or create tag
        tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
        if not tag:
            tag = TagModel(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_objects.append(tag)

    # Create entity without tags first
    db_entity = EntityModel(**entity_dict)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)

    # Associate tags
    for tag in tag_objects:
        db_entity.tags.append(tag)

    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.get("/entities/", response_model=List[Entity])
def read_entities(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[List[str]] = Query(None),
    type: Optional[List[str]] = Query(None),
    city: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    starred: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(EntityModel)

    # Handle multiple tags with OR logic using EXISTS subquery
    if tag:
        from backend.src.models.schema import EntityTag as EntityTagModel

        tag_subquery = (
            db.query(EntityTagModel)
            .join(TagModel)
            .filter(
                EntityTagModel.entity_id == EntityModel.id,
                or_(*[TagModel.name.ilike(f"%{t}%") for t in tag]),
            )
            .exists()
        )
        query = query.filter(tag_subquery)

    # Handle multiple types with OR logic
    if type:
        type_conditions = []
        for t in type:
            type_conditions.append(EntityModel.type.ilike(f"%{t}%"))
        if type_conditions:
            query = query.filter(or_(*type_conditions))

    if city:
        city_conditions = []
        for c in city:
            city_conditions.append(EntityModel.city.ilike(f"%{c}%"))
        if city_conditions:
            query = query.filter(or_(*city_conditions))

    if country:
        country_conditions = []
        for c in country:
            country_conditions.append(EntityModel.country.ilike(f"%{c}%"))
        if country_conditions:
            query = query.filter(or_(*country_conditions))
    if starred is not None:
        if starred:
            query = query.join(EntityModel.starred_entry)
        else:
            query = query.outerjoin(EntityModel.starred_entry).filter(
                Starred.entity_id == None
            )

    entities = query.offset(skip).limit(limit).all()

    # Add is_starred field to each entity
    for entity in entities:
        entity.is_starred = entity.starred_entry is not None

    return entities


@router.get("/entities/{entity_id}", response_model=Entity)
def read_entity(entity_id: str, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity


@router.put("/entities/{entity_id}", response_model=Entity)
def update_entity(entity_id: str, entity: EntityUpdate, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    update_data = entity.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entity, key, value)

    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.delete("/entities/{entity_id}", status_code=204)
def delete_entity(entity_id: str, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    db.delete(db_entity)
    db.commit()

    return Response(status_code=204)


@router.post("/entities/{entity_id}/star", status_code=204)
def star_entity(entity_id: str, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    starred_entry = db.query(Starred).filter(Starred.entity_id == entity_id).first()
    if not starred_entry:
        db.add(Starred(entity_id=entity_id))
        db.commit()

    return Response(status_code=204)


@router.delete("/entities/{entity_id}/star", status_code=204)
def unstar_entity(entity_id: str, db: Session = Depends(get_db)):
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    starred_entry = db.query(Starred).filter(Starred.entity_id == entity_id).first()
    if starred_entry:
        db.delete(starred_entry)
        db.commit()

    return Response(status_code=204)


@router.post("/entities/{entity_id}/tags/{tag_name}", status_code=204)
def add_tag_to_entity(entity_id: str, tag_name: str, db: Session = Depends(get_db)):
    # Check if entity exists
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Find or create tag
    db_tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
    if db_tag is None:
        db_tag = TagModel(name=tag_name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)

    # Check if association already exists
    existing = (
        db.query(EntityTagModel)
        .filter(
            EntityTagModel.entity_id == entity_id, EntityTagModel.tag_id == db_tag.id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="Tag already associated with entity"
        )

    # Create association
    entity_tag = EntityTagModel(entity_id=entity_id, tag_id=db_tag.id)
    db.add(entity_tag)
    db.commit()

    return Response(status_code=204)


@router.delete("/entities/{entity_id}/tags/{tag_name}", status_code=204)
def remove_tag_from_entity(
    entity_id: str, tag_name: str, db: Session = Depends(get_db)
):
    # Check if entity exists
    db_entity = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Find tag
    db_tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Find and delete association
    entity_tag = (
        db.query(EntityTagModel)
        .filter(
            EntityTagModel.entity_id == entity_id, EntityTagModel.tag_id == db_tag.id
        )
        .first()
    )
    if not entity_tag:
        raise HTTPException(status_code=404, detail="Tag not associated with entity")

    db.delete(entity_tag)
    db.commit()

    return Response(status_code=204)


@router.get("/entity-types")
def get_entity_types():
    """Get all valid entity types"""
    from backend.src.models.validation import entity_types

    return {"types": entity_types}


@router.get("/filters")
def get_filter_options(db: Session = Depends(get_db)):
    """Get all unique values for filter dropdowns"""
    # Get unique entity types
    entity_types_db = (
        db.query(EntityModel.type).distinct().filter(EntityModel.type.isnot(None)).all()
    )
    types = [t[0] for t in entity_types_db if t[0]]

    # Get unique tag names
    tags = db.query(TagModel.name).distinct().filter(TagModel.name.isnot(None)).all()
    tag_names = [t[0] for t in tags if t[0]]

    # Get unique cities and countries
    cities = (
        db.query(EntityModel.city).distinct().filter(EntityModel.city.isnot(None)).all()
    )
    city_names = [c[0] for c in cities if c[0]]

    countries = (
        db.query(EntityModel.country)
        .distinct()
        .filter(EntityModel.country.isnot(None))
        .all()
    )
    country_names = [c[0] for c in countries if c[0]]

    return {
        "types": sorted(types),
        "tags": sorted(tag_names),
        "cities": sorted(city_names),
        "countries": sorted(country_names),
    }
