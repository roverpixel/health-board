document.addEventListener('DOMContentLoaded', function() {
    const healthTableBody = document.getElementById('health-table').getElementsByTagName('tbody')[0];
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    let statusConfig = {};
    let lastFetchedData = {}; // Store last fetched data to re-render on dark mode toggle

    // Dark Mode Logic
    const darkModeKey = 'darkMode';

    // Color Configuration for Last Updated
    const dateColors = {
        light: {
            fresh: [40, 167, 69],   // #28a745 (Green)
            day1:  [184, 144, 112], // #B89070 (Greyish Orange)
            day2:  [255, 140, 0],   // #FF8C00 (Orange)
            day3:  [240, 128, 128], // #F08080 (Light Red)
            day4:  [220, 53, 69]    // #DC3545 (Red)
        },
        dark: {
            fresh: [144, 238, 144], // #90EE90 (Light Green)
            day1:  [192, 160, 128], // #C0A080 (Greyish Orange)
            day2:  [255, 165, 0],   // #FFA500 (Orange)
            day3:  [255, 96, 96],   // #FF6060 (Light Red)
            day4:  [255, 64, 64]    // #FF4040 (Red)
        }
    };

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
        // Re-render table to update timestamp colors
        updateTable(lastFetchedData);
    }

    // Check cookie on load
    const savedDarkMode = getCookie(darkModeKey);
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    function interpolate(start, end, factor) {
        const r = Math.round(start[0] + (end[0] - start[0]) * factor);
        const g = Math.round(start[1] + (end[1] - start[1]) * factor);
        const b = Math.round(start[2] + (end[2] - start[2]) * factor);
        return `rgb(${r}, ${g}, ${b})`;
    }

    function getDateColor(hours, isDark) {
        const palette = isDark ? dateColors.dark : dateColors.light;

        if (hours < 24) return `rgb(${palette.fresh.join(',')})`;

        if (hours >= 96) return `rgb(${palette.day4.join(',')})`;

        // 24h to 96h interpolation
        let start, end, factor;
        if (hours < 48) {
            start = palette.day1;
            end = palette.day2;
            factor = (hours - 24) / 24;
        } else if (hours < 72) {
            start = palette.day2;
            end = palette.day3;
            factor = (hours - 48) / 24;
        } else { // 72 to 96
            start = palette.day3;
            end = palette.day4;
            factor = (hours - 72) / 24;
        }
        return interpolate(start, end, factor);
    }

    /**
     * Fetches the status configuration from the API.
     */
    function fetchStatusConfig() {
        return fetch('api/status-config')
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
        fetch('api/health')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                lastFetchedData = data;
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

        const isDarkMode = document.body.classList.contains('dark-mode');
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
                            if (item.last_updated) {
                                const date = new Date(item.last_updated);
                                lastUpdatedCell.textContent = date.toLocaleString();

                                // Calculate age in hours
                                const now = new Date();
                                const diffMs = now - date;
                                const diffHours = diffMs / (1000 * 60 * 60);

                                // Apply color logic
                                lastUpdatedCell.style.color = getDateColor(diffHours, isDarkMode);

                                // Apply italic if older than 3 days (72 hours)
                                if (diffHours >= 72) {
                                    lastUpdatedCell.style.fontStyle = 'italic';
                                }
                            } else {
                                lastUpdatedCell.textContent = 'N/A';
                            }

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
