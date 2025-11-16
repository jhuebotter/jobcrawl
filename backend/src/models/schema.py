from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    kind = Column(String)
    summary = Column(Text)
    website = Column(String)
    city = Column(String)
    country = Column(String)
    confidence = Column(Float)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    run_id = Column(Integer, ForeignKey('runs.id'))

    entity_tags = relationship(
        "EntityTag",
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags = association_proxy(
        "entity_tags",
        "tag",
        creator=lambda tag: EntityTag(tag=tag)
    )

    people = relationship("Person", back_populates="entity", cascade="all, delete-orphan", passive_deletes=True)
    sources = relationship("Source", back_populates="entity", cascade="all, delete-orphan", passive_deletes=True)
    edit_logs = relationship("EditLog", back_populates="entity", cascade="all, delete-orphan", passive_deletes=True)
    starred_entry = relationship("Starred", back_populates="entity", uselist=False, cascade="all, delete-orphan", passive_deletes=True)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    entity_tags = relationship(
        "EntityTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    entities = association_proxy(
        "entity_tags",
        "entity",
        creator=lambda entity: EntityTag(entity=entity)
    )

class EntityTag(Base):
    __tablename__ = 'entity_tags'
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
    entity = relationship("Entity", back_populates="entity_tags")
    tag = relationship("Tag", back_populates="entity_tags")

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    role = Column(String)
    source_url = Column(String)
    review_status = Column(String)
    run_id = Column(Integer, ForeignKey('runs.id'))
    entity = relationship("Entity", back_populates="people")

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"))
    url = Column(String, nullable=False)
    retrieved_at = Column(String, nullable=False)
    run_id = Column(Integer, ForeignKey('runs.id'))
    entity = relationship("Entity", back_populates="sources")

class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    started_at = Column(String, nullable=False)
    finished_at = Column(String)
    parameters = Column(Text)
    status = Column(String)
    results_summary = Column(Text)

class EditLog(Base):
    __tablename__ = 'edit_logs'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"))
    field_name = Column(String, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(String, nullable=False)
    entity = relationship("Entity", back_populates="edit_logs")

class Starred(Base):
    __tablename__ = 'starred'
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"), primary_key=True)
    entity = relationship("Entity", back_populates="starred_entry")
