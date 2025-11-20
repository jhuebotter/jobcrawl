from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from backend.src.models.schema import Base
import sqlite3
from urllib.parse import urlparse
from fuzzywuzzy import fuzz
from typing import List, Optional
from datetime import datetime, timezone

# Database URL - using SQLite for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./jobcrawl.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency to get a database session.
    Use in FastAPI endpoints with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined in the models.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)


def normalize_website(url: str) -> str:
    """
    Normalize website URL for consistent storage and comparison.

    Best practices:
    - Remove protocol (http/https)
    - Remove www. prefix
    - Convert to lowercase
    - Remove trailing slashes
    - Handle empty/None values gracefully

    Args:
        url: The website URL to normalize

    Returns:
        Normalized domain string (e.g., "example.com")
    """
    if not url or not isinstance(url, str):
        return ""

    url = url.strip()
    if not url:
        return ""

    # Add scheme if missing to help urlparse
    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return ""

        # Extract domain and remove www. prefix
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        # Remove trailing slashes
        return domain.rstrip("/")
    except Exception:
        # If parsing fails, return empty string
        return ""


def find_or_create_entity(
    db,
    name: str,
    city: str,
    country: str,
    entity_type: str,
    tags: List[str],
    website: Optional[str] = None,
    description: Optional[str] = None,
):
    """
    Centralized deduplication and upsert logic for entities.

    This function implements a multi-step deduplication process:
    1. Website/domain matching (first pass)
    2. Fuzzy name matching with aliases
    3. Create new entity if no matches found

    Args:
        db: Database session
        name: Entity name
        city: City location
        country: Country location
        entity_type: Type of entity (Company, NGO, etc.)
        tags: List of tag names to associate
        website: Website URL (optional)
        description: Entity description (optional)

    Returns:
        Entity: Either existing entity (with tags added) or new entity
    """
    from backend.src.models.schema import Entity as EntityModel, Tag as TagModel

    # Step 1: Website/domain matching (first pass)
    if website:
        normalized_domain = normalize_website(website)
        if normalized_domain:
            # Find entities with matching normalized domains
            candidates = (
                db.query(EntityModel)
                .filter(
                    EntityModel.city == city,
                    EntityModel.country == country,
                    EntityModel.type == entity_type,
                )
                .all()
            )

            for candidate in candidates:
                candidate_domain = normalize_website(candidate.website or "")
                if candidate_domain == normalized_domain:
                    # Found match by domain - add tags and update description if needed
                    add_tags_to_entity(db, candidate, tags)
                    if description and (
                        candidate.description is None
                        or candidate.description != description
                    ):
                        candidate.description = description
                        candidate.updated_at = datetime.now(timezone.utc)
                        db.commit()
                    return candidate

    # Step 2: Fuzzy name matching with aliases
    candidates = (
        db.query(EntityModel)
        .filter(
            EntityModel.city == city,
            EntityModel.country == country,
            EntityModel.type == entity_type,
        )
        .all()
    )

    for candidate in candidates:
        # Check main name
        similarity = fuzz.ratio(candidate.name.lower(), name.lower())
        if similarity > 80:  # 80% similarity threshold
            add_tags_to_entity(db, candidate, tags)
            if description and (
                candidate.description is None or candidate.description != description
            ):
                candidate.description = description
                candidate.updated_at = datetime.now(timezone.utc)
                db.commit()
            return candidate

        # Check aliases
        for alias in candidate.aliases:
            alias_similarity = fuzz.ratio(alias.alias.lower(), name.lower())
            if alias_similarity > 80:
                add_tags_to_entity(db, candidate, tags)
                if description and (
                    candidate.description is None
                    or candidate.description != description
                ):
                    candidate.description = description
                    candidate.updated_at = datetime.now(timezone.utc)
                    db.commit()
                return candidate

    # Step 3: Create new entity
    new_entity = EntityModel(
        name=name,
        city=city,
        country=country,
        type=entity_type,
        website=website,
        description=description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(new_entity)  # Add to session first
    add_tags_to_entity(db, new_entity, tags)  # Then add tags
    db.commit()
    db.refresh(new_entity)
    return new_entity


def add_tags_to_entity(db, entity, tag_names: List[str]):
    """
    Add tags to an entity, creating tags if they don't exist.

    Args:
        db: Database session
        entity: Entity model instance
        tag_names: List of tag names to add
    """
    from backend.src.models.schema import Tag as TagModel

    for tag_name in tag_names:
        # Find or create tag
        tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
        if not tag:
            tag = TagModel(name=tag_name, description="")
            db.add(tag)
            db.commit()
            db.refresh(tag)

        # Add tag to entity if not already present
        if tag not in entity.tags:
            entity.tags.append(tag)

    entity.updated_at = datetime.now(timezone.utc)
    db.commit()


def display_all_tables(db_path="jobcrawl.db", use_pandas=True):
    """
    Connects to the SQLite database and prints the contents of all tables.

    Args:
        db_path (str): Path to the SQLite database file
        use_pandas (bool): Whether to use pandas for pretty printing (requires pandas)
    """
    try:
        if use_pandas:
            try:
                import pandas as pd

                # Set pandas options to display all data without truncation
                pd.set_option("display.max_rows", None)
                pd.set_option("display.max_columns", None)
                pd.set_option("display.width", 2000)
                pd.set_option("display.max_colwidth", None)
            except ImportError:
                print("Warning: pandas not available, falling back to basic output")
                use_pandas = False

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print(f"No tables found in the database '{db_path}'.")
            return

        print(f"Database: {db_path}\n")

        # Iterate through the list of tables
        for table_name in tables:
            table_name = table_name[0]
            print("-" * 50)
            print(f"Table: {table_name}")
            print("-" * 50)

            try:
                if use_pandas:
                    # Use pandas to read the table
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    if df.empty:
                        print("Table is empty.")
                    else:
                        # For the 'entities' table, print each record individually for clarity
                        if table_name == "entities":
                            for i, (_, row) in enumerate(df.iterrows()):
                                print(f"--- Record {i+1} ---")
                                for col in df.columns:
                                    print(f"  {col:<15}: {row[col]}")
                                print()
                        else:
                            # For other tables, the default string format is fine
                            print(df.to_string())
                else:
                    # Fallback without pandas
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()

                    if not rows:
                        print("Table is empty.")
                    else:
                        # Get column names
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in cursor.fetchall()]

                        # Print header
                        print(" | ".join(f"{col:<15}" for col in columns))
                        print("-" * (len(columns) * 18))

                        # Print rows
                        for row in rows:
                            print(" | ".join(f"{str(cell):<15}" for cell in row))

                print("\n")
            except Exception as e:
                print(f"Could not read table {table_name}: {e}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()


if __name__ == "__main__":
    # Allow running this module directly for debugging
    display_all_tables()
