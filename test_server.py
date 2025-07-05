import unittest

from server import app


class MyTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status, "200 OK")
