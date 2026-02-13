import unittest
import json
import os
import sys

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as main_app

class TestStatusConfig(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()

    def test_get_status_config(self):
        """Test that the status config endpoint returns the loaded configuration."""
        response = self.client.get('/api/status-config')
        self.assertEqual(response.status_code, 200)

        # Verify content matches main_app.STATUS_CONFIG
        self.assertEqual(response.json, main_app.STATUS_CONFIG)

        # Verify specific keys exist (basic sanity check)
        self.assertIn("passing", response.json)
        self.assertIn("failing", response.json)
        self.assertIn("unknown", response.json)

if __name__ == '__main__':
    unittest.main()
