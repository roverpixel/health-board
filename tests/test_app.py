import unittest
import json
from unittest.mock import patch # Removed MagicMock as it's implicitly used by patch
import sys
import os

# Adjust path to import app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as main_app

class TestAppAPI(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        main_app.app.testing = True
        self.client = main_app.app.test_client()
        main_app.health_data.clear()

        # Patch datetime.datetime within the 'app' module's scope
        self.patcher_datetime = patch('app.datetime.datetime')
        self.mocked_datetime_class = self.patcher_datetime.start()

        # Configure the mock for the chain: datetime.datetime.utcnow().isoformat()
        # self.mocked_datetime_class.utcnow.return_value will be a MagicMock by default
        self.mocked_datetime_class.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"

    def tearDown(self):
        """Clean up after each test."""
        self.patcher_datetime.stop()

    def _get_expected_timestamp(self):
        # Access the configured return value through the mocked class structure
        return self.mocked_datetime_class.utcnow.return_value.isoformat.return_value + 'Z'


    # Category Tests
    def test_create_category(self):
        response = self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Cat1', response.json)
        self.assertEqual(main_app.health_data['Cat1'], {})

    def test_create_category_duplicate(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_create_category_missing_name(self):
        response = self.client.post('/api/categories', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_delete_category(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.delete('/api/categories/Cat1')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Cat1', main_app.health_data)

    def test_delete_category_not_found(self):
        response = self.client.delete('/api/categories/NonExistentCat')
        self.assertEqual(response.status_code, 404)

    # Item Tests
    def test_create_item(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        self.assertEqual(response.status_code, 201)
        expected_item_data = {
            "status": "unknown",
            "last_updated": self._get_expected_timestamp(),
            "message": "",
            "url": ""
        }
        self.assertEqual(response.json['Item1'], expected_item_data)
        self.assertEqual(main_app.health_data['Cat1']['Item1'], expected_item_data)

    def test_create_item_category_not_found(self):
        response = self.client.post('/api/categories/NonExistentCat/items', json={'item_name': 'Item1'})
        self.assertEqual(response.status_code, 404)

    def test_create_item_duplicate(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        # First creation
        first_response = self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        self.assertEqual(first_response.status_code, 201)
        created_item_data = first_response.json['Item1']

        # Attempt to create duplicate
        response = self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        self.assertEqual(response.status_code, 200)
        response_json = response.json
        self.assertEqual(response_json.get("note"), "Item already existed.")
        # Check that the other fields match the originally created item
        self.assertEqual(response_json.get("status"), created_item_data["status"])
        self.assertEqual(response_json.get("last_updated"), created_item_data["last_updated"])
        self.assertEqual(response_json.get("message"), created_item_data["message"])
        self.assertEqual(response_json.get("url"), created_item_data["url"])

    def test_create_item_missing_name(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.post('/api/categories/Cat1/items', json={})
        self.assertEqual(response.status_code, 400)

    def test_update_item(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})

        update_payload = {"status": "passing", "message": "All good", "url": "http://example.com"}
        response = self.client.put('/api/categories/Cat1/items/Item1', json=update_payload)
        self.assertEqual(response.status_code, 200)

        expected_item_data = {
            "status": "passing",
            "last_updated": self._get_expected_timestamp(),
            "message": "All good",
            "url": "http://example.com"
        }
        self.assertEqual(response.json['Item1'], expected_item_data)
        self.assertEqual(main_app.health_data['Cat1']['Item1'], expected_item_data)

    def test_update_item_partial(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})

        update_payload = {"status": "failing"}
        response = self.client.put('/api/categories/Cat1/items/Item1', json=update_payload)
        self.assertEqual(response.status_code, 200)

        expected_item_data = {
            "status": "failing",
            "last_updated": self._get_expected_timestamp(),
            "message": "",
            "url": ""
        }
        self.assertEqual(response.json['Item1'], expected_item_data)
        self.assertEqual(main_app.health_data['Cat1']['Item1'], expected_item_data)

    def test_update_item_invalid_status(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        response = self.client.put('/api/categories/Cat1/items/Item1', json={'status': 'invalid_state'})
        self.assertEqual(response.status_code, 400)

    def test_update_item_status_up(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})

        update_payload = {"status": "up"}
        response = self.client.put('/api/categories/Cat1/items/Item1', json=update_payload)
        self.assertEqual(response.status_code, 200)

        expected_item_data = {
            "status": "up",
            "last_updated": self._get_expected_timestamp(),
            "message": "",
            "url": ""
        }
        self.assertEqual(response.json['Item1'], expected_item_data)
        self.assertEqual(main_app.health_data['Cat1']['Item1'], expected_item_data)

    def test_update_item_category_not_found(self):
        response = self.client.put('/api/categories/NonExistentCat/items/Item1', json={'status': 'passing'})
        self.assertEqual(response.status_code, 404)

    def test_update_item_item_not_found(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.put('/api/categories/Cat1/items/NonExistentItem', json={'status': 'passing'})
        self.assertEqual(response.status_code, 404)

    def test_delete_item(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        response = self.client.delete('/api/categories/Cat1/items/Item1')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Item1', main_app.health_data['Cat1'])

    def test_delete_item_category_not_found(self):
        response = self.client.delete('/api/categories/NonExistentCat/items/Item1')
        self.assertEqual(response.status_code, 404)

    def test_delete_item_item_not_found(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        response = self.client.delete('/api/categories/Cat1/items/NonExistentItem')
        self.assertEqual(response.status_code, 404)

    def test_get_health_data(self):
        self.client.post('/api/categories', json={'category_name': 'Cat1'})
        self.client.post('/api/categories/Cat1/items', json={'item_name': 'Item1'})
        self.client.put('/api/categories/Cat1/items/Item1', json={"status": "passing", "message": "OK"})

        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)

        expected_data = {
            "Cat1": {
                "Item1": {
                    "status": "passing",
                    "last_updated": self._get_expected_timestamp(),
                    "message": "OK",
                    "url": ""
                }
            }
        }
        self.assertEqual(response.json, expected_data)
        self.assertEqual(main_app.health_data, expected_data)

    def test_get_empty_health_data(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {})
        self.assertEqual(main_app.health_data, {})

    # Checkpoint and Restore Tests
    def test_checkpoint_and_restore(self):
        # 1. Setup initial data
        self.client.post('/api/categories', json={'category_name': 'TestCat'})
        self.client.post('/api/categories/TestCat/items', json={'item_name': 'TestItem'})
        update_payload = {"status": "passing", "message": "Checkpoint test", "url": "http://checkpoint.example.com"}
        self.client.put('/api/categories/TestCat/items/TestItem', json=update_payload)

        initial_data = main_app.health_data.copy()

        # 2. Test /checkpoint
        response_checkpoint = self.client.post('/api/checkpoint')
        self.assertEqual(response_checkpoint.status_code, 200)
        self.assertIn("Data checkpointed successfully", response_checkpoint.json['message'])

        # Verify file content
        self.assertTrue(os.path.exists('health_data.json'))
        with open('health_data.json', 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file, initial_data)

        # 3. Modify in-memory data to ensure restore actually works
        main_app.health_data.clear()
        main_app.health_data['AnotherCat'] = {} # Make it different from checkpointed data

        # 4. Test /restore
        response_restore = self.client.post('/api/restore')
        self.assertEqual(response_restore.status_code, 200)
        self.assertIn("Data restored successfully", response_restore.json['message'])
        self.assertEqual(main_app.health_data, initial_data) # Should be back to original

        # 5. Clean up
        if os.path.exists('health_data.json'):
            os.remove('health_data.json')

    def test_restore_file_not_found(self):
        # Ensure file does not exist
        if os.path.exists('health_data.json'):
            os.remove('health_data.json')

        response = self.client.post('/api/restore')
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json['error'])

    def test_restore_invalid_json(self):
        # Create an invalid JSON file
        with open('health_data.json', 'w') as f:
            f.write("this is not valid json")

        response = self.client.post('/api/restore')
        self.assertEqual(response.status_code, 500)
        self.assertIn("Invalid JSON", response.json['error'])

        # Clean up
        if os.path.exists('health_data.json'):
            os.remove('health_data.json')

if __name__ == '__main__':
    unittest.main()
