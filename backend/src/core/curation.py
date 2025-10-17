from backend.src.core.agent import Agent
from backend.src.models.validation import EntityCreate
from backend.src.core.logging import get_logger

logger = get_logger(__name__)

class CurationAgent(Agent):
    def enrich_entity(self, entity_data: dict) -> EntityCreate | None:
        """
        Takes minimal entity data (e.g., from manual user input) and enriches it.
        """
        logger.info(f"Enriching entity: {entity_data.get('name')}")

        # For now, we'll just normalize and validate.
        # In a real implementation, this would involve more complex logic.
        validated_entity = self._normalize_and_validate(entity_data)
        if not validated_entity:
            return None

        # In a real implementation, we would use the LLM to fill in missing fields.
        logger.info(f"Enriched and validated: {validated_entity.name}")
        return validated_entity

curation_agent = CurationAgent()
