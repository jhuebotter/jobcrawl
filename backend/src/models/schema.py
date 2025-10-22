from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

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
    tags = relationship("EntityTag", back_populates="entity")
    people = relationship("Person", back_populates="entity")
    sources = relationship("Source", back_populates="entity")
    edit_logs = relationship("EditLog", back_populates="entity")
    starred_entry = relationship("Starred", back_populates="entity", uselist=False)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    entities = relationship("EntityTag", back_populates="tag")

class EntityTag(Base):
    __tablename__ = 'entity_tags'
    entity_id = Column(Integer, ForeignKey('entities.id', ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    entity = relationship("Entity", back_populates="tags")
    tag = relationship("Tag", back_populates="entities")

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
