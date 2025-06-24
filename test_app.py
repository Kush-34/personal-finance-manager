"""
test_app.py
-----------
Unit tests for the Personal Finance Management Application.
"""

import unittest
from database import Database

class TestFinanceApp(unittest.TestCase):

    def setUp(self):
        # Use in-memory database for testing
        self.db = Database(':memory:')
        self.db.register_user('testuser', 'pass')

    def test_user_registration(self):
        # Duplicate username should fail
        self.assertFalse(self.db.register_user('testuser', 'pass'))

    def test_authentication(self):
        user_id = self.db.authenticate_user('testuser', 'pass')
        self.assertIsNotNone(user_id)

    def test_add_transaction(self):
        user_id = self.db.authenticate_user('testuser', 'pass')
        self.db.add_transaction(user_id, 100, 'Salary', 'income')
        self.db.add_transaction(user_id, 50, 'Food', 'expense')

    def test_budget(self):
        user_id = self.db.authenticate_user('testuser', 'pass')
        self.db.set_budget(user_id, 'Food', 100)
        self.db.add_transaction(user_id, 120, 'Food', 'expense')  # Should warn

if __name__ == '__main__':
    unittest.main()
