# Checklist: API Requirements Quality

**Purpose**: To validate the clarity, completeness, and consistency of the API requirements before task breakdown.
**Created**: 2025-10-16
**Feature**: `specs/001-jobcrawl-mvp-spec/spec.md`

---

## Requirement Completeness

- [x] **CHK016**: Are the request bodies for `POST /api/tags` and `POST /api/runs` fully specified? [Completeness, contracts/openapi.yaml]
- [x] **CHK017**: Are the success and error response schemas (e.g., for 404 Not Found or 400 Bad Request) defined for every endpoint? [Completeness, Gap]
- [x] **CHK018**: Is there a requirement for an endpoint to manage individual `sources`, or are they only intended to be read-only via an entity? [Gap]
- [x] **CHK019**: Are the requirements for managing the `review_queue` fully defined (e.g., how a user submits a merge decision)? [Completeness, Gap]

## Requirement Clarity

- [x] **CHK020**: Is the filtering logic for `GET /api/entities` clearly specified (e.g., how multiple filters like `tag=X` AND `city=Y` interact)? [Clarity, spec.md §FR-014]
- [x] **CHK021**: Is the sorting behavior (e.g., by field, direction) for all list endpoints (`/api/tags`, `/api/entities`, `/api/runs`) defined? [Clarity, Gap]
- [x] **CHK022**: Are the validation rules for all input fields (e.g., max length for tag names, URL format for websites) documented in the requirements? [Clarity, Gap]
- [x] **CHK023**: Is the structure of the JSON object for starting a new run (`POST /api/runs`) explicitly defined in the requirements? [Clarity, contracts/openapi.yaml]

## Requirement Consistency

- [x] **CHK024**: Are field names and data types consistent across all API endpoints and the data model (e.g., is `entity_id` always an integer)? [Consistency, contracts/openapi.yaml, data-model.md]
- [x] **CHK025**: Is the error response format consistent for all endpoints when a request fails? [Consistency, Gap]
- [x] **CHK026**: Do the API contracts in `openapi.yaml` align with the functional requirements in `spec.md` without discrepancies? [Consistency]

## Scenario & Edge Case Coverage

- [x] **CHK027**: Are requirements defined for how the API should handle a request to undo a run when no runs have been executed yet? [Edge Case, spec.md §FR-009]
- [x] **CHK028**: Does the spec define the API's behavior when a user tries to create a tag that already exists (e.g., return a 409 Conflict)? [Edge Case, spec.md §FR-016]
- [x] **CHK029**: Are requirements for pagination specified for list endpoints (`/api/entities`, `/api/runs`) to handle potentially large datasets? [Coverage, Gap]
- [x] **CHK030**: Is the expected API behavior defined for when a user tries to update a non-existent entity (`PUT /api/entities/{id}`)? [Edge Case]

## Non-Functional Requirements

- [x] **CHK031**: Are performance targets (e.g., max response time) specified for the `GET /api/entities` endpoint, especially with multiple filters applied? [Clarity, spec.md §SC-004]
- [x] **CHK032**: Are requirements for rate limiting external API calls (i.e., to the Gemini API) documented to prevent excessive usage and cost? [Gap]
- [x] **CHK033**: Is a versioning strategy for the internal API defined in the requirements to support future frontend and backend changes? [Gap]

---
### Extended Items (2025-10-17)

- [x] **CHK052**: Are the API requirements for reporting the status of a background run (initiated by `POST /api/runs`) defined, including how a client can check for completion or failure? [Completeness, tasks.md:T021]
