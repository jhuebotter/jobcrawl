# Feature Specification: JobCrawl MVP

**Feature Branch**: `001-jobcrawl-mvp-spec`
**Created**: 2025-10-16
**Status**: Draft
**Input**: User description: "We are building the full MVP of an application called **JobCrawl**. It is a single-user, local-first web application with a reactive interface and an agentic backend..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure and Run a Discovery Agent (Priority: P1)

As a researcher, I want to define thematic tags, select cities and institution types, and trigger a discovery run so that I can populate my local database with relevant professional entities.

**Why this priority**: This is the core data-gathering functionality of the application. Without it, there is no data to explore.

**Independent Test**: Can be tested by configuring a run with at least one tag and one city, executing it, and verifying that new entities are added to the database.

**Acceptance Scenarios**:

1.  **Given** I have defined a tag "AI for Science" and selected the city "Zurich", **When** I trigger a discovery run, **Then** the system should perform a search and add new entities related to "AI for Science" in "Zurich" to the local database.
2.  **Given** a discovery run is in progress, **When** I view the run manager, **Then** I should see the status of the current run.

### User Story 2 - Explore and Filter Discovered Entities (Priority: P2)

As a researcher, I want to browse the collected entities, filter them by tags, city, and type, and view detailed information for each entity so that I can efficiently analyze the results.

**Why this priority**: This functionality allows the user to derive value from the collected data.

**Independent Test**: Can be tested by loading a pre-populated database, applying filters, and verifying that the displayed results are correct.

**Acceptance Scenarios**:

1.  **Given** my database contains entities from "Zurich" and "Berlin", **When** I filter by "Berlin", **Then** only entities from "Berlin" should be displayed.
2.  **Given** I am viewing a list of entities, **When** I click on an entity, **Then** I should be taken to a detail view showing all its metadata.

### User Story 3 - Curate and Manage Data (Priority: P3)

As a researcher, I want to edit entity details, add notes, manage duplicates, star favorites, and undo the last discovery run so that I can maintain the quality and organization of my data.

**Why this priority**: Data curation is essential for long-term use and accuracy.

**Independent Test**: Can be tested by performing each curation action (edit, star, undo) and verifying the database state reflects the change.

**Acceptance Scenarios**:

1.  **Given** I am viewing an entity's details, **When** I edit its summary and save, **Then** the new summary should be persisted.
2.  **Given** I have just completed a discovery run, **When** I click "Undo Last Run", **Then** all entities added by that run should be removed from the database.

### User Story 4 - Manually Add and Autocomplete Entities (Priority: P2)

As a researcher, I want to manually add a new entity by providing minimal information (like a name or website), and have the agent automatically research it, fill in the details, and check for duplicates, so I can easily add entities I already know about.

**Why this priority**: This gives the user control to seed the database with known entities and ensures important targets are not missed by automated discovery alone.

**Independent Test**: Can be tested by providing a name of a known entity, triggering the feature, and verifying that a complete, non-duplicate entity is created.

**Acceptance Scenarios**:

1.  **Given** I provide the name of a known research lab, **When** I trigger the "add and autocomplete" function, **Then** the system should create a new, fully populated entity entry for that lab.
2.  **Given** I provide the URL of a startup's website, **When** I trigger the "add and autocomplete" function, **Then** the system should create a corresponding entity with details extracted from the site.
3.  **Given** I try to add an entity that already exists, **When** the agent autocompletes it, **Then** it should flag it as a duplicate and prompt me to review or merge.

### Edge Cases

-   What happens when a discovery run finds no results for a given tag/city pair?
-   How does the system handle network errors when calling the Gemini API?
-   What happens if the user tries to undo a run that has already been undone?
-   What happens if the agent cannot find any information for a manually added entity?

## Requirements *(mandatory)*

### Functional Requirements

#### Agentic Discovery
-   **FR-001**: The system MUST allow users to define thematic tags with descriptions.
-   **FR-002**: The system MUST allow users to select one or more cities or regions for discovery.
-   **FR-003**: The system MUST allow users to filter discovery runs by institution type (Academic, Research Institutes, Industry, NGOs, Government/Agencies).
-   **FR-004**: The system MUST perform sequential, targeted searches for each (city × tag) combination.
-   **FR-005**: The system MUST extract structured entities including name, kind, website, summary, city, country, and a source URL.
-   **FR-006**: The system MUST deduplicate results against the local database before insertion.
-   **FR-007**: The system MUST log each discovery run with its parameters, timestamps, and a summary of changes.
-   **FR-008**: The run log MUST clearly indicate the outcome for each (city × tag) pair, stating either the number of new entities found or "No new results found". This reporting MUST NOT interrupt the execution of a larger run.
-   **FR-009**: The system MUST provide a function to undo the last discovery run.
-   **FR-010**: The system MUST automatically enrich existing entries with new, non-conflicting information from potential duplicates. If conflicting data is found or if the confidence of the duplicate match is moderate, the pair MUST be flagged for manual user review.

