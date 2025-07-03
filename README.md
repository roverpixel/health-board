[![Python application](https://github.com/roverpixel/health-board/actions/workflows/python-app.yml/badge.svg)](https://github.com/roverpixel/health-board/actions/workflows/python-app.yml)

# System Health Dashboard

This is a web application to display the health status of various systems, organized into categories and items.
It provides a dashboard view in a browser, showing one row per item with its category, status icons,
status messages, last update times, and links for more details.

States are managed via a REST API, allowing for dynamic creation and deletion of categories and items,
as well as updates to item statuses.

## Features

-   Hierarchical health status display: items grouped under categories.
-   Real-time (polling) health status display.
-   Visual status indicators (icons) for each item.
-   Timestamp for the last update of each item's status.
-   Optional detailed messages and investigation links for each item.
-   REST API for:
    -   Querying all health data.
    -   Creating and deleting categories.
    -   Creating, deleting, and updating items within categories.
    - Checkpointing current state to a file.
    - Restoring state from a checkpoint file.

## CLI Client (`health_board.py`)

A command-line client, `health_board.py`, is provided for interacting with the Health Dashboard API.

### CLI Setup

1.  **Prerequisites:**
    *   Python 3.x
    *   `click` library: `pip install click`
    *   `requests` library: `pip install requests`

2.  **Make the client executable:**
    ```bash
    chmod +x health_board.py
    ```
    This allows you to run it directly (e.g., `./health_board.py ...`). You can also run it with `python health_board.py ...`.

### CLI Usage

The primary way to run the client after making it executable is `./health_board.py`.

**General Help:**
```bash
./health_board.py --help
```

**Commands:**

*   **`show`**: Display the current board data.
    ```bash
    ./health_board.py show
    ```

*   **`create category <category_name>`**: Create a new category.
    ```bash
    ./health_board.py create category "Deployment Pipelines"
    ```

*   **`create item <category_name> <item_name>`**: Create a new item within a category.
    ```bash
    ./health_board.py create item "Deployment Pipelines" "Production Deploy"
    ```

*   **`update item <category_name> <item_name> [OPTIONS]`**: Update an item's status, message, or URL.
    *   `--status TEXT`: New status (e.g., running, down, passing, failing, unknown, up).
    *   `--message TEXT`: Descriptive message.
    *   `--url TEXT`: Related URL.
    ```bash
    ./health_board.py update item "Deployment Pipelines" "Production Deploy" --status passing --message "v1.2.3 deployed successfully" --url "http://deploy.example.com/prod/123"
    ./health_board.py update item "Deployment Pipelines" "Production Deploy" --status failing
    ```

*   **`remove category <category_name>`**: Remove a category and all its items.
    ```bash
    ./health_board.py remove category "Deployment Pipelines"
    ```

*   **`remove item <category_name> <item_name>`**: Remove an item from a category.
    ```bash
    ./health_board.py remove item "Deployment Pipelines" "Production Deploy"
    ```

*   **`save`**: Save the current board data to `health_data.json`.
    ```bash
    ./health_board.py save
    ```

*   **`restore`**: Restore board data from `health_data.json`.
    ```bash
    ./health_board.py restore
    ```

---

## Web Application

### Project Structure

```
.
├── app.py                       # Flask application (backend API and serving frontend)
├── templates/
│   └── index.html               # Main HTML page for the dashboard
├── static/
│   ├── script.js                # Frontend JavaScript for API interaction and DOM manipulation
│   └── style.css                # CSS for styling the dashboard
├── setup_dashboard.sh           # Example script to initialize the dashboard structure
├── update_status_examples.sh    # Example script to update statuses of some items
└── README.md                    # This file
```

## Setup and Running

1.  **Prerequisites:**
    *   Python 3.x
    *   Flask (`pip install Flask`)
    *   `curl` (for running the example scripts)

2.  **Make Scripts Executable (Optional but Recommended):**
    ```bash
    chmod +x setup_dashboard.sh
    chmod +x update_status_examples.sh
    ```

3.  **Run the Application:**
    Navigate to the project directory and run:
    ```bash
    python app.py
    ```
    The application will be accessible at `http://localhost:5000`.

4.  **Initialize Dashboard (Optional - using example script):**
    In a separate terminal, while the app is running, execute:
    ```bash
    ./setup_dashboard.sh
    ```
    This will populate the dashboard with predefined categories and items in an "unknown" state.

5.  **Update Statuses (Optional - using example script):**
    After setup, you can update statuses:
    ```bash
    ./update_status_examples.sh
    ```

## API Endpoints

The base URL for the API is `http://localhost:5000/api`.

**Important Naming Conventions:**
-   Category names and Item names **must not** contain the forward slash character (`/`).
-   Spaces in names are generally acceptable (e.g., "Operational Systems", "Main Build") as they will be URL-encoded by clients like `curl`. However, for maximum simplicity and to avoid any potential issues with URL encoding across different tools or libraries, using underscores (`_`) or hyphens (`-`) instead of spaces is a good practice (e.g., `Operational_Systems`, `Main_Build`).

### Health Data

#### Get All Health Data
-   **URL:** `/health`
-   **Method:** `GET`
-   **Success Response (200 OK):**
    ```json
    {
      "Builds": {
        "Main Build": {"status": "passing", "last_updated": "...", "message": "...", "url": "..."}
      },
      "Hosts Online": {
        "mars": {"status": "down", "last_updated": "...", "message": "...", "url": "..."}
      }
    }
    ```

### Categories

#### Create Category
-   **URL:** `/categories`
-   **Method:** `POST`
-   **Headers:** `Content-Type: application/json`
-   **Body:** `{"category_name": "New Category Name"}` (See Naming Conventions, e.g., "New_Category" or "New Category")
-   **Success Response (201 Created):** `{"New Category Name": {}}`
-   **Error Response (400 Bad Request):** If category exists or invalid payload.

#### Delete Category
-   **URL:** `/categories/<category_name>`
    -   Example: `/categories/Builds`, `/categories/Hosts%20Online`
    -   (Note: URL encode spaces if present, e.g., `Operational%20Systems`)
-   **Method:** `DELETE`
-   **Success Response (200 OK):** `{"message": "Category '<category_name>' deleted successfully"}`
-   **Error Response (404 Not Found):** If category does not exist.

### Items (within Categories)

#### Create Item in Category
-   **URL:** `/categories/<category_name>/items`
-   **Method:** `POST`
-   **Headers:** `Content-Type: application/json`
-   **Body:** `{"item_name": "New Item Name"}`
    -   Item is created with "unknown" status and current timestamp.
-   **Success Response (201 Created):** `{"New Item Name": {"status": "unknown", "last_updated": "...", "message": "", "url": ""}}`
-   **Error Response (404 Not Found):** If category does not exist.
-   **Error Response (400 Bad Request):** If item already exists or invalid payload.

#### Update Item in Category
-   **URL:** `/categories/<category_name>/items/<item_name>`
    -   Example: `/categories/Builds/items/Main%20Build`
-   **Method:** `PUT`
-   **Headers:** `Content-Type: application/json`
-   **Body (provide fields to update):**
    ```json
    {
      "status": "passing",  // Valid: "running", "down", "passing", "failing", "unknown"
      "message": "Optional detailed message",
      "url": "Optional investigation URL"
    }
    ```
-   **Success Response (200 OK):** The updated item object.
-   **Error Response (404 Not Found):** If category or item does not exist.
-   **Error Response (400 Bad Request):** If invalid status or payload.

#### Delete Item from Category
-   **URL:** `/categories/<category_name>/items/<item_name>`
-   **Method:** `DELETE`
-   **Success Response (200 OK):** `{"message": "Item '<item_name>' from category '<category_name>' deleted successfully"}`
-   **Error Response (404 Not Found):** If category or item does not exist.

## Frontend

-   The frontend is served by Flask from `templates/index.html`.
-   JavaScript (`static/script.js`) fetches data from `/api/health` every 30 seconds and updates the table.
-   The table displays items grouped by category. The category name is shown for the first item in its group.
-   CSS (`static/style.css`) provides styling.

## Example Scripts

-   `setup_dashboard.sh`: Initializes a set of common categories and items.
-   `update_status_examples.sh`: Updates the statuses of some of the pre-initialized items to demonstrate different states.
Make sure these scripts are executable (`chmod +x *.sh`).

## Running Tests

This project includes unit tests for the API and simulation tests for the example shell scripts.

1.  **Navigate to the project root directory.**
2.  **Run the tests using the `unittest` module:**
    ```bash
    python -m unittest discover tests
    ```
    Or, to run a specific test file:
    ```bash
    python -m unittest tests.test_app
    python -m unittest tests.test_scripts
    ```

The tests are located in the `tests/` directory:
-   `tests/test_app.py`: Contains unit tests for the Flask API endpoints.
-   `tests/test_scripts.py`: Contains tests that simulate the execution of `setup_dashboard.sh` and `update_status_examples.sh` to verify their intended effect on the application state.
