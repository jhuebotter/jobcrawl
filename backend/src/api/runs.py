from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Run as RunModel, Entity as EntityModel
from backend.src.models.validation import Run, RunCreate, Entity
import os

if "PYTEST_CURRENT_TEST" in os.environ:
    from backend.src.core.agent import agent_mock as agent
else:
    from backend.src.core.agent import agent
from typing import List
import datetime
from datetime import timezone

router = APIRouter()


@router.post("/runs/", status_code=202, response_model=Run)
def create_run(
    run: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Starts a new agent run in the background.
    """
    db_run = RunModel(
        started_at=datetime.datetime.now(timezone.utc),
        parameters=f"tags: {run.tags}, locations: {run.locations}, types: {run.institution_types}",
        status="in_progress",
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    background_tasks.add_task(
        agent.start_run,
        db=db,
        run_id=str(db_run.id),
        tags=run.tags,
        locations=run.locations,
        institution_types=run.institution_types,
    )

    return db_run


@router.get("/runs/", response_model=List[Run])
def read_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = (
        db.query(RunModel).order_by(RunModel.id.desc()).offset(skip).limit(limit).all()
    )
    return runs


@router.get("/runs/{run_id}", response_model=Run)
def read_run(run_id: str, db: Session = Depends(get_db)):
    db_run = db.query(RunModel).filter(RunModel.id == run_id).first()
    if db_run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return db_run


@router.get("/runs/{run_id}/entities", response_model=List[Entity])
def read_run_entities(run_id: str, db: Session = Depends(get_db)):
    entities = db.query(EntityModel).filter(EntityModel.run_id == run_id).all()
    if not entities:
        # This is not an error, it just means no entities were found for this run yet.
        # An empty list is a valid response.
        pass
    db_run = db.query(RunModel).filter(RunModel.id == run_id).first()
    if db_run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return entities


@router.post("/runs/undo_last", response_model=dict)
def undo_last_run(db: Session = Depends(get_db)):
    # Full undo logic will be implemented in a later phase.
    return {"message": "Undo last run endpoint skeleton."}
