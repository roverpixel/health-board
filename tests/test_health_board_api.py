import unittest
from unittest.mock import patch, Mock
import requests
from health_board_api import HealthBoard

class TestHealthBoardAPI(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://mock-api.com"
        self.board = HealthBoard(base_url=self.base_url)

    def _mock_response(self, status_code=200, json_data=None, raise_for_status=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data if json_data is not None else {}

        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        else:
            mock_resp.raise_for_status.return_value = None

        return mock_resp

    @patch('requests.request')
    def test_get_health_success(self, mock_request):
        expected_data = {"status": "healthy"}
        mock_request.return_value = self._mock_response(json_data=expected_data)

        data = self.board.get_health()

        self.assertEqual(data, expected_data)
        mock_request.assert_called_once_with('GET', f"{self.base_url}/health")

    @patch('requests.request')
    def test_checkpoint_success(self, mock_request):
        expected_data = {"message": "Checkpoint created"}
        mock_request.return_value = self._mock_response(json_data=expected_data)

        data = self.board.checkpoint()

        self.assertEqual(data, expected_data)
        mock_request.assert_called_once_with('POST', f"{self.base_url}/checkpoint")

    @patch('requests.request')
    def test_restore_success(self, mock_request):
        expected_data = {"message": "Restored from checkpoint"}
        mock_request.return_value = self._mock_response(json_data=expected_data)

        data = self.board.restore()

        self.assertEqual(data, expected_data)
        mock_request.assert_called_once_with('POST', f"{self.base_url}/restore")

    @patch('requests.request')
    def test_create_category_success(self, mock_request):
        category_name = "test-category"
        expected_data = {"category_name": category_name}
        mock_request.return_value = self._mock_response(json_data=expected_data)

        data = self.board.create_category(category_name)

        self.assertEqual(data, expected_data)
        mock_request.assert_called_once_with('POST', f"{self.base_url}/categories", json={"category_name": category_name})

    @patch('requests.request')
    def test_delete_category_success(self, mock_request):
        category_name = "test-category"
        mock_request.return_value = self._mock_response(status_code=204)

        response = self.board.delete_category(category_name)

        self.assertEqual(response.status_code, 204)
        mock_request.assert_called_once_with('DELETE', f"{self.base_url}/categories/{category_name}")

    @patch('requests.request')
    def test_create_item_success(self, mock_request):
        category_name = "test-category"
        item_name = "test-item"
        expected_data = {"item_name": item_name}

        # Mock the responses for both category creation and item creation
        mock_create_category_response = self._mock_response(status_code=201, json_data={"category_name": category_name})
        mock_create_item_response = self._mock_response(status_code=201, json_data=expected_data)
        mock_request.side_effect = [mock_create_category_response, mock_create_item_response]

        data = self.board.create_item(category_name, item_name, upsert=True)

        self.assertEqual(data, expected_data)
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_any_call('POST', f"{self.base_url}/categories", json={"category_name": category_name})
        mock_request.assert_any_call('POST', f"{self.base_url}/categories/{category_name}/items", json={"item_name": item_name})

    @patch('requests.request')
    def test_create_item_upsert_category_exists(self, mock_request):
        category_name = "existing-category"
        item_name = "new-item"
        expected_item_data = {"item_name": item_name}

        # Simulate category creation returning a 200 OK, then item creation succeeding
        mock_create_category_response = self._mock_response(status_code=200, json_data={"note": "Category already exists"})
        mock_create_item_response = self._mock_response(status_code=201, json_data=expected_item_data)
        mock_request.side_effect = [mock_create_category_response, mock_create_item_response]

        data = self.board.create_item(category_name, item_name, upsert=True)

        self.assertEqual(data, expected_item_data)
        self.assertEqual(mock_request.call_count, 2)

    @patch('requests.request')
    def test_create_item_no_upsert_fails(self, mock_request):
        category_name = "non-existent-category"
        item_name = "some-item"

        # Simulate item creation failing because the category doesn't exist
        mock_request.return_value = self._mock_response(status_code=404, raise_for_status=requests.exceptions.HTTPError(response=self._mock_response(404)))

        with self.assertRaises(requests.exceptions.HTTPError):
            self.board.create_item(category_name, item_name, upsert=False)

        mock_request.assert_called_once_with('POST', f"{self.base_url}/categories/{category_name}/items", json={"item_name": item_name})

    @patch('requests.request')
    def test_delete_item_success(self, mock_request):
        category_name = "test-category"
        item_name = "test-item"
        mock_request.return_value = self._mock_response(status_code=204)

        response = self.board.delete_item(category_name, item_name)

        self.assertEqual(response.status_code, 204)
        mock_request.assert_called_once_with('DELETE', f"{self.base_url}/categories/{category_name}/items/{item_name}")

    @patch('requests.request')
    def test_update_item_success(self, mock_request):
        category_name = "test-category"
        item_name = "test-item"
        update_payload = {"status": "passing", "message": "Tests are green."}
        expected_data = {"status": "passing", "message": "Tests are green."}

        # Mock responses for create_item (category and item) and the final update
        mock_create_cat = self._mock_response(201, {"category_name": category_name})
        mock_create_item = self._mock_response(201, {"item_name": item_name})
        mock_update_item = self._mock_response(200, expected_data)
        mock_request.side_effect = [mock_create_cat, mock_create_item, mock_update_item]

        data = self.board.update_item(category_name, item_name, status="passing", message="Tests are green.", upsert=True)

        self.assertEqual(data, expected_data)
        self.assertEqual(mock_request.call_count, 3)
        mock_request.assert_called_with('PUT', f"{self.base_url}/categories/{category_name}/items/{item_name}", json=update_payload)

    def test_update_item_no_params(self):
        # This test is no longer valid as the method now returns a message instead of raising an error.
        # We can test for the message instead.
        category_name = "cat"
        item_name = "item"
        # Mock responses for the create_item call within update_item
        with patch.object(self.board, 'create_item', return_value=None) as mock_create:
            response = self.board.update_item(category_name, item_name)
            self.assertEqual(response, {"message": "No update parameters provided. Item state unchanged."})
            mock_create.assert_called_once_with(category_name, item_name, upsert=True)


    @patch('requests.request')
    def test_update_item_no_upsert_fails(self, mock_request):
        category_name = "non-existent-category"
        item_name = "some-item"

        # Simulate update failing because the item/category does not exist
        mock_request.return_value = self._mock_response(status_code=404, raise_for_status=requests.exceptions.HTTPError(response=self._mock_response(404)))

        with self.assertRaises(requests.exceptions.HTTPError):
            self.board.update_item(category_name, item_name, status="failing", upsert=False)

        mock_request.assert_called_once_with('PUT', f"{self.base_url}/categories/{category_name}/items/{item_name}", json={"status": "failing"})

    @patch('requests.request')
    def test_request_failure(self, mock_request):
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")

        with self.assertRaises(requests.exceptions.RequestException):
            self.board.get_health()

if __name__ == '__main__':
    unittest.main()
