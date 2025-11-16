from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Run as RunModel
from backend.src.models.validation import Run, RunCreate
from backend.src.core.agent import agent
from typing import List

router = APIRouter()

@router.post("/runs/", status_code=202, response_model=Run)
def create_run(run: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # A bit of a hack for now to parse the parameters
    params = run.parameters.split(',')
    tags = [p.split(':')[1] for p in params if 'tags' in p]
    cities = [p.split(':')[1] for p in params if 'cities' in p]
    types = [p.split(':')[1] for p in params if 'types' in p]
    
    # Add the agent run to the background
    background_tasks.add_task(agent.start_run, db=db, tags=tags, cities=cities, institution_types=types)
    
    # For now, just return a representation of the run being started
    # A more robust implementation would create the Run record here and pass its ID to the agent
    return {"parameters": run.parameters, "status": "in_progress", "id": 0, "started_at": ""}

@router.get("/runs/", response_model=List[Run])
def read_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(RunModel).order_by(RunModel.id.desc()).offset(skip).limit(limit).all()
    return runs

@router.post("/runs/undo_last", response_model=dict)
def undo_last_run(db: Session = Depends(get_db)):
    # Full undo logic will be implemented in a later phase.
    return {"message": "Undo last run endpoint skeleton."}
