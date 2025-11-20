from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime, timezone
from backend.src.core.utils import generate_short_id

Base = declarative_base()


class Entity(Base):
    """Represents a discovered organization or entity with metadata."""

    __tablename__ = "entities"
    id = Column(
        String, primary_key=True, default=lambda: generate_short_id(prefix="entity_")
    )
    name = Column(String, nullable=False)
    type = Column(String)
    description = Column(Text)
    website = Column(String)
    city = Column(String)
    country = Column(String)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    run_id = Column(String, ForeignKey("runs.id"))

    entity_tags = relationship(
        "EntityTag",
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags = association_proxy(
        "entity_tags", "tag", creator=lambda tag: EntityTag(tag=tag)
    )

    starred_entry = relationship(
        "Starred",
        back_populates="entity",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    hierarchies_as_child = relationship(
        "EntityHierarchy",
        foreign_keys="EntityHierarchy.child_id",
        back_populates="child",
        overlaps="parent_relationships",
    )
    hierarchies_as_parent = relationship(
        "EntityHierarchy",
        foreign_keys="EntityHierarchy.parent_id",
        back_populates="parent",
        overlaps="child_relationships",
    )

    parent_relationships = relationship(
        "EntityHierarchy",
        foreign_keys="EntityHierarchy.child_id",
        back_populates="child",
        overlaps="hierarchies_as_child",
    )
    child_relationships = relationship(
        "EntityHierarchy",
        foreign_keys="EntityHierarchy.parent_id",
        back_populates="parent",
        overlaps="hierarchies_as_parent",
    )

    aliases = relationship(
        "EntityAlias",
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Tag(Base):
    """Represents a categorization tag for entities."""

    __tablename__ = "tags"
    id = Column(
        String, primary_key=True, default=lambda: generate_short_id(prefix="tag_")
    )
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    entity_tags = relationship(
        "EntityTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    entities = association_proxy(
        "entity_tags", "entity", creator=lambda entity: EntityTag(entity=entity)
    )


class EntityTag(Base):
    """Junction table for many-to-many relationship between entities and tags."""

    __tablename__ = "entity_tags"
    entity_id = Column(
        String, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    entity = relationship("Entity", back_populates="entity_tags")
    tag = relationship("Tag", back_populates="entity_tags")


class Run(Base):
    """Represents a search operation or run with metadata and token usage."""

    __tablename__ = "runs"
    id = Column(
        String, primary_key=True, default=lambda: generate_short_id(prefix="run_")
    )
    started_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    finished_at = Column(DateTime)
    parameters = Column(Text)
    status = Column(String)
    results_summary = Column(Text)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    thinking_tokens = Column(Integer, nullable=False, default=0)
    tool_tokens = Column(Integer, nullable=False, default=0)


class Starred(Base):
    """Represents favorited/starred entities."""

    __tablename__ = "starred"
    entity_id = Column(
        String, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    entity = relationship("Entity", back_populates="starred_entry")


class EntityHierarchy(Base):
    """Represents hierarchical 'part of' relationships between entities."""

    __tablename__ = "entity_hierarchies"
    id = Column(
        String, primary_key=True, default=lambda: generate_short_id(prefix="hierarchy_")
    )
    child_id = Column(
        String, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    parent_id = Column(
        String, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type = Column(String, nullable=False, default="part_of")

    # Unique constraint to prevent duplicate relationships
    __table_args__ = (
        UniqueConstraint("child_id", "parent_id", name="unique_child_parent"),
    )

    child = relationship(
        "Entity", foreign_keys=[child_id], back_populates="parent_relationships"
    )
    parent = relationship(
        "Entity", foreign_keys=[parent_id], back_populates="child_relationships"
    )


class EntityAlias(Base):
    """Tracks alternative names/aliases for entities."""

    __tablename__ = "entity_aliases"
    id = Column(
        String, primary_key=True, default=lambda: generate_short_id(prefix="alias_")
    )
    entity_id = Column(
        String, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    alias = Column(String, nullable=False, unique=True)  # e.g., "UVA"

    entity = relationship("Entity", back_populates="aliases")
