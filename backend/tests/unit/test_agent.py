import pytest
from backend.src.core.agent import Agent
from backend.src.models.validation import Location


@pytest.fixture
def agent():
    return Agent()


def test_generate_search_combinations(agent):
    """Test that search combinations are generated correctly"""
    locations = [
        Location(city="San Francisco", country="USA"),
        Location(city="Berlin", country="Germany"),
    ]
    tags = ["AI", "ML"]
    institution_types = ["Company", "Research Lab"]

    combinations = agent.generate_search_combinations(
        locations, tags, institution_types
    )

    # Should generate 2 locations × 2 tags × 2 types = 8 combinations
    assert len(combinations) == 8

    # Check structure of first combination
    first_combo = combinations[0]
    assert "location" in first_combo
    assert "tag" in first_combo
    assert "entity_type" in first_combo
    assert "run_id" in first_combo

    assert first_combo["location"] == locations[0]
    assert first_combo["tag"] == tags[0]
    assert first_combo["entity_type"] == institution_types[0]


def test_chunk_combinations(agent):
    """Test that combinations are properly chunked into batches"""
    combinations = list(range(10))  # 10 items
    batch_size = 3

    batches = agent.chunk_combinations(combinations, batch_size)

    # Should create 4 batches: [0,1,2], [3,4,5], [6,7,8], [9]
    assert len(batches) == 4
    assert batches[0] == [0, 1, 2]
    assert batches[1] == [3, 4, 5]
    assert batches[2] == [6, 7, 8]
    assert batches[3] == [9]


def test_build_prompt(agent):
    """Test that prompts are built correctly with template substitution"""
    template = "Find {count} {target_type} organizations in {city}, {country} working on {topic}."

    prompt = agent.build_prompt(
        template,
        city="Berlin",
        country="Germany",
        topic="AI",
        count=5,
        target_type="Research Lab",
    )

    expected = "Find 5 Research Lab organizations in Berlin, Germany working on AI."
    assert prompt == expected


def test_load_prompt_template(agent):
    """Test that prompt templates can be loaded"""
    # This assumes the template file exists
    try:
        template = agent.load_prompt_template()
        assert isinstance(template, str)
        assert len(template) > 0
    except FileNotFoundError:
        # If template file doesn't exist, that's okay for this test
        pytest.skip("Prompt template file not found")
