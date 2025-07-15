import unittest
from unittest.mock import patch, MagicMock
from health_board_api import HealthBoardUpdater

class TestHealthBoardUpdater(unittest.TestCase):

    @patch('health_board_api.HealthBoard.update_item')
    def test_update_item(self, mock_update_item):
        # Arrange
        base_url = "http://fake-url.com"
        category = "test_category"
        item = "test_item"
        status = "testing"
        message = "This is a test"
        url = "http://test.com"

        updater = HealthBoardUpdater(base_url, category, item)

        # Act
        updater.update_item(status=status, message=message, url=url, upsert=False)

        # Assert
        mock_update_item.assert_called_once_with(category, item, status, message, url, False)
