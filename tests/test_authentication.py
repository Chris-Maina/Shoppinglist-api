""" /tests/test_authentication.py"""
import unittest
import json
from app import create_app, db


class UserTestCases(unittest.TestCase):
    """
    Test successful registration
    Test invalid email provided
    Test no email/password provided
    Test password length
    Test user login
    Test user login with non existent email/password
    """

    def setUp(self):
        """Set up test env, test client and user"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        # test user
        self.user_details = {
            'email': 'mainachris@gmail.com',
            'password': 'password123'
        }

        with self.app.app_context():
            # create tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_success_registration(self):
        """ Test if registration works"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        self.assertIn(
            "You have been registered successfully. Please login", str(res.data))

    def test_invalid_email_provided(self):
        """ Test invalid email provided"""
        res = self.client().post('/auth/register/', data={'email': 'mainachris@gmail',
                                                          'password': 'pass123'})
        self.assertEqual(res.status_code, 403)
        self.assertIn(
            "provide a valid email", str(res.data))

    def test_no_email_provided(self):
        """Test no email provided"""
        res = self.client().post('/auth/register/',
                                 data={'email': '', 'password': 'pass123'})
        self.assertEqual(res.status_code, 400)
        self.assertIn(
            "Please fill email", str(res.data))
    
    def test_no_password_provided(self):
        """Test no password provided"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn(
            "Please fill password", str(res.data))

    def test_password_length(self):
        """Test password length"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': 'pass'})
        self.assertEqual(res.status_code, 403)
        self.assertIn(
            "password should be atleast 6 characters", str(res.data))

