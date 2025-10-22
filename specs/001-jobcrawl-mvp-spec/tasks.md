# Tasks: JobCrawl MVP

**Input**: Design documents from `specs/001-jobcrawl-mvp-spec/`

---

## Phase 1: Foundational Setup & Test Environment

**Purpose**: Solidify the project's foundation and ensure the test environment is robust and reliable.

- [x] T01.01 [P] Update `environment.yml` to ensure `fastapi`, `sqlalchemy`, `pydantic`, `python-dotenv`, `google-generativeai`, `pytest`, `httpx`, and `google-search-results` are included.
- [x] T01.02 [P] Verify the `backend` and `frontend` directory structures match the `plan.md`.
- [x] T01.03 [P] Update `backend/src/models/schema.py` and `backend/src/models/validation.py` to be fully consistent with the final `data-model.md`.
- [x] T01.04 Refactor `backend/src/core/db.py` to include the canonical `get_db` function.
- [x] T01.05 Refactor all API routers in `backend/src/api/` to use the canonical `get_db` function.
- [x] T01.06 Refactor `backend/tests/conftest.py` to use the `StaticPool` and app factory pattern for a reliable, in-memory test database.
- [x] T01.07 **Checkpoint**: Run all existing integration tests and confirm they pass with the new test setup.
- [x] T01.08 **Git**: Commit and push all foundational setup changes with message "refactor: Solidify foundational backend and test setup".

---

## Phase 2: Foundational Backend API

**Purpose**: Implement the full skeleton of the backend API, ensuring all endpoints are defined and testable before adding complex business logic.

- [x] T02.01 [P] Implement the basic CRUD endpoints for tags (`create_tag`, `read_tags`) in `backend/src/api/tags.py`.
- [x] T02.02 [P] Implement the skeleton for all entity endpoints (`read_entities`, `update_entity`, `autocomplete_entity`) in `backend/src/api/entities.py`.
- [x] T02.03 [P] Implement the skeleton for all run endpoints (`create_run`, `read_runs`, `undo_last_run`) in `backend/src/api/runs.py`.
- [x] T02.04 [P] Implement the skeleton for the review queue endpoints in `backend/src/api/review.py`.
- [x] T02.05 [P] Implement the skeleton for the export endpoint in `backend/src/api/export.py`.
- [x] T02.06 Write basic integration tests for each skeleton endpoint in the `backend/tests/integration/` directory to ensure they are reachable and return correct status codes.
- [x] T02.07 **Checkpoint**: Run all integration tests against the skeleton API and confirm they pass.
- [ ] T02.08 **Git**: Commit and push the complete API skeleton with message "feat: Implement foundational API skeleton".

---

## Phase 3: User Story 1 - Core Agent Implementation (Golden Path)

**Goal**: Implement the core agentic discovery loop, moving from mock to real implementation, driven by a comprehensive integration test.

### Sub-Phase 3.1: Prompt Engineering

- [ ] T03.01 [US1] Create a utility function in `backend/src/core/prompts.py` to load prompt templates from the `backend/src/prompts/` directory.
- [ ] T03.02 [US1] Write a unit test for the prompt loading utility in `backend/tests/unit/test_prompts.py`.
- [ ] T03.03 [P] [US1] Write the first version of the search query generation prompt in `backend/src/prompts/discovery.txt`.
- [ ] T03.04 [P] [US1] Write the first version of the data extraction prompt in `backend/src/prompts/extraction.txt`, ensuring it explicitly requests valid JSON with a confidence score.

### Sub-Phase 3.2: Real Agent Logic

- [ ] T03.05 [US1] **Upgrade** `backend/src/core/scraping.py`: Implement a real web search function using the `google-search-results` library.
- [ ] T03.06 [US1] **Upgrade** `backend/src/core/agent.py`: Implement the `_generate_search_query` method to use the `discovery.txt` prompt.
- [ ] T03.07 [US1] **Upgrade** `backend/src/core/agent.py`: In the `_process_pair` method, explicitly call the `robots_checker.can_fetch()` method from `scraping.py` before attempting to scrape any URL.
- [ ] T03.08 [US1] **Upgrade** `backend/src/core/agent.py`: Implement the `_extract_data` method to use the `extraction.txt` prompt and include robust JSON parsing.
- [ ] T03.09 [US1] Write a unit test for the `_normalize_and_validate` method in `backend/tests/unit/test_agent.py`.
- [ ] T03.10 [US1] Implement the LLM-driven deduplication logic in the `_find_duplicate` method in `backend/src/core/agent.py`.
- [ ] T03.11 [US1] **Upgrade** `backend/src/core/agent.py`: Implement the full `_process_pair` orchestration logic, calling all helper methods in sequence.

### Sub-Phase 3.3: "Golden Path" E2E Integration Test

