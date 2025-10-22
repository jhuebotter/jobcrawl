# Implementation Plan: JobCrawl MVP

**Branch**: `001-jobcrawl-mvp-spec` | **Date**: 2025-10-17 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `specs/001-jobcrawl-mvp-spec/spec.md`

## Summary

This plan outlines the implementation of the JobCrawl MVP, a local-first, single-user web application for discovering and managing professional entities. The backend will be an agentic system written in Python, and the frontend will be a reactive web interface. This plan has been updated to focus on a concrete, test-driven implementation strategy.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**:
- Backend API Framework: **FastAPI**
- Data Storage & ORM: **SQLite** with **SQLAlchemy**
- Data Validation: **Pydantic**
- Agent Orchestration: **Custom Implementation** (sequential, single-threaded)
- LLM Provider API: Google Gemini API (via official Python client)
- Frontend Framework: **React**
- Frontend API Client: **httpx** (or a browser-equivalent like `fetch`)
**Storage**: Local SQLite database file (`jobcrawl.db`).
**Testing**:
- **Unit Tests**: Pytest will be used to test individual functions in isolation. Coverage must include data normalization functions, deduplication scoring logic, and business logic in services.
- **Integration Tests**: Pytest with a `TestClient` will verify that API endpoints interact correctly with the database. Coverage must include filtering logic, the "Undo last run" feature, and user-generated data operations.
- **E2E Tests**: A minimal smoke test will simulate a full user story: create a tag, start a run, verify entities are created in the DB, export the results, and successfully undo the run.
**Target Platform**: OS-agnostic (macOS, Linux, Windows).
**Project Type**: Web Application (local-first).
**Performance Goals**: UI filtering and sorting responds in <1 second for a database of 500 entities.
**Constraints**: Must respect `robots.txt`. All data processing and storage is local by default, except for calls to the Gemini API.

## Constitution Check

- [X] **Intent-First Specification**: The specification is clear on the what and why.
- [X] **Privacy-by-Design & Local-First**: The plan prioritizes local data and processing.
- [X] **Provenance & Traceability**: The plan includes measures for auditing and reproducibility.
- [X] **Simplicity & Modularity**: The proposed solution is simple and modular.
- [X] **Quality Gates & Review Discipline**: The plan includes validation and review steps.

## Project Structure

### Documentation (this feature)

```
specs/001-jobcrawl-mvp-spec/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── main.py          # API server entry point
│   ├── core/            # Core logic (agent orchestration, services)
│   ├── models/          # Data models and validation
│   ├── api/             # API endpoint definitions
│   └── prompts/         # LLM prompts
└── tests/
    ├── unit/
    └── integration/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: A standard web application structure with a distinct backend and frontend is appropriate for this project. It promotes separation of concerns and allows for independent development and testing.

## Agent Orchestration Logic

The core of the application is a custom agent orchestrator that processes each `(city x tag)` pair sequentially. The workflow for each pair is as follows:

1.  **Query Generation**: The agent will take the city, tag, and institution types and use the LLM provider with a dedicated prompt from `prompts/discovery.txt` to generate a set of targeted search engine queries.
2.  **Web Search Execution**: The agent will use a web search tool/API to execute each query, collecting a list of relevant URLs.
3.  **Content Scraping**: For each URL, the agent will first check `robots.txt` using a utility in `core/scraping.py`. If allowed, it will fetch the raw HTML content of the page.
4.  **Data Extraction**: The raw HTML content is passed to the LLM provider with a detailed prompt from `prompts/extraction.txt`. The agent expects a structured JSON object back, matching the `Entity` schema, including a `confidence` score.
5.  **Deduplication**:
    *   **Initial Filter**: For a newly extracted entity, the agent will first query the database for potential duplicates (e.g., entities in the same `city` with a similar `name`).
    *   **LLM Fuzzy Match**: If candidates are found, the agent will make a call to the LLM with the new and existing entity data. The prompt will ask the LLM to determine if they represent the same real-world organization.
    *   **Decision**: Based on the LLM's 'yes' or 'no' answer, the entity is either flagged as a duplicate for review or treated as new. "Non-conflicting information" is defined as any field that is empty or null in the existing entity but is present in the new data. All other discrepancies are considered conflicts and must be flagged for review.
6.  **Persistence**: If the entity is new, the validated data is saved to the `entities` table. Its origin URL and the current timestamp are saved to the `sources` table to ensure full provenance.

## Data Normalization

To ensure data consistency and improve the reliability of searches and deduplication, the following normalization rules MUST be applied before any data is persisted to the database:

-   **Whitespace**: All string-based fields (e.g., `name`, `summary`, `city`) must have leading and trailing whitespace removed.
-   **Case for Tags**: All `tag` names must be converted to lowercase to ensure case-insensitive uniqueness (e.g., "AI" and "ai" are treated as the same tag).

## Error Handling

The agent must be resilient to common failures. The following behaviors are required:

-   **Network Errors**: For external API calls (web search, LLM), the agent MUST implement a simple retry mechanism (e.g., 3 retries with exponential backoff).
-   **Partial Run Failure**: If a single `(city x tag)` pair fails for any reason, the agent MUST log the error and continue to the next pair in the run.
-   **Incomplete Extraction**: If the LLM returns an incomplete or unparseable JSON object, the agent MUST discard the result for that URL, log a warning, and continue.
-   **API Key Errors**: The LLM provider MUST raise a specific, catchable exception if the API key is missing or invalid.
-   **Prompt Loading**: The prompt loading utility MUST raise an exception if a required prompt file cannot be found.

## Complexity Tracking

No constitutional violations are anticipated with this revised plan.
