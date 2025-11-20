import uuid
import secrets
import string


def generate_uuid() -> str:
    """Generate a UUID4 string for unique identifiers (external services)"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8, prefix: str = "") -> str:
    """Generate a short random alphanumeric ID for human-readable identifiers

    Args:
        length: Length of the random part (default 8)
        prefix: Optional prefix to prepend (e.g., "run_", "entity_")

    Returns:
        String ID with optional prefix
    """
    alphabet = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}{random_part}" if prefix else random_part
