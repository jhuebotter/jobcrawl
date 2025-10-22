import pytest
from backend.src.core.agent import Agent

@pytest.fixture
def agent():
    return Agent()

def test_normalize_and_validate_success(agent):
    data = {"name": "  Test Entity  ", "website": "http://example.com"}
    validated = agent._normalize_and_validate(data)
    assert validated is not None
    assert validated.name == "Test Entity"

def test_normalize_and_validate_failure(agent):
    data = {"website": "not-a-url"}
    validated = agent._normalize_and_validate(data)
    assert validated is None
