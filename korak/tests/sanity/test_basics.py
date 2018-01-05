import unittest
from flask import current_app
from app import create_app

# =============================

class BasicsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.db.create_all()
    # _____________________________

    def tearDown(self):
        self.app.db.drop_all()
        self.app_context.pop()
    # _____________________________

    def test_app_exists(self):
        self.assertFalse(current_app is None)
    # _____________________________

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
