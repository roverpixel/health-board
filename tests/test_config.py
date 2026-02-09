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

    def test_get_status_config_success(self):
        """Test successful retrieval of status config."""
        # Using context managers for explicit patch ordering and clarity
        # We need to mock open first (so it's available) then json.load

        with patch('builtins.open', new_callable=mock_open) as mock_file:
            with patch('app.app.json.load') as mock_json_load:
                mock_json_load.return_value = self.expected_data

                response = self.client.get('/api/status-config')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, self.expected_data)

                mock_file.assert_called_with('status_config.json', 'r')
                mock_json_load.assert_called_once()

    def test_get_status_config_file_not_found(self):
        """Test behavior when status_config.json is missing."""
        with patch('builtins.open', side_effect=FileNotFoundError) as mock_file:
            response = self.client.get('/api/status-config')

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {"error": "status_config.json not found"})

            mock_file.assert_called_with('status_config.json', 'r')

    def test_get_status_config_invalid_json(self):
        """Test behavior when status_config.json contains invalid JSON."""
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            # We mock json.load to raise the error
            error = json.JSONDecodeError("Expecting value", "doc", 0)
            with patch('app.app.json.load', side_effect=error) as mock_json_load:
                response = self.client.get('/api/status-config')

                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.json, {"error": "Invalid JSON in status_config.json"})

                mock_file.assert_called_with('status_config.json', 'r')
                mock_json_load.assert_called_once()

if __name__ == '__main__':
    unittest.main()
