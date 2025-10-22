import pytest
from backend.src.core.prompts import load_prompt

def test_load_prompt_success():
    prompt = load_prompt("test_prompt")
    assert prompt == "This is a test prompt.\n"

def test_load_prompt_not_found():
    with pytest.raises(ValueError):
        load_prompt("non_existent_prompt")
