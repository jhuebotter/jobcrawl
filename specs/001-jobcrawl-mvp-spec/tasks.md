# Tasks: JobCrawl MVP

**Input**: Design documents from `specs/001-jobcrawl-mvp-spec/`

---

## Phase 1: Setup & Configuration

**Purpose**: Initialize the project structure, environment, and configuration.

- [ ] T001 [P] Create the backend and frontend directory structures in the repository root.
- [ ] T002 [P] Create the `environment.yml` file with core backend dependencies (Python, FastAPI, Uvicorn, SQLAlchemy, Pydantic).
- [ ] T003 [P] Create a `.env.example` file in the root directory for the `GEMINI_API_KEY`.
- [ ] T004 [P] Initialize the frontend project with `npm init` and create placeholder directories.
- [ ] T005 Update `specs/001-jobcrawl-mvp-spec/quickstart.md` with mamba-first (and conda fallback) environment setup instructions.
- [ ] T006 Update the root `README.md` with a project overview and a link to the quickstart guide.

---

## Phase 2: Foundational Backend

**Purpose**: Build the core data and service layers of the backend.

- [ ] T007 Implement the database schema in `backend/src/models/schema.py` based on `data-model.md`.
- [ ] T008 Create a database initialization script in `backend/src/core/db.py` to create the SQLite database and tables.
- [ ] T009 Implement Pydantic models for data validation in `backend/src/models/validation.py`.
- [ ] T010 [P] Create the LLM provider abstraction in `backend/src/core/provider.py` with a default Gemini implementation.
- [ ] T011 Implement a simple rate-limiting mechanism in the LLM provider abstraction in `backend/src/core/provider.py`.
- [ ] T012 [P] Create placeholder prompt files in `backend/src/prompts/` (e.g., `discovery.txt`, `extraction.txt`, `enrichment.txt`).
- [ ] T013 Implement a utility in `backend/src/core/scraping.py` to check `robots.txt` before fetching a URL.
- [ ] T014 Implement a structured logging configuration in `backend/src/core/logging.py`.
- [ ] T015 Write unit tests for the data validation models in `backend/tests/unit/test_validation.py`.
- [ ] T016 **Checkpoint**: Run tests to confirm the data layer is solid.

---

## Phase 3: User Story 1 - Configure and Run a Discovery Agent

**Goal**: Implement the core agentic discovery loop.
**Independent Test**: A user can define tags, configure a run via the API, and see new entities persisted in the database.

- [ ] T017 [US1] Implement the main orchestration loop for (city × tag) processing in `backend/src/core/agent.py`.
- [ ] T018 [US1] Implement search query generation logic within the agent in `backend/src/core/agent.py`.
- [ ] T019 [US1] Implement the web retrieval step, using the `robots.txt` checker, in `backend/src/core/scraping.py`.
- [ ] T020 [US1] Implement the data extraction step using the LLM provider in `backend/src/core/agent.py`.
- [ ] T021 [US1] Implement data normalization and validation for extracted data in `backend/src/core/agent.py`.
- [ ] T022 [US1] Implement the deduplication and merge proposal logic against the database in `backend/src/core/agent.py`.
- [ ] T023 [US1] Implement the logic to persist new/updated entities and their provenance in `backend/src/core/agent.py`.
- [ ] T024 [US1] Implement the API endpoint for creating and listing tags (`POST /api/tags`, `GET /api/tags`) in `backend/src/api/tags.py`.
- [ ] T025 [US1] Implement the API endpoint for starting and listing runs (`POST /api/runs`, `GET /api/runs`) in `backend/src/api/runs.py`.
- [ ] T026 [US1] Write integration tests for the tags and runs API endpoints in `backend/tests/integration/test_api_runs.py`.
- [ ] T027 [P] [US1] Create the placeholder `TagManager` view component in `frontend/src/pages/TagManager.js`.
- [ ] T028 [P] [US1] Create the placeholder `RunPanel` view component in `frontend/src/pages/RunPanel.js`.
- [ ] T029 **Checkpoint**: Manually test the API endpoints to confirm a run can be started and its state is logged.

---

## Phase 4: User Story 2 - Explore and Filter Discovered Entities

