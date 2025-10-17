from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

class EntityBase(BaseModel):
    name: str
    kind: Optional[str] = None
    summary: Optional[str] = None
    website: Optional[HttpUrl] = None
    city: Optional[str] = None
    country: Optional[str] = None
    confidence: Optional[float] = None

class EntityCreate(EntityBase):
    pass

class Entity(EntityBase):
    id: int
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class RunBase(BaseModel):
    parameters: str

class RunCreate(RunBase):
    pass

class Run(RunBase):
    id: int
    started_at: str
    finished_at: Optional[str] = None
    status: str

    class Config:
        orm_mode = True
