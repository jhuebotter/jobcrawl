from typing import List, Dict, Optional
from google import genai
from backend.src.models.validation import Location, EntityList
from backend.src.core.db import get_db, find_or_create_entity, SessionLocal
import asyncio
import time
from datetime import datetime, timezone
import json
import os


class Agent:
    def __init__(self, model: str = "gemini-3-pro-preview", mock: bool = False):
        self.client = genai.Client()
        self.max_batch_size = 100  # Configurable batch size limit - each batch becomes one Google AI batch job
        self.model = model
        self.mock = mock or "PYTEST_CURRENT_TEST" in os.environ

    async def start_run(
        self,
        db=None,
        tags: Optional[List[str]] = None,
        locations: Optional[List[Location]] = None,
        institution_types: Optional[List[str]] = None,
        run_id: Optional[str] = None,
        count: int = 5,
        include_google_search: bool = True,
    ):
        """Execute complete search run with batch processing

        If any parameter is None, searches across all known values for that dimension.
        """
        # Check if in test mode
        is_test = "PYTEST_CURRENT_TEST" in os.environ
        if is_test:
            self.mock = True
        if db is None:
            close_db = True
            db = SessionLocal()
        else:
            close_db = False

        created_run_id = None
        try:
            # Fill in defaults for missing parameters
            if tags is None:
                from backend.src.models.schema import Tag as TagModel

                tags = [tag.name for tag in db.query(TagModel).all()]

            if locations is None:
                from backend.src.models.schema import Entity

                # Get unique city/country combinations from existing entities
                unique_locations = (
                    db.query(Entity.city, Entity.country).distinct().all()
                )
                locations = [
                    Location(city=city, country=country)
                    for city, country in unique_locations
                ]

            if institution_types is None:
                from backend.src.models.validation import entity_types

                institution_types = entity_types

            # Validate we have something to search
            if not tags or not locations or not institution_types:
                raise ValueError(
                    "No search parameters available - ensure database has tags/entities or provide explicit parameters"
                )

            # Create Run record if not provided
            if run_id is None:
                from backend.src.models.schema import Run

                run = Run(
                    status="initialized",
                    started_at=datetime.now(timezone.utc),
                    parameters=json.dumps(
                        {
                            "tags": tags,
                            "locations": [
                                {"city": l.city, "country": l.country}
                                for l in locations
                            ],
                            "institution_types": institution_types,
                            "count": count,
                            "include_google_search": include_google_search,
                        }
                    ),
                )
                db.add(run)
                db.commit()
                run_id = run.id
                created_run_id = run_id
                print(f"Created new run with ID: {run_id}")

                # Update status to pending as we start processing
                run.status = "pending"
                db.commit()

            print(
                f"Starting run with {len(tags)} tags, {len(locations)} locations, {len(institution_types)} types"
            )  # Generate all combinations: (location, tag, entity_type)
            print(
                f"Mock mode: {self.mock}, env PYTEST: {'PYTEST_CURRENT_TEST' in os.environ}"
            )
            search_combinations = self.generate_search_combinations(
                locations, tags, institution_types
            )

            print(f"Generated {len(search_combinations)} search combinations")

            # Process in batches
            all_results = {}
            total_input_tokens = 0
            total_output_tokens = 0
            total_thinking_tokens = 0
            total_tool_tokens = 0

            for batch in self.chunk_combinations(
                search_combinations, self.max_batch_size
            ):
                print(f"Processing batch of {len(batch)} combinations")
                assert (
                    run_id is not None
                ), "run_id should be set before processing batches"
                batch_results, batch_tokens = await self.process_batch(
                    db, batch, count, include_google_search, run_id
                )
                all_results.update(batch_results)

                # Accumulate token usage across batches
                for combination_key, (
                    input_t,
                    output_t,
                    thinking_t,
                    tool_t,
                ) in batch_tokens.items():
                    total_input_tokens += input_t
                    total_output_tokens += output_t
                    total_thinking_tokens += thinking_t
                    total_tool_tokens += tool_t

            # Save results with deduplication
            # run_id should be set by now
            assert run_id is not None, "run_id should be set before saving results"
            final_run_id = await self.save_batch_results(
                db,
                all_results,
                run_id,
                tags,
                locations,
                institution_types,
                total_input_tokens,
                total_output_tokens,
                total_thinking_tokens,
                total_tool_tokens,
            )
            print(f"Run completed with ID: {final_run_id}")

            return final_run_id

        except Exception as e:
            # Handle crashes by updating run status to crashed
            if created_run_id:
                try:
                    if not close_db:
                        crashed_run = (
                            db.query(Run).filter(Run.id == created_run_id).first()
                        )
                        if crashed_run:
                            crashed_run.status = "crashed"
                            db.commit()
                    else:
                        # Need to create a new session to update status
                        temp_db = SessionLocal()
                        crashed_run = (
                            temp_db.query(Run).filter(Run.id == created_run_id).first()
                        )
                        if crashed_run:
                            crashed_run.status = "crashed"
                            temp_db.commit()
                        temp_db.close()
                except Exception:
                    # If we can't update the status, just continue
                    pass

            raise e
        finally:
            if close_db:
                db.close()

    def generate_search_combinations(
        self, locations: List[Location], tags: List[str], institution_types: List[str]
    ) -> List[Dict]:
        """Generate all combinations of location × tag × entity_type"""
        combinations = []
        for location in locations:
            for tag in tags:
                for entity_type in institution_types:
                    combinations.append(
                        {
                            "location": location,
                            "tag": tag,
                            "entity_type": entity_type,
                            "run_id": None,  # Will be set later
                        }
                    )
        return combinations

    def chunk_combinations(self, combinations: List, batch_size: int) -> List[List]:
        """Split combinations into batches"""
        return [
            combinations[i : i + batch_size]
            for i in range(0, len(combinations), batch_size)
        ]

    def load_prompt_template(self, filename: str = "search_prompt_template.txt") -> str:
        """Load a prompt template from the prompts directory"""
        path = f"backend/src/prompts/{filename}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def build_prompt(
        self,
        template: str,
        *,
        city: str,
        country: str,
        topic: str,
        count: int,
        target_type: str,
    ) -> str:
        """Fill the template with dynamic fields (same as scratch file)"""
        from backend.src.models.validation import entity_types, entity_descriptions

        def all_entity_type_names() -> str:
            return ", ".join(entity_types)

        def build_type_definitions() -> str:
            lines = []
            for et_name, desc in entity_descriptions.items():
                lines.append(f"- {et_name}: {desc}")
            return "\n".join(lines)

        return template.format(
            city=city,
            country=country,
            topic=topic,
            count=count,
            target_type=target_type,
            all_types=all_entity_type_names(),
            type_definitions=build_type_definitions(),
        )

    def build_enriched_prompt(
        self, db, location: Location, tag: str, entity_type: str
    ) -> str:
        """Generate addon text with existing entities context to avoid duplicates"""
        # Get existing entities for this location/tag/type combination
        from backend.src.models.schema import Entity, EntityTag

        existing_entities = (
            db.query(Entity)
            .join(EntityTag)
            .filter(
                Entity.city == location.city,
                Entity.country == location.country,
                EntityTag.tag.has(name=tag),
                Entity.type == entity_type,
            )
            .all()
        )

        # Build context string as addon text
        if existing_entities:
            context = f"\nExisting {entity_type} entities in {location.city}, {location.country} that you should NOT rediscover:\n"
            for entity in existing_entities:
                context += f"- {entity.name}"
                if entity.website:
                    context += f" ({entity.website})"
                context += "\n"
            context += (
                "\nPlease find NEW organizations that are NOT in this list above.\n"
            )
        else:
            context = f"\nNo existing {entity_type} entities found in {location.city}, {location.country} for this topic yet.\n"

        return context

    async def process_batch(
        self,
        db,
        batch: List[Dict],
        count: int,
        include_google_search: bool,
        run_id: str,
    ) -> tuple[Dict[str, EntityList], Dict[str, tuple[int, int, int, int]]]:
        """Process a batch of search combinations using Google Gemini Batch API

        Creates a single batch job with multiple inline requests and polls for completion.

        Returns:
            tuple: (results_dict, token_usage_dict)
                results_dict: {combination_key: EntityList}
                token_usage_dict: {combination_key: (input_tokens, output_tokens, thinking_tokens, tool_tokens)}
        """
        results = {}
        token_usage = {}

        if self.mock:
            # Load dummy response
            with open("dummy_response.txt", "r") as f:
                dummy_json = f.read()
            entity_list = EntityList.model_validate_json(dummy_json)
            print(f"Mock parsed entities: {entity_list}")
            dummy_tokens = (10, 20, 5, 3)
            for combination in batch:
                location = combination["location"]
                tag = combination["tag"]
                entity_type = combination["entity_type"]
                combination_key = f"{location.city}_{tag}_{entity_type}"
                results[combination_key] = entity_list
                token_usage[combination_key] = dummy_tokens
            return results, token_usage

        # Load the main prompt template once for the batch
        main_template = self.load_prompt_template()

        # Build inline requests for all combinations in this batch
        inline_requests = []
        combination_keys = []

        for combination in batch:
            location = combination["location"]
            tag = combination["tag"]
            entity_type = combination["entity_type"]
            combination_key = f"{location.city}_{tag}_{entity_type}"
            combination_keys.append(combination_key)

            # Generate enriched addon text
            enriched_addon = self.build_enriched_prompt(db, location, tag, entity_type)

            # Build the base prompt with template placeholders filled
            base_prompt = self.build_prompt(
                main_template,
                city=location.city,
                country=location.country,
                topic=tag,
                count=count,
                target_type=entity_type,
            )

            # Combine base prompt with enriched addon
            final_prompt = base_prompt.replace(
                "Return only valid JSON that matches the provided schema.",
                f"{enriched_addon}\nReturn only valid JSON that matches the provided schema.",
            )

            # DEBUG: Print final prompt during development
            print(f"\n=== Final Prompt for {combination_key} ===")
            print(final_prompt)
            print("=" * 50)

            # Create inline request (same format as scratch file)
            tools = []
            if include_google_search:
                tools.extend([{"url_context": {}}, {"google_search": {}}])

            req = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": final_prompt}],
                    }
                ],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": EntityList.model_json_schema(),
                    "tools": tools,
                },
            }
            inline_requests.append(req)

        # Submit batch job
        batch_job = self.client.batches.create(
            model=self.model,
            src=inline_requests,
            config={
                "display_name": f"jobcrawl-batch-{len(batch)}-combinations",
            },
        )

        job_name = batch_job.name
        if job_name is None:
            print("Batch job name is None - cannot poll for status")
            # Update run status to failed
            from backend.src.models.schema import Run

            failed_run = db.query(Run).filter(Run.id == run_id).first()
            if failed_run:
                failed_run.status = "failed"
                db.commit()
            # Return empty results for all combinations in this batch
            for combination_key in combination_keys:
                results[combination_key] = EntityList(results=[])
                token_usage[combination_key] = (0, 0, 0, 0)
            return results, token_usage

        print(f"Created batch job: {job_name} with {len(batch)} requests")

        # Update run status to running
        from backend.src.models.schema import Run

        run = db.query(Run).filter(Run.id == run_id).first()
        if run:
            run.status = "running"
            db.commit()

        # Poll for completion (same as scratch file)
        terminal_states = {
            "JOB_STATE_SUCCEEDED",
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
        }

        while True:
            batch_job = self.client.batches.get(name=job_name)
            if batch_job is None or batch_job.state is None:
                print(f"Failed to get batch job status for {job_name}")
                break
            state_name = batch_job.state.name
            if state_name in terminal_states:
                break
            print(
                f"Batch job {job_name} not finished. State: {state_name}. Waiting 10 seconds..."
            )
            await asyncio.sleep(10)  # Use asyncio.sleep for async

        if batch_job is None or batch_job.state is None:
            print("Batch job object is None")
            # Update run status to failed
            if run:
                run.status = "failed"
                db.commit()
            # Return empty results for all combinations in this batch
            for combination_key in combination_keys:
                results[combination_key] = EntityList(results=[])
                token_usage[combination_key] = (0, 0, 0, 0)
            return results, token_usage

        state_name = batch_job.state.name
        print(f"Batch job {job_name} finished with state: {state_name}")

        if state_name != "JOB_STATE_SUCCEEDED":
            print(f"Batch job failed with state: {state_name}")
            # Update run status to failed
            if run:
                run.status = "failed"
                db.commit()
            # Return empty results for all combinations in this batch
            for combination_key in combination_keys:
                results[combination_key] = EntityList(results=[])
                token_usage[combination_key] = (0, 0, 0, 0)
            return results, token_usage

        # Process responses (same as scratch file)
        if batch_job.dest is None or batch_job.dest.inlined_responses is None:
            print("No responses found in batch job")
            # Return empty results for all combinations in this batch
            for combination_key in combination_keys:
                results[combination_key] = EntityList(results=[])
                token_usage[combination_key] = (0, 0, 0, 0)
            return results, token_usage

        inlined_responses = batch_job.dest.inlined_responses

        print(f"inlined_responses type: {type(inlined_responses)}")
        print(
            f"inlined_responses length: {len(inlined_responses) if inlined_responses else 'None'}"
        )

        for idx, inline_response in enumerate(inlined_responses):
            print(f"inline_response[{idx}] type: {type(inline_response)}")
            # print(f"inline_response[{idx}] attributes: {dir(inline_response) if inline_response else 'None'}")

            if inline_response is None:
                print(f"inline_response[{idx}] is None!")
                continue

            response = getattr(inline_response, "response", None)
            # print(f"response for inline_response[{idx}]: {response}")

            if response is None:
                print(
                    f"Response for inline_response[{idx}] is None - checking for error..."
                )
                error = getattr(inline_response, "error", None)
                if error:
                    print(f"Error in inline_response[{idx}]: {error}")
                continue

            combination_key = combination_keys[idx]

            # Parse response and extract both entities and token usage
            entity_list, tokens = self.parse_gemini_response(response)
            results[combination_key] = entity_list
            token_usage[combination_key] = tokens

        return results, token_usage

    def parse_gemini_response(
        self, response
    ) -> tuple[EntityList, tuple[int, int, int, int]]:
        """Parse Gemini API response into EntityList and token usage

        Returns:
            tuple: (EntityList, (input_tokens, output_tokens, thinking_tokens, tool_tokens))
        """
        # Check for errors
        if hasattr(response, "error") and response.error:
            print(f"Gemini API error: {response.error}")
            return EntityList(results=[]), (0, 0, 0, 0)

        # Parse JSON response into EntityList
        try:
            entity_list = EntityList.model_validate_json(response.text)
            print(f"Parsed entities: {entity_list}")
        except Exception as e:
            print(f"Failed to parse Gemini response as EntityList: {e}")
            print(f"Raw response: {response}")
            entity_list = EntityList(results=[])

        # Extract token usage
        usage = getattr(response, "usage_metadata", None)
        if usage is None:
            tokens = (0, 0, 0, 0)
        else:
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0
            thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0
            tool_tokens = getattr(usage, "tool_use_prompt_token_count", 0) or 0
            tokens = (input_tokens, output_tokens, thinking_tokens, tool_tokens)

        return entity_list, tokens

    async def save_batch_results(
        self,
        db,
        results: Dict[str, EntityList],
        run_id: str,  # Now required since run should already exist
        tags: List[str],
        locations: List[Location],
        institution_types: List[str],
        input_tokens: int,
        output_tokens: int,
        thinking_tokens: int,
        tool_tokens: int,
    ) -> str:
        """Save all batch results with deduplication and complete the run"""
        from backend.src.models.schema import Run
        from backend.src.core.db import find_or_create_entity

        # Get the existing run
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")

        # Process results and save entities
        total_entities = 0
        for combination_key, entity_list in results.items():
            for entity_data in entity_list.results:
                print(f"Saving entity: {entity_data.model_dump()}")
                # Create entity with deduplication
                entity = find_or_create_entity(
                    db=db,
                    name=entity_data.name,
                    city=entity_data.city,
                    country=entity_data.country,
                    entity_type=entity_data.type.value,
                    tags=tags,  # Use the search tags
                    website=str(entity_data.website) if entity_data.website else None,
                    description=entity_data.description,
                )
                print(f"Created/found entity: {entity.name}, id: {entity.id}")
                # Associate with run
                entity.run_id = run_id
                total_entities += 1

        # Update run with final results and completion status
        if not self.mock:
            run.status = "completed"
            run.finished_at = datetime.now(timezone.utc)
            run.results_summary = (
                f"Found {total_entities} entities across {len(results)} combinations"
            )
            run.input_tokens = input_tokens
            run.output_tokens = output_tokens
            run.thinking_tokens = thinking_tokens
            run.tool_tokens = tool_tokens
        db.commit()

        return run_id

    # Specialized search methods (Option B)
    async def search_by_tags(self, tags: List[str], run_id: Optional[str] = None):
        """Search for entities with specific tags across all known locations and types"""
        return await self.start_run(tags=tags, run_id=run_id)

    async def search_by_locations(
        self, locations: List[Location], run_id: Optional[str] = None
    ):
        """Search for entities in specific locations across all known tags and types"""
        return await self.start_run(locations=locations, run_id=run_id)

    async def search_by_types(
        self, institution_types: List[str], run_id: Optional[str] = None
    ):
        """Search for entities of specific types across all known locations and tags"""
        return await self.start_run(institution_types=institution_types, run_id=run_id)

    async def search_everything(self, run_id: Optional[str] = None):
        """Search across all known tags, locations, and types"""
        return await self.start_run(run_id=run_id)


# Global agent instance
agent = Agent()
agent_mock = Agent(mock=True)
