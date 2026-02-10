import unittest
import json
import os
import sys
from unittest.mock import patch

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as main_app

class TestCheckpoint(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()
        main_app.health_data.clear()

        # Ensure we are working with a clean slate for files
        if os.path.exists('health_data.json'):
            os.remove('health_data.json')

    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists('health_data.json'):
            os.remove('health_data.json')

    def test_checkpoint_data_success(self):
        """Test successful checkpointing of data."""
        main_app.health_data['TestCat'] = {'TestItem': {'status': 'ok'}}

        response = self.client.post('/api/checkpoint')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Data checkpointed successfully", response.json['message'])

        self.assertTrue(os.path.exists('health_data.json'))
        with open('health_data.json', 'r') as f:
            data = json.load(f)
        self.assertEqual(data, main_app.health_data)

    def test_restore_data_success(self):
        """Test successful restoration of data."""
        initial_data = {'TestCat': {'TestItem': {'status': 'ok'}}}
        with open('health_data.json', 'w') as f:
            json.dump(initial_data, f)

        response = self.client.post('/api/restore')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Data restored successfully", response.json['message'])
        self.assertEqual(main_app.health_data, initial_data)

    def test_restore_data_io_error(self):
        """Test error handling when reading checkpoint file fails."""
        # Mock open to raise IOError (which is OSError in Python 3)
        # We ensure it's not a FileNotFoundError by using a generic message
        with patch('builtins.open', side_effect=IOError("Simulated read error")):
            response = self.client.post('/api/restore')

            self.assertEqual(response.status_code, 500)
            self.assertIn("Failed to read checkpoint file: Simulated read error", response.json['error'])

    def test_checkpoint_data_io_error(self):
        """Test error handling when writing checkpoint file fails."""
        with patch('builtins.open', side_effect=IOError("Simulated write error")):
            response = self.client.post('/api/checkpoint')

            self.assertEqual(response.status_code, 500)
            self.assertIn("Failed to write checkpoint file: Simulated write error", response.json['error'])

if __name__ == '__main__':
    unittest.main()
