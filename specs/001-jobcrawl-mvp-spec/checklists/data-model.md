# Checklist: Data Model Requirements Quality

**Purpose**: To validate the completeness, clarity, and consistency of the data model requirements before task breakdown.
**Created**: 2025-10-16
**Feature**: `specs/001-jobcrawl-mvp-spec/spec.md`

---

## Requirement Completeness

- [ ] **CHK001**: Are all required fields explicitly marked as `NOT NULL` or otherwise noted as mandatory in the data model? [Completeness, data-model.md]
- [ ] **CHK002**: Is the enumerated list of possible values for `entities.kind` and `people.review_status` documented? [Gap]
- [ ] **CHK003**: Are cascade deletion behaviors defined for all foreign key relationships (e.g., what happens to `people` or `entity_tags` when an `entity` is deleted)? [Gap]
- [ ] **CHK004**: Does the `runs` table schema include a field to store a summary of results (e.g., number of new entities found)? [Completeness, data-model.md §runs]

## Requirement Clarity

- [ ] **CHK005**: Is the valid format for `website` and `source_url` fields specified (e.g., must include `http://` or `https://`)? [Clarity, data-model.md]
- [ ] **CHK006**: Is the range and meaning of the `entities.confidence` score (e.g., 0.0 to 1.0) explicitly defined? [Clarity, data-model.md §entities]
- [ ] **CHK007**: Are the specific fields and criteria for entity deduplication documented? [Clarity, spec.md §FR-006]
- [ ] **CHK008**: Is the structure of the `runs.parameters` JSON object specified? [Clarity, data-model.md §runs]
- [ ] **CHK009**: Are the requirements for string normalization (e.g., case, whitespace) before database insertion defined? [Gap]

## Requirement Consistency

- [ ] **CHK010**: Is the requirement for logging edits (`edit_logs`) consistently applicable to all user-editable fields across all tables? [Consistency, spec.md §FR-022]
- [ ] **CHK011**: Do the foreign key relationships in `data-model.md` correctly reflect the one-to-many and many-to-many relationships described in the spec? [Consistency]
- [ ] **CHK012**: Is the `updated_at` timestamp requirement on the `entities` table consistently applied after any related data changes (e.g., adding a tag or person)? [Consistency, Gap]

## Acceptance Criteria Quality

- [ ] **CHK013**: Are the requirements for the "Undo last run" feature sufficiently detailed to be testable and guarantee a clean rollback? [Measurability, spec.md §FR-009]
- [ ] **CHK014**: Can the automatic merge logic for duplicates be objectively tested based on the current requirements? [Measurability, spec.md §FR-010]
- [ ] **CHK015**: Is the process for flagging a `person` for review based on confidence scores clearly defined and measurable? [Measurability, spec.md §FR-013]
