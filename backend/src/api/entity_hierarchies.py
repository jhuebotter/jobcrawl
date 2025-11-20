from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import EntityHierarchy as EntityHierarchyModel
from backend.src.models.validation import (
    EntityHierarchy,
    EntityHierarchyCreate,
    EntityHierarchyResponse,
)
from typing import List

router = APIRouter()


@router.post("/entity-hierarchies/", response_model=EntityHierarchyResponse)
def create_entity_hierarchy(
    hierarchy: EntityHierarchyCreate, db: Session = Depends(get_db)
):
    from backend.src.models.schema import Entity as EntityModel

    # Check if entities exist
    child_entity = (
        db.query(EntityModel).filter(EntityModel.id == hierarchy.child_id).first()
    )
    if not child_entity:
        raise HTTPException(status_code=404, detail="Child entity not found")

    parent_entity = (
        db.query(EntityModel).filter(EntityModel.id == hierarchy.parent_id).first()
    )
    if not parent_entity:
        raise HTTPException(status_code=404, detail="Parent entity not found")

    # Check for existing relationship
    existing = (
        db.query(EntityHierarchyModel)
        .filter(
            EntityHierarchyModel.child_id == hierarchy.child_id,
            EntityHierarchyModel.parent_id == hierarchy.parent_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Hierarchy relationship already exists"
        )

    db_hierarchy = EntityHierarchyModel(**hierarchy.model_dump())
    db.add(db_hierarchy)
    db.commit()
    db.refresh(db_hierarchy)
    return db_hierarchy


@router.get("/entity-hierarchies/", response_model=List[EntityHierarchyResponse])
def read_entity_hierarchies(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    hierarchies = db.query(EntityHierarchyModel).offset(skip).limit(limit).all()
    return hierarchies


@router.get(
    "/entity-hierarchies/{hierarchy_id}", response_model=EntityHierarchyResponse
)
def read_entity_hierarchy(hierarchy_id: str, db: Session = Depends(get_db)):
    db_hierarchy = (
        db.query(EntityHierarchyModel)
        .filter(EntityHierarchyModel.id == hierarchy_id)
        .first()
    )
    if db_hierarchy is None:
        raise HTTPException(status_code=404, detail="Entity hierarchy not found")
    return db_hierarchy


@router.delete("/entity-hierarchies/{hierarchy_id}")
def delete_entity_hierarchy(hierarchy_id: str, db: Session = Depends(get_db)):
    db_hierarchy = (
        db.query(EntityHierarchyModel)
        .filter(EntityHierarchyModel.id == hierarchy_id)
        .first()
    )
    if db_hierarchy is None:
        raise HTTPException(status_code=404, detail="Entity hierarchy not found")

    db.delete(db_hierarchy)
    db.commit()
    return {"message": "Hierarchy deleted"}
