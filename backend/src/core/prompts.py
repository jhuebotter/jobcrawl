import os

def load_prompt(name: str) -> str:
    """
    Loads a prompt template from the prompts directory.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{name}.txt")
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Prompt template not found: {name}")
