# Quickstart: JobCrawl MVP

This guide provides instructions for setting up and running the JobCrawl application.

## Prerequisites

-   Python 3.11+
-   An environment manager (like `venv` or `conda`)
-   Node.js and `npm` (for the frontend)

## Setup

### 1. Backend (Python)

**Using `venv`:**

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Using `conda`:**

```bash
# Navigate to the backend directory
cd backend

# Create a conda environment
conda create --name jobcrawl python=3.11
conda activate jobcrawl

# Install dependencies
pip install -r requirements.txt
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
2.  Set it as an environment variable:

    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```

    If this variable is not set, the application will prompt you to enter it on the first run.

## Running the Application

1.  **Start the Backend Server:**

    ```bash
    # From the backend directory
    uvicorn src.main:app --reload
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
