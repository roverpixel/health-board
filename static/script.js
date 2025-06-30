document.addEventListener('DOMContentLoaded', function() {
    const healthTableBody = document.getElementById('health-table').getElementsByTagName('tbody')[0];

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
            .catch(error => console.error('Error fetching health data:', error));
    }

    /**
     * Updates the HTML table with the provided health data.
     * @param {object} data - The health status data from the API.
     */
    function updateTable(data) {
        healthTableBody.innerHTML = ''; // Clear existing rows to prevent duplication

        for (const systemName in data) {
            if (data.hasOwnProperty(systemName)) {
                const system = data[systemName];
                const row = healthTableBody.insertRow();

                // System Name Cell
                const nameCell = row.insertCell();
                // Format systemName: replace underscores with spaces and capitalize words
                nameCell.textContent = systemName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                // Status Cell (Icon + Text)
                const statusCell = row.insertCell();
                const statusIcon = document.createElement('span');
                statusIcon.className = `status-icon status-${system.status ? system.status.toLowerCase() : 'unknown'}`;
                statusCell.appendChild(statusIcon);
                const statusText = system.status ? system.status.charAt(0).toUpperCase() + system.status.slice(1) : 'Unknown';
                statusCell.appendChild(document.createTextNode(statusText));

                // Last Updated Cell
                const lastUpdatedCell = row.insertCell();
                lastUpdatedCell.textContent = system.last_updated ? new Date(system.last_updated).toLocaleString() : 'N/A';

                // Message Cell
                const messageCell = row.insertCell();
                messageCell.textContent = system.message || 'N/A'; // Display message or 'N/A'

                // Link Cell
                const linkCell = row.insertCell();
                if (system.url) {
                    const link = document.createElement('a');
                    link.href = system.url;
                    link.textContent = 'Investigate';
                    link.target = '_blank'; // Open link in a new tab
                    link.rel = 'noopener noreferrer'; // Security best practice for target="_blank"
                    linkCell.appendChild(link);
                } else {
                    linkCell.textContent = 'N/A';
                }
            }
        }
    }

    // Initial fetch of health data when the page loads
    fetchHealthData();

    // Set up polling to refresh health data every 30 seconds
    setInterval(fetchHealthData, 30000); // 30000 milliseconds = 30 seconds
});
