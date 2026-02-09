import unittest
import json
from unittest.mock import patch, mock_open
import sys
import os

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as main_app

class TestStatusConfig(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()

        # Load the actual status_config.json for validation
        config_path = os.path.join(os.path.dirname(__file__), '..', 'status_config.json')
        with open(config_path, 'r') as f:
            self.expected_data = json.load(f)

    @patch('app.app.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_status_config_success(self, mock_file, mock_json_load):
        """Test successful retrieval of status config."""
        # Argument order: Bottom decorator (open) -> 1st arg, Top decorator (json.load) -> 2nd arg

        mock_json_load.return_value = self.expected_data

        response = self.client.get('/api/status-config')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.expected_data)

        mock_file.assert_called_with('status_config.json', 'r')
        mock_json_load.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_status_config_file_not_found(self, mock_file):
        """Test behavior when status_config.json is missing."""
        response = self.client.get('/api/status-config')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "status_config.json not found"})

    @patch('app.app.json.load', side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    @patch('builtins.open', new_callable=mock_open)
    def test_get_status_config_invalid_json(self, mock_file, mock_json_load):
        """Test behavior when status_config.json contains invalid JSON."""
        # Argument order: Bottom decorator (open) -> 1st arg, Top decorator (json.load) -> 2nd arg

        response = self.client.get('/api/status-config')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Invalid JSON in status_config.json"})

if __name__ == '__main__':
    unittest.main()