- [ ] T03.12 [US1] Create the new test file `backend/tests/integration/test_agent_e2e.py`.
- [ ] T03.13 [US1] In `test_agent_e2e.py`, write a `test_golden_path` function that runs the agent for a single, hardcoded query and asserts that a valid, structured `Entity` is created in the test database.
- [ ] T03.14 [US1] **Checkpoint**: Run the `test_golden_path` and ensure it passes, proving the core agent logic works end-to-end.
- [ ] T03.15 [US1] **Git**: Commit and push all Golden Path changes with message "feat(US1): Implement Golden Path E2E test".

---

## Phase 4: API Generalization & US2 Implementation

**Goal**: Connect the functional agent to the API and implement the entity browsing and filtering features.

- [ ] T04.01 [US1] **Upgrade** the `POST /api/runs` endpoint in `backend/src/api/runs.py` to run the agent as a background task using FastAPI's `BackgroundTasks`.
- [ ] T04.02 [US1] **Upgrade** the `agent.start_run` method to accept dynamic tags and cities from the API.
- [ ] T04.03 [US1] Write a full integration test for the `POST /api/runs` endpoint in `backend/tests/integration/test_api_runs.py`.
- [ ] T04.04 [US2] Implement comprehensive filtering logic in the `GET /api/entities` endpoint in `backend/src/api/entities.py`.
- [ ] T04.05 [US2] Write integration tests for all filter parameters of the `GET /api/entities` endpoint in `backend/tests/integration/test_api_entities.py`.
- [ ] T04.06 [US2] Implement the `GET /api/export` endpoint in `backend/src/api/export.py`.
- [ ] T04.07 [US2] Write integration tests for the export endpoint in `backend/tests/integration/test_api_entities.py`.
- [ ] T04.08 [P] [US2] Create the placeholder `BrowseView.js` and `EntityDetail.js` components in `frontend/src/pages/`.
- [ ] T04.09 [US1, US2] **Checkpoint**: Start the servers, open the browser, and manually verify that you can start a run from the API and see the results appear when you query the entities endpoint.
- [ ] T04.10 [US1, US2] **Git**: Commit and push all API generalization and US2 changes with message "feat(US1, US2): Generalize API and implement entity browsing".

---

## Phase 5: User Story 4 - Manually Add and Autocomplete Entities

**Goal**: Implement the AI-assisted manual data entry feature.

- [ ] T05.01 [US4] Implement the single-entity enrichment logic in `backend/src/core/curation.py`.
- [ ] T05.02 [US4] Implement the `POST /api/entities/autocomplete` endpoint in `backend/src/api/entities.py`.
- [ ] T05.03 [US4] Implement the `GET /api/review_queue` endpoint in `backend/src/api/review.py`.
- [ ] T05.04 [US4] Write integration tests for the autocomplete and review queue endpoints in `backend/tests/integration/test_api_curation.py`.
- [ ] T05.05 [P] [US4] Create placeholder components `AddEntityForm.js` and `ReviewQueue.js` in `frontend/src/`.
- [ ] T05.06 [US4] **Checkpoint**: Manually test the autocomplete endpoint to confirm it enriches and saves a new entity.
- [ ] T05.07 [US4] **Git**: Commit and push all US4 changes with message "feat(US4): Implement AI-assisted curation".

---

## Phase 6: User Story 3 - Curate and Manage Data

**Goal**: Implement manual editing, starring, and the undo feature.

- [ ] T06.01 [US3] Implement the `PUT /api/entities/{entity_id}` endpoint in `backend/src/api/entities.py`.
- [ ] T06.02 [US3] Implement the starring/unstarring endpoints in `backend/src/api/entities.py`.
- [ ] T06.03 [US3] Implement the "Undo Last Run" logic in `backend/src/core/agent.py`.
- [ ] T06.04 [US3] Implement the `POST /api/runs/undo_last` endpoint in `backend/src/api/runs.py`.
- [ ] T06.05 [US3] Write integration tests for all edit, star, and undo endpoints in `backend/tests/integration/test_api_edits.py`.
- [ ] T06.06 [US3] **Checkpoint**: Manually test all curation features via the API.
- [ ] T06.07 [US3] **Git**: Commit and push all US3 changes with message "feat(US3): Implement data curation and undo".

---

## Phase 7: Polish & Finalization

**Purpose**: Finalize the application for MVP release.

- [ ] T07.01 [P] Implement user-friendly error handling across the API.
- [ ] T07.02 [P] Create basic empty states in the frontend placeholder components.
- [ ] T07.03 Write the final E2E smoke test in `backend/tests/e2e/test_smoke.py`.
- [ ] T07.04 Final review and update of all documentation (`README.md`, `quickstart.md`).
- [ ] T07.05 **Checkpoint**: Run all tests (`unit`, `integration`, `e2e`) and confirm 100% pass rate.
- [ ] T07.06 **Git**: Commit and push all final changes with message "chore: Finalize MVP and run all tests".
