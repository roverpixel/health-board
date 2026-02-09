import unittest
import json
from app.app import app

class TestSecurityValidation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear health_data before each test if possible, or just rely on new names.
        # Since `health_data` is global in app.py, tests might interfere if not careful.
        # Ideally, I would reset it, but `app.py` doesn't expose a reset function easily
        # without restarting or importing the global. Let's just import it and clear it.
        from app.app import health_data
        health_data.clear()

    def test_create_category_valid(self):
        response = self.app.post('/api/categories', json={'category_name': 'Valid_Name-123'})
        self.assertEqual(response.status_code, 201)

    def test_create_category_too_long(self):
        long_name = "A" * 51
        response = self.app.post('/api/categories', json={'category_name': long_name})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid category_name", response.data)

    def test_create_category_invalid_chars(self):
        invalid_names = ["<script>", "name/with/slashes", "name with @", "name!"]
        for name in invalid_names:
            response = self.app.post('/api/categories', json={'category_name': name})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b"Invalid category_name", response.data)

    def test_create_item_valid(self):
        # Create category first
        self.app.post('/api/categories', json={'category_name': 'Cat1'})

        response = self.app.post('/api/categories/Cat1/items', json={'item_name': 'Valid Item.Name'})
        self.assertEqual(response.status_code, 201)

    def test_create_item_too_long(self):
        self.app.post('/api/categories', json={'category_name': 'Cat1'})
        long_name = "B" * 51
        response = self.app.post('/api/categories/Cat1/items', json={'item_name': long_name})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid item_name", response.data)

    def test_create_item_invalid_chars(self):
        self.app.post('/api/categories', json={'category_name': 'Cat1'})
        invalid_names = ["<script>", "item/slash", "item$"]
        for name in invalid_names:
            response = self.app.post('/api/categories/Cat1/items', json={'item_name': name})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b"Invalid item_name", response.data)

if __name__ == '__main__':
    unittest.main()
