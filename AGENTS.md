# AGENTS.md

This file contains instructions and context for AI agents working on this repository.

## Project Overview
This is a Flask-based System Health Dashboard that displays the status of various systems.
- **Backend:** `app/app.py` (Flask)
- **Frontend:** `app/templates/index.html`, `app/static/script.js`, `app/static/style.css`
- **Execution:** `export FLASK_APP=app/app.py && flask run`
- **Tests:** `python -m unittest discover tests`

## Working Guidelines

### 1. Deep Planning Mode
Before making any changes, you must enter a "Deep Planning Mode".
- **Understand Requirements:** Do not assume you understand the task. Ask clarifying questions until you are absolutely certain of the user's expectations.
- **Verify Assumptions:** Even if the task seems clear, ask for confirmation (e.g., "Do you want X to happen when Y?").
- **Plan Approval:** Create a plan using `set_plan` only **after** you have clarified all requirements and received user confirmation.

### 2. Verification & Testing
- **Always Verify:** After every file modification, verify the change (e.g., `read_file`, `list_files`).
- **Test First:** Run relevant tests before and after changes.
- **Frontend Verification:** For UI changes, use Playwright scripts to generate screenshots and verify them visually.
- **Pre-Commit:** Always run `pre_commit_instructions` before submitting.

## Feature Specifications

### Core Functionality
The application provides a dashboard view of system health, organized by **Categories** and **Items**.

*   **Data Model:**
    *   **Categories:** Named groups of items (e.g., "Builds", "Production").
    *   **Items:** Individual health checks within a category (e.g., "Main Build", "Database").
    *   **Item Properties:** `status` (e.g., passing, failing), `message` (description), `url` (link to logs/details), and `last_updated` (timestamp).
*   **API:** A REST API at `/api` allows for:
    *   `GET /health`: Retrieving the full board state.
    *   `POST /categories`, `DELETE /categories/<name>`: Managing categories.
    *   `POST`, `PUT`, `DELETE` on `/categories/<cat>/items/<item>`: Managing items.
    *   `POST /checkpoint`, `POST /restore`: Saving/loading state to/from disk (`health_data.json`).
*   **Clients:**
    *   `health_board.py`: Python CLI for interacting with the API.
    *   `health_board.sh`: Bash/Curl CLI for interacting with the API.
    *   `health_board_api.py`: Python library for programmatic API access.

### Frontend
*   **Polling:** The dashboard polls `/api/health` every 30 seconds to update the table.
*   **Dark Mode:** Supported via a CSS class on the `body`. State is persisted in a cookie (`darkMode`).
*   **"Last Updated" Column Coloring:**
    The timestamps are color-coded based on their age relative to the current time.
    *   **Logic:**
        *   **< 24 Hours:** Solid Green (Fresh).
        *   **>= 24 Hours:** Linear color interpolation between milestones:
            *   **24h:** Greyish Orange
            *   **48h:** Orange
            *   **72h:** Light Red
            *   **>= 96h:** Solid Red
    *   **Styling:** Timestamps older than **72 hours** (3 days) are *italicized*.
    *   **Dark Mode:** Distinct color palettes are used for Light and Dark modes. The colors update immediately when toggling Dark Mode.

    **Color Palettes (Approximate):**
    *   **Light Mode:**
        *   Fresh: `#28a745`
        *   24h: `#B89070`
        *   48h: `#FF8C00`
        *   72h: `#F08080`
        *   96h: `#DC3545`
    *   **Dark Mode:**
        *   Fresh: `#90EE90`
        *   24h: `#C0A080`
        *   48h: `#FFA500`
        *   72h: `#FF6060`
        *   96h: `#FF4040`
