import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as main_app # Renamed to avoid conflict with 'app' instance

class TestShellScriptsSimulated(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()
        main_app.health_data.clear() # Reset health_data

        # Mock datetime for consistent timestamps
        self.mock_datetime = MagicMock()
        self.mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        self.patcher = patch('app.datetime', self.mock_datetime)
        self.patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.patcher.stop()

    def _get_expected_timestamp(self):
        return self.mock_datetime.utcnow.return_value.isoformat.return_value + 'Z'

    def simulate_setup_dashboard_sh(self):
        """Simulates the actions of setup_dashboard.sh using the test client."""
        # Create categories
        categories = ["Builds", "Tests", "Hosts Online", "Operational Systems"] # Changed "Host_Up_Down" to "Hosts Online"
        for cat in categories:
            self.client.post('/api/categories', json={'category_name': cat})

        # Add items
        self.client.post('/api/categories/Builds/items', json={'item_name': 'Main Build'})
        self.client.post('/api/categories/Builds/items', json={'item_name': 'Release Build'})

        test_items = ["Login Test", "API Test", "Performance Test", "Security Scan"]
        for item in test_items:
            self.client.post('/api/categories/Tests/items', json={'item_name': item})

        host_items = ["mars", "saturn", "jupiter"]
        for item in host_items:
            # Category name changed here. Flask test client handles spaces in path segments.
            self.client.post('/api/categories/Hosts Online/items', json={'item_name': item})

        self.client.post('/api/categories/Operational Systems/items', json={'item_name': 'Core OS Services'})


    def simulate_update_status_examples_sh(self):
        """Simulates the actions of update_status_examples.sh using the test client."""
        # Update "Main Build"
        self.client.put('/api/categories/Builds/items/Main%20Build',
                        json={"status": "passing", "message": "Build successful on commit abc1234", "url": "http://jenkins.example.com/builds/main/101"})

        # Update "mars" - category name changed. Test client handles space in 'Hosts Online'.
        self.client.put('/api/categories/Hosts Online/items/mars',
                        json={"status": "down", "message": "Host mars is unresponsive, ping failed.", "url": "http://monitoring.example.com/hosts/mars"})
        # Update "jupiter" - category name changed
        self.client.put('/api/categories/Hosts Online/items/jupiter',
                        json={"status": "running", "message": "All systems normal.", "url": "http://monitoring.example.com/hosts/jupiter"})

        # Update "Login Test"
        self.client.put('/api/categories/Tests/items/Login%20Test',
                        json={"status": "failing", "message": "Login test failed: credentials expired.", "url": "http://tests.example.com/results/login/latest"})
        # Update "API Test"
        self.client.put('/api/categories/Tests/items/API%20Test',
                        json={"status": "passing", "message": "All API endpoints responding correctly.", "url": "http://tests.example.com/results/api/latest"})

        # Update "Core OS Services"
        self.client.put('/api/categories/Operational%20Systems/items/Core%20OS%20Services',
                        json={"status": "running", "message": "Operational system services are stable.", "url": "http://status.example.com/os"})


    def test_setup_dashboard_script_simulation(self):
        """Test the state of health_data after simulating setup_dashboard.sh."""
        self.simulate_setup_dashboard_sh()

        health = main_app.health_data
        self.assertIn("Builds", health)
        self.assertIn("Main Build", health["Builds"])
        self.assertEqual(health["Builds"]["Main Build"]["status"], "unknown")
        self.assertEqual(health["Builds"]["Release Build"]["status"], "unknown")

        self.assertIn("Tests", health)
        self.assertEqual(len(health["Tests"]), 4)
        self.assertEqual(health["Tests"]["Login Test"]["status"], "unknown")

        self.assertIn("Hosts Online", health) # Changed category name
        self.assertEqual(len(health["Hosts Online"]), 3)
        self.assertEqual(health["Hosts Online"]["mars"]["status"], "unknown")

        self.assertIn("Operational Systems", health)
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["status"], "unknown")
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["last_updated"], self._get_expected_timestamp())


    def test_update_status_examples_script_simulation(self):
        """Test the state of health_data after simulating both scripts."""
        self.simulate_setup_dashboard_sh() # Start with the base setup
        self.simulate_update_status_examples_sh() # Apply updates

        health = main_app.health_data
        ts = self._get_expected_timestamp()

        # Check updated items
        self.assertEqual(health["Builds"]["Main Build"]["status"], "passing")
        self.assertEqual(health["Builds"]["Main Build"]["message"], "Build successful on commit abc1234")
        self.assertEqual(health["Builds"]["Main Build"]["last_updated"], ts)

        self.assertEqual(health["Hosts Online"]["mars"]["status"], "down") # Changed category name
        self.assertEqual(health["Hosts Online"]["jupiter"]["status"], "running") # Changed category name

        self.assertEqual(health["Tests"]["Login Test"]["status"], "failing")
        self.assertEqual(health["Tests"]["API Test"]["status"], "passing")

        self.assertEqual(health["Operational Systems"]["Core OS Services"]["status"], "running")
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["last_updated"], ts)


if __name__ == '__main__':
    unittest.main()
