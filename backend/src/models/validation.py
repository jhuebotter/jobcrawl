from pydantic import BaseModel, HttpUrl, ConfigDict, field_validator, model_validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum


class Location(BaseModel):
    city: str
    country: str


# Entity types data - single source of truth
entity_type_data = [
    {
        "name": "Company",
        "description": "For-profit businesses or corporations, including startups and large tech companies. Examples: Google, Microsoft.",
    },
    {
        "name": "NGO",
        "description": "Non-profit, non-governmental organizations, foundations, advocacy groups, and charities, typically independent from direct government control. Examples: Amnesty International, Greenpeace.",
    },
    {
        "name": "University",
        "description": "Universities and universities of applied sciences as whole institutions. Examples: TU Berlin, University of Amsterdam.",
    },
    {
        "name": "Research Lab",
        "description": "Research groups, centers, or laboratories that are part of a larger organization (a university, institute, or company). Examples: AI Lab at TU Berlin, The artificial cognitive systems lab, Gatsby Computational Neuroscience Unit.",
    },
    {
        "name": "Institute",
        "description": "Standalone or semi-independent research institutes or centers that usually contain multiple labs or departments. Examples: Fraunhofer institutes, Max Planck institutes, DFKI.",
    },
    {
        "name": "Governmental Organization",
        "description": "Public authorities, ministries, agencies, or intergovernmental bodies with an official government mandate. Examples: European Commission, Federal Ministry of Education and Research (Germany).",
    },
]

# Generate enum from data
EntityType = Enum(
    "EntityType", {item["name"]: item["name"] for item in entity_type_data}
)

# Generate lists/dicts from data
entity_types = [item["name"] for item in entity_type_data]
entity_descriptions = {item["name"]: item["description"] for item in entity_type_data}


class TagBase(BaseModel):
    name: str
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class EntityBase(BaseModel):
    name: str
    city: str
    country: str
    type: EntityType
    description: Optional[str] = None
    website: Optional[HttpUrl] = None

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.type}) - {self.city}, {self.country}\n"
            f"Website: {self.website}\n"
            f"Description: {self.description}\n"
        )


class EntityList(BaseModel):
    results: List[EntityBase]

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self.results)


class EntityCreate(EntityBase):
    tags: Optional[List[str]] = None


class EntityUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None

    @field_validator("name", "city", "country", "type")
    @classmethod
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("This field cannot be empty")
        return v.strip() if v else v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in entity_types:
            raise ValueError(f'Type must be one of: {", ".join(entity_types)}')
        return v


class Entity(EntityBase):
    id: str
    run_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    is_starred: bool = False
    hierarchies_as_child: List["EntityHierarchy"] = []
    hierarchies_as_parent: List["EntityHierarchy"] = []
    aliases: List["EntityAlias"] = []
    model_config = ConfigDict(from_attributes=True)


class EntityAliasBase(BaseModel):
    alias: str


class EntityAliasCreate(EntityAliasBase):
    entity_id: Union[str, int]

    @field_validator("entity_id", mode="before")
    @classmethod
    def convert_entity_id_to_str(cls, v):
        return str(v) if isinstance(v, int) else v


class EntityAlias(EntityAliasBase):
    id: str
    entity_id: str
    entity: Entity
    model_config = ConfigDict(from_attributes=True)


class EntityAliasResponse(EntityAliasBase):
    id: str
    entity_id: str
    # Exclude the entity relationship to avoid circular references
    model_config = ConfigDict(from_attributes=True)


class EntityHierarchyBase(BaseModel):
    parent_id: Union[str, int]
    relationship_type: str = "part_of"

    @field_validator("parent_id", mode="before")
    @classmethod
    def convert_parent_id_to_str(cls, v):
        return str(v) if isinstance(v, int) else v


class EntityHierarchyCreate(EntityHierarchyBase):
    child_id: Union[str, int]

    @field_validator("child_id", mode="before")
    @classmethod
    def convert_child_id_to_str(cls, v):
        return str(v) if isinstance(v, int) else v


class EntityHierarchy(EntityHierarchyBase):
    id: str
    child_id: str
    child: Entity
    parent: Entity
    model_config = ConfigDict(from_attributes=True)


class EntityHierarchyResponse(EntityHierarchyBase):
    id: str
    child_id: str
    parent_id: str
    # Exclude the entity relationships to avoid circular references
    model_config = ConfigDict(from_attributes=True)


class EntityResponse(EntityBase):
    id: str
    run_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    is_starred: bool = False
    # Exclude hierarchies and aliases to avoid circular references
    model_config = ConfigDict(from_attributes=True)


class RunBase(BaseModel):
    pass


class RunCreate(RunBase):
    tags: List[str]
    locations: List[Location]
    institution_types: List[str]


class Run(RunBase):
    id: str
    parameters: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    results_summary: Optional[str] = None
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    tool_tokens: int
