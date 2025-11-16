
import os
from fastapi import FastAPI
from backend.src.api import tags, runs, entities, export, review, entity_tags
from backend.src.core.db import create_db_and_tables
from backend.src.core.logging import setup_logging

print("All modules imported successfully")
