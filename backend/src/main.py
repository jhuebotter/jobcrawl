from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.models.validation import entity_types, entity_descriptions
from backend.src.core.db import create_tables
from backend.src.api.entities import router as entities_router
from backend.src.api.tags import router as tags_router
from backend.src.api.entity_tags import router as entity_tags_router
from backend.src.api.export import router as export_router
from backend.src.api.runs import router as runs_router
from backend.src.api.entity_hierarchies import router as entity_hierarchies_router
from backend.src.api.entity_aliases import router as entity_aliases_router
from typing import List, Tuple


def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create database tables on startup
    create_tables()

    # Include API routers
    app.include_router(entities_router, prefix="/api")
    app.include_router(tags_router, prefix="/api")
    app.include_router(entity_tags_router, prefix="/api")
    app.include_router(export_router, prefix="/api")
    app.include_router(runs_router, prefix="/api")
    app.include_router(entity_hierarchies_router, prefix="/api")
    app.include_router(entity_aliases_router, prefix="/api")

    @app.get("/")
    def read_root():
        return {"message": "Welcome to JobCrawl"}

    @app.get("/entity-types")
    def get_entity_types():
        return {"types": entity_types, "descriptions": entity_descriptions}

    @app.post("/export-list")
    def export_list(locations: List[Tuple[str, str]]):
        with open("exported_locations.txt", "w") as f:
            for loc in locations:
                f.write(f"{tuple(loc)}\n")
        return {"message": "List exported to exported_locations.txt"}

    return app


app = create_app()
