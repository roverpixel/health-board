import unittest
import json
from app.app import app, health_data

class TestURLValidation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        health_data.clear()
        # Setup initial state
        self.app.post('/api/categories', json={'category_name': 'TestCat'})
        self.app.post('/api/categories/TestCat/items', json={'item_name': 'TestItem'})

    def test_valid_urls(self):
        valid_urls = [
            "http://example.com",
            "https://example.com/path?query=1"
        ]
        for url in valid_urls:
            response = self.app.put('/api/categories/TestCat/items/TestItem',
                                    json={'url': url})
            self.assertEqual(response.status_code, 200)
            item = health_data['TestCat']['TestItem']
            self.assertEqual(item['url'], url)

    def test_invalid_schemes(self):
        invalid_urls = [
            "javascript:alert(1)",
            "ftp://example.com",
            "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==",
            "www.google.com" # Missing scheme
        ]

        # First set a valid URL
        self.app.put('/api/categories/TestCat/items/TestItem',
                     json={'url': "http://original.com"})

        for url in invalid_urls:
            response = self.app.put('/api/categories/TestCat/items/TestItem',
                                    json={'url': url})
            self.assertEqual(response.status_code, 200)
            item = health_data['TestCat']['TestItem']
            # Should match original URL (update ignored)
            self.assertEqual(item['url'], "http://original.com", f"URL '{url}' should be rejected")

    def test_empty_string_clears_url(self):
        # First set a valid URL
        self.app.put('/api/categories/TestCat/items/TestItem',
                     json={'url': "http://original.com"})

        # Send empty string
        response = self.app.put('/api/categories/TestCat/items/TestItem',
                                json={'url': ""})
        self.assertEqual(response.status_code, 200)
        item = health_data['TestCat']['TestItem']
        self.assertEqual(item['url'], "")

    def test_partial_update_with_invalid_url(self):
        # Ensure other fields are updated even if URL is invalid
        response = self.app.put('/api/categories/TestCat/items/TestItem',
                                json={
                                    'url': "javascript:bad()",
                                    'message': "Updated Message",
                                    'status': 'degraded' # assuming 'degraded' is valid, need to check config
                                })

        # Wait, 'degraded' might not be in status_config.json.
        # I should check status_config.json or use a safe status.
        # But 'status' validation is strict.
        # Let's check status_config.json first or mock it.
        # But for now, let's just update 'message'.

        response = self.app.put('/api/categories/TestCat/items/TestItem',
                                json={
                                    'url': "javascript:bad()",
                                    'message': "Updated Message"
                                })

        self.assertEqual(response.status_code, 200)
        item = health_data['TestCat']['TestItem']
        self.assertEqual(item['message'], "Updated Message")
        self.assertEqual(item['url'], "") # Default was "", and update was ignored.

if __name__ == '__main__':
    unittest.main()
