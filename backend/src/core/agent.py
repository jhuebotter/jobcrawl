import datetime
import json
from sqlalchemy.orm import Session
from backend.src.core.logging import get_logger
from backend.src.models.schema import Run, Entity, Tag, EntityTag, Source, Person
from backend.src.models.validation import EntityCreate
from backend.src.core.provider import llm_provider
from backend.src.core.scraping import scraper
from backend.src.core.prompts import load_prompt
from pydantic import ValidationError

logger = get_logger(__name__)

class Agent:
    def start_run(self, db: Session, tags: list[str], cities: list[str], institution_types: list[str]):
        run = Run(
            started_at=datetime.datetime.now(datetime.UTC).isoformat(),
            parameters=f"tags: {tags}, cities: {cities}, types: {institution_types}",
            status="in_progress"
        )
        db.add(run)
        db.commit()
        logger.info(f"Starting run {run.id} with parameters: {run.parameters}")

        for city in cities:
            for tag_name in tags:
                logger.info(f"Processing city: {city}, tag: {tag_name}")
                self._process_pair(db, city, tag_name, institution_types, run.id)

        run.finished_at = datetime.datetime.now(datetime.UTC).isoformat()
        run.status = "completed"
        db.commit()
        logger.info(f"Run {run.id} completed.")

    def _generate_search_query(self, city: str, tag_name: str, institution_types: list[str]) -> str:
        prompt_template = load_prompt("discovery")
        prompt = prompt_template.format(
            institution_types=', '.join(institution_types),
            tag_name=tag_name,
            city=city
        )
        query = llm_provider.generate(prompt).strip()
        logger.info(f"  - Generated search query: {query}")
        return query

    def _extract_data(self, content: str, url: str) -> dict:
        prompt_template = load_prompt("extraction")
        prompt = prompt_template.format(url=url, content=content)
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

    def _find_duplicate(self, db: Session, entity_data: EntityCreate) -> Entity | None:
        existing_entity = db.query(Entity).filter(
            (Entity.name == entity_data.name) | (Entity.website == str(entity_data.website))
        ).first()
        return existing_entity

    def _persist_entity(self, db: Session, entity_data: EntityCreate, url: str, run_id: int):
        now = datetime.datetime.now(datetime.UTC).isoformat()
        
        entity_dict = entity_data.model_dump()
        if 'website' in entity_dict and entity_dict['website'] is not None:
            entity_dict['website'] = str(entity_dict['website'])

        new_entity = Entity(
            **entity_dict,
            created_at=now,
            updated_at=now,
            run_id=run_id
        )
        db.add(new_entity)
        db.commit()

        new_source = Source(
            entity_id=new_entity.id,
            url=url,
            retrieved_at=now,
            run_id=run_id
        )
        db.add(new_source)
        db.commit()
        logger.info(f"  - Persisted new entity '{new_entity.name}' with id {new_entity.id}")

    def _process_pair(self, db: Session, city: str, tag_name: str, institution_types: list[str], run_id: int):
        search_query = self._generate_search_query(city, tag_name, institution_types)
        
        urls = scraper.retrieve_content(search_query)
        for url in urls:
            if not scraper.robots_checker.can_fetch(url):
                logger.info(f"Skipping {url} due to robots.txt")
                continue

            content = scraper.get_page_content(url)
            if content:
                extracted_data = self._extract_data(content, url)
                if extracted_data:
                    logger.info(f"  - Extracted: {extracted_data.get('name')}")
                    validated_entity = self._normalize_and_validate(extracted_data)
                    if validated_entity:
                        logger.info(f"  - Validated: {validated_entity.name}")
                        duplicate = self._find_duplicate(db, validated_entity)
                        if duplicate:
                            logger.info(f"  - Found duplicate for '{validated_entity.name}'. Merging/flagging for review.")
                            # Merge logic will be implemented in a later task
                        else:
                            self._persist_entity(db, validated_entity, url, run_id)
        pass

agent = Agent()
