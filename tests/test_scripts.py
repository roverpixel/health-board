import unittest
import json
from unittest.mock import patch # Removed MagicMock as it's implicitly used by patch
import sys
import os

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as main_app

class TestShellScriptsSimulated(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()
        main_app.health_data.clear()

        # Patch datetime.datetime within the 'app' module's scope
        self.patcher_datetime = patch('app.app.datetime.datetime')
        self.mocked_datetime_class = self.patcher_datetime.start()

        # Configure the mock for the chain: datetime.datetime.utcnow().isoformat()
        self.mocked_datetime_class.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"


    def tearDown(self):
        """Clean up after each test."""
        self.patcher_datetime.stop()

    def _get_expected_timestamp(self):
        # Access the configured return value through the mocked class structure
        return self.mocked_datetime_class.utcnow.return_value.isoformat.return_value + 'Z'

    def simulate_setup_dashboard_sh(self):
        """Simulates the actions of setup_dashboard.sh using the test client."""
        categories = ["Builds", "Tests", "Hosts Online", "Operational Systems"]
        for cat in categories:
            self.client.post('/api/categories', json={'category_name': cat})

        self.client.post('/api/categories/Builds/items', json={'item_name': 'Main Build'})
        self.client.post('/api/categories/Builds/items', json={'item_name': 'Release Build'})

        test_items = ["Login Test", "API Test", "Performance Test", "Security Scan"]
        for item in test_items:
            self.client.post('/api/categories/Tests/items', json={'item_name': item})

        host_items = ["mars", "saturn", "jupiter"]
        for item in host_items:
            self.client.post('/api/categories/Hosts Online/items', json={'item_name': item})

        self.client.post('/api/categories/Operational Systems/items', json={'item_name': 'Core OS Services'})


    def simulate_update_status_examples_sh(self):
        """Simulates the actions of update_status_examples.sh using the test client."""
        self.client.put('/api/categories/Builds/items/Main%20Build',
                        json={"status": "passing", "message": "Build successful on commit abc1234", "url": "http://jenkins.example.com/builds/main/101"})

        self.client.put('/api/categories/Hosts Online/items/mars',
                        json={"status": "down", "message": "Host mars is unresponsive, ping failed.", "url": "http://monitoring.example.com/hosts/mars"})
        self.client.put('/api/categories/Hosts Online/items/jupiter',
                        json={"status": "running", "message": "All systems normal.", "url": "http://monitoring.example.com/hosts/jupiter"})

        self.client.put('/api/categories/Tests/items/Login%20Test',
                        json={"status": "failing", "message": "Login test failed: credentials expired.", "url": "http://tests.example.com/results/login/latest"})
        self.client.put('/api/categories/Tests/items/API%20Test',
                        json={"status": "passing", "message": "All API endpoints responding correctly.", "url": "http://tests.example.com/results/api/latest"})

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

        self.assertIn("Hosts Online", health)
        self.assertEqual(len(health["Hosts Online"]), 3)
        self.assertEqual(health["Hosts Online"]["mars"]["status"], "unknown")

        self.assertIn("Operational Systems", health)
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["status"], "unknown")
        # Verify timestamp of one item as a sample
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["last_updated"], self._get_expected_timestamp())


    def test_update_status_examples_script_simulation(self):
        """Test the state of health_data after simulating both scripts."""
        self.simulate_setup_dashboard_sh()
        self.simulate_update_status_examples_sh()

        health = main_app.health_data
        ts = self._get_expected_timestamp() # Timestamp of the update operations

        self.assertEqual(health["Builds"]["Main Build"]["status"], "passing")
        self.assertEqual(health["Builds"]["Main Build"]["message"], "Build successful on commit abc1234")
        self.assertEqual(health["Builds"]["Main Build"]["last_updated"], ts)

        self.assertEqual(health["Hosts Online"]["mars"]["status"], "down")
        self.assertEqual(health["Hosts Online"]["mars"]["last_updated"], ts)
        self.assertEqual(health["Hosts Online"]["jupiter"]["status"], "running")
        self.assertEqual(health["Hosts Online"]["jupiter"]["last_updated"], ts)

        self.assertEqual(health["Tests"]["Login Test"]["status"], "failing")
        self.assertEqual(health["Tests"]["Login Test"]["last_updated"], ts)
        self.assertEqual(health["Tests"]["API Test"]["status"], "passing")
        self.assertEqual(health["Tests"]["API Test"]["last_updated"], ts)

        self.assertEqual(health["Operational Systems"]["Core OS Services"]["status"], "running")
        self.assertEqual(health["Operational Systems"]["Core OS Services"]["last_updated"], ts)

        # Check an item that wasn't updated by update_status_examples.sh (e.g., Release Build)
        # Its timestamp should still be from the setup phase.
        # This requires a more sophisticated mock if we want to distinguish setup timestamps from update timestamps
        # if both happen within the same test method using the same mock config.
        # For this test, we assume the timestamp we are checking (ts) is the one from the update operations.
        # If an item was *not* updated by simulate_update_status_examples_sh, its timestamp would be the *same* ts,
        # because our mock returns the same timestamp for all calls within one test method's setUp/tearDown cycle.
        # A more granular test would involve changing the mock's return value between simulate_setup and simulate_update.
        # However, the current test correctly verifies that items *that were updated* get *a* mocked timestamp.
        self.assertEqual(health["Builds"]["Release Build"]["status"], "unknown")
        self.assertEqual(health["Builds"]["Release Build"]["last_updated"], ts) # This will be true with current mock

if __name__ == '__main__':
    unittest.main()