**Goal**: Allow users to see and interact with the data.
**Independent Test**: A user can retrieve a filtered list of entities from the API and export it.

- [ ] T030 [US2] Implement the API endpoint for listing and filtering entities (`GET /api/entities`) in `backend/src/api/entities.py`.
- [ ] T031 [US2] Implement the API endpoint for exporting entities (`GET /api/export`) in `backend/src/api/export.py`.
- [ ] T032 [US2] Write integration tests for the entities and export API endpoints in `backend/tests/integration/test_api_entities.py`.
- [ ] T033 [P] [US2] Create the placeholder `BrowseView` component in `frontend/src/pages/BrowseView.js`.
- [ ] T034 [P] [US2] Create the placeholder `EntityDetail` view component in `frontend/src/pages/EntityDetail.js`.
- [ ] T035 **Checkpoint**: Manually test the API to confirm entities can be filtered and exported correctly.

---

## Phase 5: User Story 4 - Manually Add and Autocomplete Entities

**Goal**: Implement the AI-assisted manual entry feature.
**Independent Test**: A user can submit a new entity with minimal data, and the agent will complete and save it.

- [ ] T036 [US4] Implement the agentic logic for single-entity enrichment in `backend/src/core/curation.py`.
- [ ] T037 [US4] Implement the API endpoint for AI-assisted entity creation (`POST /api/entities/autocomplete`) in `backend/src/api/entities.py`.
- [ ] T038 [US4] Implement the API endpoint for the review queue (`GET /api/review_queue`) in `backend/src/api/review.py`.
- [ ] T039 [US4] Write integration tests for the new autocomplete and review queue endpoints in `backend/tests/integration/test_api_curation.py`.
- [ ] T040 [P] [US4] Create the placeholder "Add Entity" form component in `frontend/src/components/AddEntityForm.js`.
- [ ] T041 [P] [US4] Create the placeholder `ReviewQueue` view component in `frontend/src/pages/ReviewQueue.js`.
- [ ] T042 **Checkpoint**: Manually test the autocomplete endpoint to confirm it enriches and saves a new entity.

---

## Phase 6: User Story 3 - Curate and Manage Data

**Goal**: Implement data editing, starring, and the undo feature.
**Independent Test**: A user can edit an entity, star it, and undo the last run, with all changes correctly reflected in the database.

- [ ] T043 [US3] Implement the API endpoint for updating an entity (`PUT /api/entities/{entity_id}`) in `backend/src/api/entities.py`.
- [ ] T044 [US3] Implement the API endpoints for starring/unstarring an entity in `backend/src/api/entities.py`.
- [ ] T045 [US3] Implement the "Undo Last Run" logic in `backend/src/core/agent.py`.
- [ ] T046 [US3] Implement the API endpoint for undoing the last run (`POST /api/runs/undo_last`) in `backend/src/api/runs.py`.
- [ ] T047 [US3] Write integration tests for the update, star, and undo endpoints in `backend/tests/integration/test_api_edits.py`.
- [ ] T048 **Checkpoint**: Manually test all curation features via the API.

---

## Phase 7: Polish & Hardening

**Purpose**: Improve robustness, user experience, and documentation.

- [ ] T049 [P] Implement user-friendly error handling and messaging in the backend API.
- [ ] T050 [P] Create placeholder components for empty states (e.g., no entities found) in the frontend.
- [ ] T051 Write the E2E smoke test script in `backend/tests/e2e/test_smoke.py`.
- [ ] T052 Final review and update of `README.md` and `quickstart.md`.
- [ ] T053 Run all tests and confirm they pass.

---

## Summary

| Category | Count |
|---|---|
| Total Tasks | 53 |
| Parallelizable Tasks | 11 |
| **Tasks per Phase** | |
| Phase 1: Setup | 6 |
| Phase 2: Foundational | 10 |
| Phase 3: US1 | 13 |
| Phase 4: US2 | 6 |
| Phase 5: US4 | 7 |
| Phase 6: US3 | 6 |
| Phase 7: Polish | 5 |

**Suggested MVP Path**: Completing Phases 1, 2, and 3 will deliver the core value proposition: a user can configure and run the agent to collect data. This is the smallest end-to-end slice.