# Quickstart: JobCrawl MVP

This guide provides instructions for setting up and running the JobCrawl application.

## Prerequisites

-   Python 3.11+
-   An environment manager (like `venv` or `conda`)
-   Node.js and `npm` (for the frontend)

## Setup

### 1. Backend (Python)

**Recommended: `mamba`**

```bash
# Create and activate the environment from the project root
mamba env update --file environment.yml --prune

# Activate the environment
mamba activate jobcrawl
```

**Fallback: `conda`**

```bash
# Create and activate the environment from the project root
conda env update --file environment.yml --prune

# Activate the environment
conda activate jobcrawl
```

### 2. Frontend (React)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

### 3. API Key

The application uses the Google Gemini API for its agentic capabilities.

1.  Obtain an API key from Google AI Studio.
2.  Create a `.env` file in the project root (by copying `.env.example`) and add your key:

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    The application will load this variable automatically.

## Running the Application

1.  **Start the Backend Server:**

    ```bash
    # Make sure the 'jobcrawl' conda environment is activated
    # From the project root directory
    uvicorn backend.src.main:app --reload
    ```

2.  **Start the Frontend Development Server:**

    ```bash
    # From the frontend directory
    npm start
    ```

3.  Open your web browser and navigate to `http://localhost:3000` (or the address provided by the frontend server).

## Usage Walkthrough

1.  **Create Tags**: Navigate to the "Tag Manager" and create a few thematic tags (e.g., "Robotics", "AI for Science").
2.  **Configure a Run**: Go to the "Run Panel", select the tags you just created, and choose one or more cities to explore.
3.  **Start a Run**: Click "Start Discovery" to trigger the agent. You can monitor its progress in the run history.
4.  **Explore Results**: Once the run is complete, go to the main "Browse" view to see the discovered entities.
5.  **Filter and Edit**: Use the filters to narrow down the results. Click on an entity to view its details and make edits.
6.  **Undo**: If you are not satisfied with the results of the last run, you can undo it from the "Run Panel".
