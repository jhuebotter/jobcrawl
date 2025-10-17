import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.models.schema import Base

DATABASE_URL = "sqlite:///jobcrawl.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    # Check if the database file already exists. If so, do nothing.
    if not os.path.exists(DATABASE_URL.split("///")[1]):
        print("Creating database and tables...")
        Base.metadata.create_all(bind=engine)
        print("Database and tables created.")
    else:
        print("Database already exists.")

if __name__ == "__main__":
    create_db_and_tables()
