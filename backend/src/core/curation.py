# Placeholder for CurationManager
# TODO: Implement full curation logic


class CurationManager:
    def __init__(self, agent):
        self.agent = agent

    async def enrich_and_save_entity(self, entity_data):
        # Placeholder: just return the data as-is
        # In the future, this would enrich with additional info and save to DB
        from backend.src.models.validation import EntityCreate

        return EntityCreate(**entity_data)
