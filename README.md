# System Health Dashboard (Hierarchical)

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

## Project Structure

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
      "Host Up/Down": {
        "mars": {"status": "down", "last_updated": "...", "message": "...", "url": "..."}
      }
    }
    ```

### Categories

#### Create Category
-   **URL:** `/categories`
-   **Method:** `POST`
-   **Headers:** `Content-Type: application/json`
-   **Body:** `{"category_name": "New Category Name"}`
-   **Success Response (201 Created):** `{"New Category Name": {}}`
-   **Error Response (400 Bad Request):** If category exists or invalid payload.

#### Delete Category
-   **URL:** `/categories/<category_name>`
    -   Example: `/categories/Builds` (Note: URL encode spaces or special characters, e.g., `Host%20Up%2FDown`)
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
