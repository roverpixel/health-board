from flask import Flask, jsonify, render_template, request
import datetime

app = Flask(__name__)

# In-memory store for health statuses
# Each system has a dictionary with:
# - status: current health status (string, e.g., "passing", "failing")
# - last_updated: ISO 8601 timestamp of the last update (string)
# - message: optional descriptive message (string)
# - url: optional link for more details (string)
health_statuses = {
    "builds": {"status": "unknown", "last_updated": None, "message": "", "url": ""},
    "tests": {"status": "unknown", "last_updated": None, "message": "", "url": ""},
    "host_activity": {"status": "unknown", "last_updated": None, "message": "", "url": ""},
    "host_up_down": {"status": "unknown", "last_updated": None, "message": "", "url": ""},
    "operational_system": {"status": "unknown", "last_updated": None, "message": "", "url": ""},
}

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def get_health_statuses_api():
    """API endpoint to get all health statuses."""
    return jsonify(health_statuses)

@app.route('/api/health/<system_name>', methods=['POST'])
def update_health_status_api(system_name):
    """API endpoint to update the health status of a specific system."""
    if system_name not in health_statuses:
        return jsonify({"error": "System not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    valid_statuses = ["running", "down", "passing", "failing", "unknown"]
    new_status = data.get('status')

    if new_status and new_status.lower() not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

    # Update fields if provided in the request
    if new_status:
        health_statuses[system_name]['status'] = new_status.lower()
    if 'message' in data: # Allow empty string for message
        health_statuses[system_name]['message'] = data['message']
    if 'url' in data: # Allow empty string for url
        health_statuses[system_name]['url'] = data['url']

    health_statuses[system_name]['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'

    return jsonify({system_name: health_statuses[system_name]})

if __name__ == '__main__':
    # Note: debug=True is for development only.
    # Use a production WSGI server (e.g., Gunicorn) for deployment.
    app.run(debug=True, host='0.0.0.0', port=5000)
