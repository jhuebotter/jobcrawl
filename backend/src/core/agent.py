import datetime
import json
from backend.src.core.logging import get_logger
from backend.src.core.db import SessionLocal
from backend.src.models.schema import Run, Entity, Tag, EntityTag, Source, Person
from backend.src.models.validation import EntityCreate
from backend.src.core.provider import llm_provider
from backend.src.core.scraping import scraper
from pydantic import ValidationError

logger = get_logger(__name__)

class Agent:
    def __init__(self):
        self.db_session = SessionLocal()

    def start_run(self, tags: list[str], cities: list[str], institution_types: list[str]):
        run = Run(
            started_at=datetime.datetime.utcnow().isoformat(),
            parameters=f"tags: {tags}, cities: {cities}, types: {institution_types}",
            status="in_progress"
        )
        self.db_session.add(run)
        self.db_session.commit()
        logger.info(f"Starting run {run.id} with parameters: {run.parameters}")

        for city in cities:
            for tag_name in tags:
                logger.info(f"Processing city: {city}, tag: {tag_name}")
                self._process_pair(city, tag_name, institution_types, run.id)

        run.finished_at = datetime.datetime.utcnow().isoformat()
        run.status = "completed"
        self.db_session.commit()
        logger.info(f"Run {run.id} completed.")

    def _generate_search_query(self, city: str, tag_name: str, institution_types: list[str]) -> str:
        prompt = f"""
        Generate a single, concise search engine query to find {', '.join(institution_types)}
        related to '{tag_name}' in {city}. The query should be suitable for a Google search.
        Return only the query string itself.
        """
        query = llm_provider.generate(prompt).strip()
        logger.info(f"  - Generated search query: {query}")
        return query

    def _extract_data(self, content: str, url: str) -> dict:
        prompt = f"""
        Given the following text from {url}, extract a single professional entity (like a company, research lab, or university department).
        Return a JSON object with the following fields: name, kind, summary, website, city, country.

        Text:
        ---
        {content}
        ---
        """
        response_text = llm_provider.generate(prompt)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from LLM response for {url}")
            return {}

    def _normalize_and_validate(self, data: dict) -> EntityCreate | None:
        try:
            data['name'] = data.get('name', '').strip()
            validated_data = EntityCreate(**data)
            return validated_data
        except ValidationError as e:
            logger.error(f"Validation failed for entity '{data.get('name')}': {e}")
            return None

    def _find_duplicate(self, entity_data: EntityCreate) -> Entity | None:
        existing_entity = self.db_session.query(Entity).filter(
            (Entity.name == entity_data.name) | (Entity.website == str(entity_data.website))
        ).first()
        return existing_entity

    def _persist_entity(self, entity_data: EntityCreate, url: str, run_id: int):
        now = datetime.datetime.utcnow().isoformat()
        new_entity = Entity(
            **entity_data.model_dump(),
            created_at=now,
            updated_at=now
        )
        self.db_session.add(new_entity)
        self.db_session.commit()

        new_source = Source(
            entity_id=new_entity.id,
            url=url,
            retrieved_at=now
        )
        self.db_session.add(new_source)
        self.db_session.commit()
        logger.info(f"  - Persisted new entity '{new_entity.name}' with id {new_entity.id}")

    def _process_pair(self, city: str, tag_name: str, institution_types: list[str], run_id: int):
        search_query = self._generate_search_query(city, tag_name, institution_types)
        
        urls = scraper.retrieve_content(search_query)
        for url in urls:
            content = scraper.get_page_content(url)
            if content:
                extracted_data = self._extract_data(content, url)
                if extracted_data:
                    logger.info(f"  - Extracted: {extracted_data.get('name')}")
                    validated_entity = self._normalize_and_validate(extracted_data)
                    if validated_entity:
                        logger.info(f"  - Validated: {validated_entity.name}")
                        duplicate = self._find_duplicate(validated_entity)
                        if duplicate:
                            logger.info(f"  - Found duplicate for '{validated_entity.name}'. Merging/flagging for review.")
                            # Merge logic will be implemented in a later task
                        else:
                            self._persist_entity(validated_entity, url, run_id)
        pass

agent = Agent()
