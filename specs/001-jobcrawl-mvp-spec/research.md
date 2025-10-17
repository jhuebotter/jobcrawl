# Research: JobCrawl MVP

This document outlines the research required to finalize the technical stack for the JobCrawl MVP.

## 1. Backend API Framework

**Task**: Research and select a Python web framework for serving the local UI and API.

**Context**: The framework needs to be lightweight, fast, and easy to set up for a local-first desktop application. It will serve a simple REST-like API for the frontend to interact with the agentic backend and database.

**Options**:
-   **FastAPI**: Modern, high-performance framework with automatic OpenAPI documentation. Good for building robust APIs.
-   **Flask**: A mature, lightweight, and highly extensible micro-framework. Very simple to get started with.
-   **Tornado**: Asynchronous networking library and web framework, suitable for long-lived network connections if the agent runs require them.

**Decision Criteria**:
-   Ease of setup for a local application.
-   Performance for a single-user workload.
-   Quality of documentation and community support.

## 2. Agent Orchestration

**Task**: Research and select a library or design a custom framework for managing sequential agent tasks.

**Context**: The core of the application is an agent that performs a sequence of tasks (search, extract, deduplicate, enrich) for each (city x tag) pair. This workflow needs to be robust, observable, and pausable/resumable if possible.

**Options**:
-   **Custom Implementation**: A simple, custom loop that iterates through the search pairs and executes the agent tasks sequentially. State can be managed in the database.
-   **Task Queue Library (e.g., Celery, Dramatiq)**: While typically used for distributed systems, a lightweight configuration could manage the task sequence. This might be overkill for a local application.
-   **Orchestration Framework (e.g., LangChain, LlamaIndex)**: These frameworks provide high-level abstractions for building agentic workflows. They may offer useful components but could also introduce unnecessary complexity.

**Decision Criteria**:
-   Simplicity and maintainability.
-   Ability to log and track the state of each run.
-   Avoidance of heavy dependencies not suited for a local application.

## 3. Frontend Framework

**Task**: Research and select a reactive web framework for the user interface.

**Context**: The UI needs to be a reactive, single-page application that can efficiently display and filter data from the local database. It will be served by the Python backend.

**Options**:
-   **React**: A mature and widely-used library with a vast ecosystem of tools and components.
-   **Vue**: A progressive framework known for its gentle learning curve and excellent documentation.
-   **Svelte**: A compiler-based approach that results in highly efficient, vanilla JavaScript at runtime.

**Decision Criteria**:
-   Ease of integration with a Python backend.
-   Performance for rendering and filtering lists of data.
-   Developer experience and build toolchain simplicity.
