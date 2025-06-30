# System Health Dashboard

This is a simple web application to display the health status of various systems.
It provides a dashboard view in a browser, showing one row per health item with icons,
status messages, last update times, and links for more details.

States are updated via a REST API.

## Features

-   Real-time (polling) health status display for multiple systems.
-   Visual status indicators (icons).
-   Timestamp for the last update of each system's status.
-   Optional detailed messages and investigation links.
-   REST API for querying and updating health statuses.

## Project Structure

```
health_dashboard/
├── app.py             # Flask application (backend API and serving frontend)
├── templates/
│   └── index.html     # Main HTML page for the dashboard
├── static/
│   ├── script.js      # Frontend JavaScript for API interaction and DOM manipulation
│   └── style.css      # CSS for styling the dashboard
└── README.md          # This file
```

## Setup and Running

1.  **Prerequisites:**
    *   Python 3.x
    *   Flask (`pip install Flask`)

2.  **Run the Application:**
    Navigate to the `health_dashboard` directory and run:
    ```bash
    python app.py
    ```
    The application will be accessible at `http://127.0.0.1:5000` (or `http://0.0.0.0:5000` if your firewall is configured).

## API Endpoints

### Get All Health Statuses

-   **URL:** `/api/health`
-   **Method:** `GET`
-   **Success Response:**
    -   **Code:** 200 OK
    -   **Content:**
        ```json
        {
          "builds": {"status": "passing", "last_updated": "2023-10-27T10:30:00Z", "message": "All builds green.", "url": "http://jenkins.example.com/builds"},
          "tests": {"status": "failing", "last_updated": "2023-10-27T10:35:00Z", "message": "UI tests failing.", "url": "http://jenkins.example.com/tests"},
          "host_activity": {"status": "running", "last_updated": "2023-10-27T10:36:00Z", "message": "", "url": ""},
          "host_up_down": {"status": "unknown", "last_updated": null, "message": "", "url": ""},
          "operational_system": {"status": "unknown", "last_updated": null, "message": "", "url": ""}
        }
        ```

### Update System Health Status

-   **URL:** `/api/health/<system_name>`
    -   Example: `/api/health/builds`
-   **Method:** `POST`
-   **Headers:** `Content-Type: application/json`
-   **Body (JSON):**
    ```json
    {
      "status": "failing",                            // Required. Valid: "running", "down", "passing", "failing", "unknown"
      "message": "Specific build #123 failed",        // Optional
      "url": "http://jenkins.example.com/build/123"   // Optional
    }
    ```
-   **Success Response:**
    -   **Code:** 200 OK
    -   **Content:**
        ```json
        {
          "builds": {"status": "failing", "last_updated": "2023-10-27T10:40:00Z", "message": "Specific build #123 failed", "url": "http://jenkins.example.com/build/123"}
        }
        ```
-   **Error Responses:**
    -   `400 Bad Request`: Invalid JSON payload or invalid status value.
    -   `404 Not Found`: System name not found.

## Frontend

-   The frontend is served by Flask from `templates/index.html`.
-   JavaScript (`static/script.js`) fetches data from `/api/health` every 30 seconds and updates the table.
-   CSS (`static/style.css`) provides basic styling for the dashboard and status icons.

## Initial System States

The application initializes with the following systems in an "unknown" state:
- builds
- tests
- host_activity
- host_up_down
- operational_system

These can be updated via the POST API endpoint.
