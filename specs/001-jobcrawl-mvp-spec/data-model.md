# Data Model: JobCrawl MVP

This document defines the database schema for the JobCrawl application, based on the entities identified in the feature specification. The schema is designed for a local SQLite database.

---

### Table: `entities`

Stores the primary records of discovered organizations, labs, companies, etc.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the entity. |
| `name` | TEXT | NOT NULL | The name of the organization. |
| `kind` | TEXT | | The type of entity (e.g., "Academic", "Industry", "Research Institute", "NGO", "Government"). |
| `summary` | TEXT | | A brief description of the entity. |
| `website` | TEXT | | The primary URL for the entity. Must be a valid URL including the protocol. |
| `city` | TEXT | | The city where the entity is located. |
| `country` | TEXT | | The country where the entity is located. |
| `confidence` | REAL | | A score from 0.0 to 1.0 representing the agent's confidence in the accuracy of the data. |
| `created_at` | TEXT | NOT NULL | Timestamp of initial creation (ISO 8601). |
| `updated_at` | TEXT | NOT NULL | Timestamp of last update (ISO 8601). |
| `run_id` | INTEGER | FOREIGN KEY (`runs.id`) | The ID of the run that created this entity. |

---

### Table: `tags`

Stores user-defined thematic tags.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the tag. |
| `name` | TEXT | NOT NULL, UNIQUE | The name of the tag. |
| `description` | TEXT | | A short description of the tag's meaning. |

---

### Table: `entity_tags`

A many-to-many join table linking entities and tags.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `entity_id` | INTEGER | FOREIGN KEY (`entities.id`) ON DELETE CASCADE | Foreign key to the `entities` table. |
| `tag_id` | INTEGER | FOREIGN KEY (`tags.id`) | Foreign key to the `tags` table. |
| | | PRIMARY KEY (`entity_id`, `tag_id`) | |

---

### Table: `people`

Stores information about individuals associated with entities.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the person. |
| `entity_id` | INTEGER | FOREIGN KEY (`entities.id`) ON DELETE CASCADE | Foreign key to the parent entity. |
| `name` | TEXT | NOT NULL | The person's full name. |
| `role` | TEXT | | The person's role or title. |
| `source_url` | TEXT | | The URL where the person's information was found. Must be a valid URL including the protocol. |
| `review_status` | TEXT | | Flag for associations with moderate/low confidence. Possible values: 'needs_review', 'confirmed'. |
| `run_id` | INTEGER | FOREIGN KEY (`runs.id`) | The ID of the run that created this person record. |

---

### Table: `sources`

Stores provenance information for each piece of data.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the source. |
| `entity_id` | INTEGER | FOREIGN KEY (`entities.id`) ON DELETE CASCADE | The entity this source applies to. |
| `url` | TEXT | NOT NULL | The source URL. |
| `retrieved_at` | TEXT | NOT NULL | Timestamp of data retrieval (ISO 8601). |
| `run_id` | INTEGER | FOREIGN KEY (`runs.id`) | The ID of the run that created this source record. |

---

### Table: `runs`

Logs metadata for each discovery run.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the run. |
| `started_at` | TEXT | NOT NULL | Timestamp when the run began (ISO 8601). |
| `finished_at` | TEXT | | Timestamp when the run completed (ISO 8601). |
| `parameters` | TEXT | | JSON object of the run parameters (e.g., `{"tags": ["AI", "Robotics"], "cities": ["Zurich", "Berlin"]}`). |
| `status` | TEXT | | The current status of the run ('in_progress', 'completed', 'failed'). |
| `results_summary` | TEXT | | JSON object of the run's outcomes (e.g., number of new entities found). |

---

### Table: `edit_logs`

Records all manual edits to entities for traceability.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for the log entry. |
| `entity_id` | INTEGER | FOREIGN KEY (`entities.id`) ON DELETE CASCADE | The entity that was edited. |
| `field_name` | TEXT | NOT NULL | The name of the field that was changed. |
| `old_value` | TEXT | | The value of the field before the change. |
| `new_value` | TEXT | | The value of the field after the change. |
| `timestamp` | TEXT | NOT NULL | Timestamp of the edit (ISO 8601). |

---

### Table: `starred`

Tracks entities that the user has marked as favorites.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `entity_id` | INTEGER | PRIMARY KEY, FOREIGN KEY (`entities.id`) ON DELETE CASCADE | The entity that is starred. |
