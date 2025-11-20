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
def export_entities(format: str = "json", db: Session = Depends(get_db)):
    entities = db.query(EntityModel).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header - only include basic entity info
        writer.writerow(["name", "city", "country"])

        # Write rows
        for entity in entities:
            writer.writerow([entity.name, entity.city, entity.country])

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv")

    # Default to JSON
    # A bit of a hack to make it JSON serializable
    return json.loads(json.dumps([dict(e.__dict__) for e in entities], default=str))