#### Data Management
-   **FR-011**: The system MUST store all data in a local database.
-   **FR-012**: The database MUST support storing entities, tags, sources, runs, and user edits.
-   **FR-013**: When a person is discovered, they MUST be added to a separate `People` table and linked to the parent entity. If the confidence of this association is moderate or low, the link MUST be flagged for user review.

#### Web Interface
-   **FR-014**: The interface MUST allow browsing and filtering of entities by tag, city, type, and starred status.
-   **FR-015**: The interface MUST provide a detail view for each entity, showing all its metadata.
-   **FR-016**: The interface MUST allow users to manage tags (add, edit, remove).
-   **FR-017**: The interface MUST provide a run manager to configure and trigger discovery runs.
-   **FR-018**: The interface MUST allow users to export the current view of entities as CSV or JSON.

#### Data Editing and User Interaction
-   **FR-019**: Users MUST be able to perform inline edits on entity fields.
-   **FR-020**: Users MUST be able to add notes to any entity.
-   **FR-021**: Users MUST be able to star/unstar entities as favorites.
-   **FR-022**: All user edits MUST be logged for traceability. Each change MUST be recorded with a timestamp, the field that was changed, and its old and new values.
-   **FR-023**: The system MUST provide a function for users to manually initiate the creation of a new entity.
-   **FR-024**: When a user provides minimal information for a new entity (e.g., name or website), the system MUST trigger an agentic process to research and populate the remaining fields.
-   **FR-025**: The agentic process for manual additions MUST reuse the same discovery, deduplication, and enrichment logic as the main discovery runs.
-   **FR-026**: After autocompleting a manually added entity, the system MUST check for duplicates against the existing database and prompt the user for review if a potential match is found.
-   **FR-027**: The `updated_at` timestamp of an `Entity` MUST be updated when a related object (e.g., a `Tag` or `Person`) is added or removed.
-   **FR-028**: The "Undo Last Run" feature MUST be implemented by deleting all `entities`, `people`, and `sources` that are associated with the `run_id` of the last completed run.
-   **FR-029**: If a user attempts to create a `Tag` that already exists (case-insensitive), the API MUST return a `400 Bad Request` error.
-   **FR-030**: If a user attempts to update an `Entity` that does not exist, the API MUST return a `404 Not Found` error.
-   **FR-031**: If a user attempts to undo a run when no runs have been completed, the API MUST return a `404 Not Found` error.

### Key Entities *(include if feature involves data)*

-   **Entity**: Represents an organization, lab, or company. Attributes include name, kind, summary, website, location, confidence, and timestamps.
-   **Tag**: A user-defined thematic label with a description.
-   **Person**: An individual associated with an entity. Stored in a separate table and linked to an Entity. Attributes MUST include Name, Role/Title, and Source URL.
-   **Source**: The origin of an entity's data (URL and retrieval timestamp).
-   **Run**: Metadata for a discovery run, including parameters and results.
-   **EditLog**: A record of manual edits and reversions.

## Constraints

-   **C-001**: The system MUST use a local, file-based SQL database (e.g., SQLite) for all data storage.
-   **C-002**: The application MUST be compatible with macOS, Linux, and Windows.
-   **C-003**: The system MUST operate locally with no cloud dependencies, apart from the required calls to the Gemini API for data processing.
-   **C-004**: For the MVP, direct user edits are limited to the `entities` table.
-   **C-005**: A person-entity link is considered 'moderate or low' confidence if the confidence score provided by the agent is less than 0.75.
-   **C-006**: Tag names must be between 1 and 50 characters.

## Clarifications

### Session 2025-10-16
- Q: What are the essential attributes for a `Person` entity? → A: Name, Role/Title, Source URL
- Q: What should the system do when a discovery run for a specific (city x tag) pair finds zero *new* entities? → A: The run log MUST clearly indicate the outcome for each pair, stating either the number of new entities found or "No new results found". This reporting MUST NOT interrupt a larger run.
- Q: How should manual edits be logged for traceability? → A: Each change MUST be recorded with a timestamp, the field that was changed, and its old and new values.
- Q: Should the "AI-assisted manual entry" feature be included in the scope of the MVP? → A: Yes, this is a core requirement. The agent should assist in completing manually added entries by reusing the main discovery and deduplication logic.
- Q: What is the required data storage mechanism? → A: A local, file-based SQL database (like SQLite).

## Success Criteria *(mandatory)*

### Measurable Outcomes

-   **SC-001**: From at least two cities and three tags with all institution types selected, the system should produce at least 50 valid entities in one run.
-   **SC-002**: At least 95% of entities must include a name, website, and a valid source URL.
-   **SC-003**: No exact duplicates shall remain in the database after the deduplication process.
-   **SC-004**: Browsing and filtering of 500 entities in the local interface must complete in under 1 second.
-   **SC-005**: The "Undo Last Run" function must fully restore the database to its state before the run.
-   **SC-006**: In a single run, the agent MUST NOT add more than 20 new entities per (city x tag) combination. This is a maximum, and the agent should use its discretion to halt searching when it determines it has covered enough ground. There is no global cap for a run.