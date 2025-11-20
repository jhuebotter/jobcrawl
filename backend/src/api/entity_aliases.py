from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import EntityAlias as EntityAliasModel
from backend.src.models.validation import (
    EntityAlias,
    EntityAliasCreate,
    EntityAliasResponse,
)
from typing import List

router = APIRouter()


@router.post("/entity-aliases/", response_model=EntityAliasResponse)
def create_entity_alias(alias: EntityAliasCreate, db: Session = Depends(get_db)):
    from backend.src.models.schema import Entity as EntityModel

    # Check if entity exists
    entity = db.query(EntityModel).filter(EntityModel.id == alias.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Check for existing alias
    existing = (
        db.query(EntityAliasModel).filter(EntityAliasModel.alias == alias.alias).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Alias already exists")

    db_alias = EntityAliasModel(**alias.model_dump())
    db.add(db_alias)
    db.commit()
    db.refresh(db_alias)
    return db_alias


@router.get("/entity-aliases/", response_model=List[EntityAliasResponse])
def read_entity_aliases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    aliases = db.query(EntityAliasModel).offset(skip).limit(limit).all()
    return aliases


@router.get("/entity-aliases/{alias_id}", response_model=EntityAliasResponse)
def read_entity_alias(alias_id: str, db: Session = Depends(get_db)):
    db_alias = (
        db.query(EntityAliasModel).filter(EntityAliasModel.id == alias_id).first()
    )
    if db_alias is None:
        raise HTTPException(status_code=404, detail="Entity alias not found")
    return db_alias


@router.delete("/entity-aliases/{alias_id}")
def delete_entity_alias(alias_id: str, db: Session = Depends(get_db)):
    db_alias = (
        db.query(EntityAliasModel).filter(EntityAliasModel.id == alias_id).first()
    )
    if db_alias is None:
        raise HTTPException(status_code=404, detail="Entity alias not found")

    db.delete(db_alias)
    db.commit()
    return {"message": "Alias deleted"}
