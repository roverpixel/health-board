document.addEventListener('DOMContentLoaded', function() {
    const healthTableBody = document.getElementById('health-table').getElementsByTagName('tbody')[0];
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    let statusConfig = {};

    // Dark Mode Logic
    const darkModeKey = 'darkMode';

    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function toggleDarkMode() {
        const body = document.body;
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        setCookie(darkModeKey, isDarkMode, 365);
    }

    // Check cookie on load
    const savedDarkMode = getCookie(darkModeKey);
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    /**
     * Fetches the status configuration from the API.
     */
    function fetchStatusConfig() {
        return fetch('/api/status-config')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error fetching status config:', error);
                return {}; // Return empty object on error
            });
    }

    /**
     * Fetches health data from the API and triggers table update.
     */
    function fetchHealthData() {
        fetch('/api/health')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                updateTable(data);
            })
            .catch(error => {
                console.error('Error fetching health data:', error);
                healthTableBody.innerHTML = '<tr><td colspan="6" class="no-data">Error loading data. Check console.</td></tr>';
            });
    }

    /**
     * Updates the HTML table with the provided health data.
     * @param {object} data - The health status data from the API.
     *                         Example: {"CategoryName": {"ItemName": {"status": "...", ...}}}
     */
    function updateTable(data) {
        healthTableBody.innerHTML = ''; // Clear existing rows

        if (Object.keys(data).length === 0) {
            healthTableBody.innerHTML = '<tr><td colspan="6" class="no-data">No health data available.</td></tr>';
            return;
        }

        let isFirstItemInCategory = true;

        for (const categoryName in data) {
            if (data.hasOwnProperty(categoryName)) {
                const items = data[categoryName];
                isFirstItemInCategory = true; // Reset for each new category

                if (Object.keys(items).length === 0) { // Display category even if it has no items yet
                    const row = healthTableBody.insertRow();
                    const categoryCell = row.insertCell();
                    categoryCell.textContent = categoryName;
                    categoryCell.className = 'category-cell';
                    row.insertCell().colSpan = 5; // Empty cells for the rest of the row
                } else {
                    for (const itemName in items) {
                        if (items.hasOwnProperty(itemName)) {
                            const item = items[itemName];
                            const row = healthTableBody.insertRow();

                            // Category Cell
                            const categoryCell = row.insertCell();
                            if (isFirstItemInCategory) {
                                categoryCell.textContent = categoryName;
                                categoryCell.className = 'category-cell';
                                isFirstItemInCategory = false;
                            } else {
                                categoryCell.textContent = ''; // Or '〃' or some ditto mark
                            }

                            // Item Name Cell
                            const itemCell = row.insertCell();
                            itemCell.textContent = itemName;

                            // Status Cell (Icon + Text)
                            const statusCell = row.insertCell();
                            const statusIcon = document.createElement('span');
                            const currentStatus = item.status ? item.status.toLowerCase() : 'unknown';

                            // Dynamically set class and style based on fetched config
                            const config = statusConfig[currentStatus] || statusConfig['unknown'];
                            let iconClass = 'status-icon';
                            if (config) {
                                iconClass += ` status-${config.color}`;
                                if (config.pulse) {
                                    iconClass += ' status-pulse';
                                }
                            } else {
                                iconClass += ' status-unknown'; // Fallback
                            }
                            statusIcon.className = iconClass;

                            statusCell.appendChild(statusIcon);
                            const statusText = item.status ? item.status.charAt(0).toUpperCase() + item.status.slice(1) : 'Unknown';
                            statusCell.appendChild(document.createTextNode(statusText));

                            // Last Updated Cell
                            const lastUpdatedCell = row.insertCell();
                            lastUpdatedCell.textContent = item.last_updated ? new Date(item.last_updated).toLocaleString() : 'N/A';

                            // Message Cell
                            const messageCell = row.insertCell();
                            messageCell.textContent = item.message || 'N/A';

                            // Link Cell
                            const linkCell = row.insertCell();
                            if (item.url) {
                                const link = document.createElement('a');
                                link.href = item.url;
                                link.textContent = 'Investigate';
                                link.target = '_blank';
                                link.rel = 'noopener noreferrer';
                                linkCell.appendChild(link);
                            } else {
                                linkCell.textContent = 'N/A';
                            }
                        }
                    }
                }
            }
        }
    }

    /**
     * Initializes the application by fetching configuration and then starting the data polling.
     */
    function initialize() {
        fetchStatusConfig().then(config => {
            statusConfig = config;
            fetchHealthData(); // Initial fetch
            setInterval(fetchHealthData, 30000); // Poll every 30 seconds
        });
    }

    initialize();
});
