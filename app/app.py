from flask import Flask, jsonify, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import datetime
import json
import os
import re
from urllib.parse import urlparse

app = Flask(__name__)

# x_prefix=1 tells Flask to trust the X-Forwarded-Prefix header
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# In-memory data store
# health_data = {
#     "CategoryName": {
#         "ItemName": {"status": "unknown", "last_updated": None, "message": "", "url": ""}
#     }
# }
health_data = {} # Initialize fresh for each run. This is sufficient when app.py is run as a script.


def get_default_item_status():
    """Returns the default status dictionary for a new item."""
    return {"status": "unknown", "last_updated": None, "message": "", "url": ""}


def is_safe_url(target):
    """
    Ensures that a redirect target is safe.
    Only allows http/https protocols.
    """
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https')


def validate_name(name):
    """
    Validates category and item names.
    - Max length: 50 characters
    - Allowed characters: alphanumeric, space, hyphen, underscore, period
    """
    if not name:
        return False, "Name cannot be empty"
    if len(name) > 50:
        return False, "Name exceeds maximum length of 50 characters"
    if not re.match(r'^[a-zA-Z0-9 _.-]+$', name):
        return False, "Name contains invalid characters. Allowed: alphanumeric, space, hyphen, underscore, period"
    return True, ""


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def get_health_data_api():
    """API endpoint to get all health data."""
    return jsonify(health_data)


@app.route('/api/status-config', methods=['GET'])
def get_status_config():
    """API endpoint to get the status configuration."""
    try:
        with open('status_config.json', 'r') as f:
            status_config = json.load(f)
        return jsonify(status_config)
    except FileNotFoundError:
        return jsonify({"error": "status_config.json not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in status_config.json"}), 500


@app.route('/api/checkpoint', methods=['POST'])
def checkpoint_data():
    """Saves the current health_data to a file."""
    try:
        with open('health_data.json', 'w') as f:
            json.dump(health_data, f, indent=4)
        return jsonify({"message": "Data checkpointed successfully to health_data.json"}), 200
    except IOError as e:
        return jsonify({"error": f"Failed to write checkpoint file: {str(e)}"}), 500


@app.route('/api/restore', methods=['POST'])
def restore_data():
    """Restores health_data from a file."""
    global health_data  # noqa: F824
    try:
        with open('health_data.json', 'r') as f:
            data_from_file = json.load(f)
            health_data.clear()
            health_data.update(data_from_file)
        return jsonify({"message": "Data restored successfully from health_data.json"}), 200
    except FileNotFoundError:
        return jsonify({"error": "Checkpoint file 'health_data.json' not found"}), 404
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON in checkpoint file: {str(e)}"}), 500
    except IOError as e:  # Catch other potential I/O errors during read
        return jsonify({"error": f"Failed to read checkpoint file: {str(e)}"}), 500


@app.route('/api/categories', methods=['POST'])
def create_category_api():
    """API endpoint to create a new category."""
    data = request.get_json()
    if not data or 'category_name' not in data:
        return jsonify({"error": "Missing category_name in request body"}), 400

    category_name = data['category_name']
    is_valid, error_msg = validate_name(category_name)
    if not is_valid:
        return jsonify({"error": f"Invalid category_name: {error_msg}"}), 400

    if category_name in health_data:
        return jsonify({"note": f"Category '{category_name}' already exists"}), 200

    health_data[category_name] = {}
    return jsonify({category_name: health_data[category_name]}), 201


@app.route('/api/categories/<category_name>', methods=['DELETE'])
def delete_category_api(category_name):
    """API endpoint to delete a category."""
    if category_name not in health_data:
        return jsonify({"error": f"Category '{category_name}' not found"}), 404

    del health_data[category_name]
    return jsonify({"message": f"Category '{category_name}' deleted successfully"}), 200


@app.route('/api/categories/<category_name>/items', methods=['POST'])
def create_item_api(category_name):
    """API endpoint to add a new item to a category."""
    if category_name not in health_data:
        return jsonify({"error": f"Category '{category_name}' not found"}), 404

    data = request.get_json()
    if not data or 'item_name' not in data:
        return jsonify({"error": "Missing item_name in request body"}), 400

    item_name = data['item_name']
    # Also validate item name since validate_name docs say "category and item names"
    is_valid, error_msg = validate_name(item_name)
    if not is_valid:
        return jsonify({"error": f"Invalid item_name: {error_msg}"}), 400

    if item_name in health_data[category_name]:
        existing_item_data = health_data[category_name][item_name]
        response_data = {"note": "Item already existed."}
        response_data.update(existing_item_data)
        return jsonify(response_data), 200

    health_data[category_name][item_name] = get_default_item_status()
    health_data[category_name][item_name]['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
    return jsonify({item_name: health_data[category_name][item_name]}), 201


@app.route('/api/categories/<category_name>/items/<item_name>', methods=['DELETE'])
def delete_item_api(category_name, item_name):
    """API endpoint to delete an item from a category."""
    if category_name not in health_data:
        return jsonify({"error": f"Category '{category_name}' not found"}), 404
    if item_name not in health_data[category_name]:
        return jsonify({"error": f"Item '{item_name}' not found in category '{category_name}'"}), 404

    del health_data[category_name][item_name]
    # Optional: if category becomes empty, delete it? For now, allow empty categories.
    # if not health_data[category_name]:
    #     del health_data[category_name]
    return jsonify({"message": f"Item '{item_name}' from category '{category_name}' deleted successfully"}), 200


@app.route('/api/categories/<category_name>/items/<item_name>', methods=['PUT'])
def update_item_api(category_name, item_name):
    """API endpoint to update an item's status, message, or url."""
    if category_name not in health_data:
        return jsonify({"error": f"Category '{category_name}' not found"}), 404
    if item_name not in health_data[category_name]:
        return jsonify({"error": f"Item '{item_name}' not found in category '{category_name}'"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    item = health_data[category_name][item_name]

    try:
        with open('status_config.json', 'r') as f:
            status_config = json.load(f)
        valid_statuses = list(status_config.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Server configuration error regarding statuses"}), 500

    if 'status' in data:
        new_status = data['status'].lower()
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        item['status'] = new_status

    if 'message' in data:
        item['message'] = data['message']

    if 'url' in data:
        if is_safe_url(data['url']):
            item['url'] = data['url']

    item['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'

    return jsonify({item_name: item})


if __name__ == '__main__':
    # Use environment variables for configuration, defaulting to secure values.
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host=host, port=port)
