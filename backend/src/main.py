from fastapi import FastAPI
from backend.src.api import tags, runs
from backend.src.core.db import create_db_and_tables

def create_app():
    app = FastAPI()

    app.include_router(tags.router, prefix="/api")
    app.include_router(runs.router, prefix="/api")

    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    @app.get("/")
    def read_root():
        return {"message": "Welcome to JobCrawl"}
    
    return app

app = create_app()
