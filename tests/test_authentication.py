""" /tests/test_authentication.py"""
import unittest
import json
from app import create_app, db


class UserTestCases(unittest.TestCase):
    """
    Test successful registration
    Test user registration twice
    Test invalid email provided
    Test no email/password provided
    Test password length
    Test successful user login
    Test user login with no email/password
    Test login GET method
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
            db.drop_all()
            db.create_all()

    def test_success_registration(self):
        """ Test if registration works"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        self.assertIn(
            "You have been registered successfully. Please login", str(res.data))

    def test_user_registration_twice(self):
        """ Test user registration twice"""
        self.client().post('/auth/register/', data=self.user_details)
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 202)
        self.assertIn(
            "User already exists", str(res.data))

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
        self.assertEqual(res.status_code, 403)
        self.assertIn(
            "provide a valid email", str(res.data))

    def test_no_password_provided(self):
        """Test no password provided"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': ''})
        self.assertEqual(res.status_code, 403)
        self.assertIn(
            "password should be atleast 6 characters", str(res.data))

    def test_password_length(self):
        """Test password length"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': 'pass'})
        self.assertEqual(res.status_code, 403)
        self.assertIn(
            "password should be atleast 6 characters", str(res.data))

    def test_register_get_method(self):
        """Test Get method in login"""
        res = self.client().get('/auth/register/')
        self.assertEqual(res.status_code, 200)
        self.assertIn("To register", str(res.data))

    def test_user_login(self):
        """Test user can login after registration"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login/', data=self.user_details)
        # Test response
        self.assertIn("You are logged in successfully", login_res.data)
        self.assertEqual(login_res.status_code, 200)
        # Get the response in json format
        result = json.loads(login_res.data.decode())
        self.assertTrue(result['access_token'])

    def test_login_no_email(self):
        """Test no email provided when login"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login/', data={
            'email': '',
            'password': 'password123'
        })
        self.assertIn("Please fill email", str(login_res.data))
        self.assertEqual(login_res.status_code, 400)

    def test_login_no_password(self):
        """Test no email provided when login"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login/', data={
            'email': 'mainachris@gmail.com',
            'password': ''
        })
        self.assertIn("Please fill password", str(login_res.data))
        self.assertEqual(login_res.status_code, 400)

    def test_login_get_method(self):
        """Test Get method in login"""
        login_res = self.client().get('/auth/login/')
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("To login", str(login_res.data))

    def test_login_non_existent_user(self):
        """Tests user login with non existent email&password"""
        user_details = {
            'email': "test@gmail.com",
            'password': "testpassword"
        }
        res = self.client().post('/auth/login/', data=user_details)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'],
                         "Invalid email or password, Please try again")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
