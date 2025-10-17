from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.src.core.db import get_db
from backend.src.models.schema import Entity as EntityModel
from fastapi.responses import StreamingResponse
import io
import csv
import json

router = APIRouter()

@router.get("/export/")
def export_entities(
    format: str = "json",
    db: Session = Depends(get_db)
):
    entities = db.query(EntityModel).all()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([c.name for c in EntityModel.__table__.columns])
        for entity in entities:
            writer.writerow([getattr(entity, c.name) for c in EntityModel.__table__.columns])
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv")

    # Default to JSON
    return [entity.__dict__ for entity in entities]
