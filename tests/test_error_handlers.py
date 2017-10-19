""" /tests/test_error_handlers.py"""
from tests.basetest import BaseTest


class ErrorHandlersTestCases(BaseTest):
    """
    Test 404
    Test 405
    Test 500
    """
    def test_404_error(self):
        """Tests 404 error"""
        res = self.client().get('/auth/register/kbnj')
        self.assertIn("not found", str(res.data))

    def test_405_error(self):
        """Test 405 error"""
        res = self.client().put('/auth/register/')
        self.assertIn("Method not allowed ", str(res.data))
