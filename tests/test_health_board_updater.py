import unittest
from unittest.mock import patch, MagicMock
from health_board_api import HealthBoardUpdater

class TestHealthBoardUpdater(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://fake-url.com"
        self.category = "test_category"
        self.item = "test_item"
        self.updater = HealthBoardUpdater(self.base_url, self.category, self.item)

    @patch('health_board_api.HealthBoard.update_item')
    def test_update_item_with_all_params_and_upsert_false(self, mock_update_item):
        status = "testing"
        message = "This is a test"
        url = "http://test.com"

        self.updater.update_item(status=status, message=message, url=url, upsert=False)

        mock_update_item.assert_called_once_with(
            self.category,
            self.item,
            status,
            message,
            url,
            False
        )

    @patch('health_board_api.HealthBoard.update_item')
    def test_update_item_with_default_upsert(self, mock_update_item):
        status = "passing"

        self.updater.update_item(status=status)

        mock_update_item.assert_called_once_with(
            self.category,
            self.item,
            status,
            None,
            None,
            True
        )

    @patch('health_board_api.HealthBoard.update_item')
    def test_update_item_with_no_params(self, mock_update_item):
        self.updater.update_item()

        mock_update_item.assert_called_once_with(
            self.category,
            self.item,
            None,
            None,
            None,
            True
        )
