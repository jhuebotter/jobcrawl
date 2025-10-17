from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Tag as TagModel
from backend.src.models.validation import Tag, TagCreate
from typing import List

router = APIRouter()

@router.post("/tags/", response_model=Tag)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = db.query(TagModel).filter(TagModel.name == tag.name).first()
    if db_tag:
        raise HTTPException(status_code=400, detail="Tag already registered")
    db_tag = TagModel(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags/", response_model=List[Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = db.query(TagModel).offset(skip).limit(limit).all()
    return tags
