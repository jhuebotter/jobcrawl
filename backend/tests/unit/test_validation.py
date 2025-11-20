import pytest
from pydantic import ValidationError
from backend.src.models.validation import TagCreate, EntityCreate


def test_tag_create_success():
    tag_data = {"name": "AI", "description": "Artificial Intelligence"}
    tag = TagCreate(**tag_data)
    assert tag.name == "AI"
    assert tag.description == "Artificial Intelligence"


def test_tag_create_missing_name():
    with pytest.raises(ValidationError):
        TagCreate(description="A tag without a name")


def test_entity_create_success():
    entity_data = {
        "name": "Test Research Lab",
        "website": "http://example.com",
        "city": "Testville",
        "country": "Testland",
        "type": "Research Lab",
    }
    entity = EntityCreate(**entity_data)
    assert entity.name == "Test Research Lab"
    assert str(entity.website) == "http://example.com/"
    assert entity.city == "Testville"
    assert entity.country == "Testland"
    assert entity.type.value == "Research Lab"


def test_entity_create_invalid_url():
    with pytest.raises(ValidationError):
        EntityCreate(
            name="Invalid URL Lab",
            website="not-a-url",
            city="Testville",
            country="Testland",
            type="Research Lab",
        )


def test_entity_create_missing_name():
    with pytest.raises(ValidationError):
        EntityCreate(city="Testville", country="Testland", type="Research Lab")
