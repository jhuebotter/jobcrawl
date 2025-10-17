from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Run as RunModel
from backend.src.models.validation import Run, RunCreate
from backend.src.core.agent import agent
from typing import List

router = APIRouter()

@router.post("/runs/", response_model=Run)
def create_run(run: RunCreate, db: Session = Depends(get_db)):
    # A bit of a hack for now to parse the parameters
    params = run.parameters.split(',')
    tags = [p.split(':')[1] for p in params if 'tags' in p]
    cities = [p.split(':')[1] for p in params if 'cities' in p]
    types = [p.split(':')[1] for p in params if 'types' in p]
    
    # In a real app, this would be a background task
    agent.start_run(db=db, tags=tags, cities=cities, institution_types=types)
    
    # For now, just return the latest run
    db_run = db.query(RunModel).order_by(RunModel.id.desc()).first()
    if db_run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return db_run

@router.get("/runs/", response_model=List[Run])
def read_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(RunModel).offset(skip).limit(limit).all()
    return runs
