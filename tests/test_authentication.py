""" /tests/test_authentication.py"""
import json
from tests.basetest import BaseTest


class UserTestCases(BaseTest):
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

    def test_success_registration(self):
        """ Test if registration works"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertIn(
            "You have been registered successfully. Please login", str(res.data))

    def test_user_registration_twice(self):
        """ Test user registration twice"""
        self.client().post('/auth/register/', data=self.user_details)
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertIn(
            "User already exists", str(res.data))

    def test_invalid_email_provided(self):
        """ Test invalid email provided"""
        res = self.client().post('/auth/register/', data={'email': 'mainachris@gmail',
                                                          'password': 'pass123'})
        self.assertIn(
            "provide a valid email", str(res.data))

    def test_no_email_provided(self):
        """Test no email provided"""
        res = self.client().post('/auth/register/',
                                 data={'email': '', 'password': 'pass123'})
        self.assertIn(
            "provide a valid email", str(res.data))

    def test_no_password_provided(self):
        """Test no password provided"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': ''})
        self.assertIn(
            "password should be atleast 6 characters", str(res.data))

    def test_password_length(self):
        """Test password length"""
        res = self.client().post('/auth/register/',
                                 data={'email': 'mainachris@gmail.com', 'password': 'pass'})
        self.assertIn(
            "password should be atleast 6 characters", str(res.data))

    def test_register_get_method(self):
        """Test Get method in login"""
        res = self.client().get('/auth/register/')
        self.assertIn("To register", str(res.data))

    def test_user_login(self):
        """Test user can login after registration"""
        res = self.client().post('/auth/register/', data=self.user_details)
        login_res = self.client().post('/auth/login/', data=self.user_details)
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

    def test_login_no_password(self):
        """Test no email provided when login"""
        res = self.client().post('/auth/register/', data=self.user_details)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login/', data={
            'email': 'mainachris@gmail.com',
            'password': ''
        })
        self.assertIn("Please fill password", str(login_res.data))

    def test_login_get_method(self):
        """Test Get method in login"""
        login_res = self.client().get('/auth/login/')
        self.assertIn("To login", str(login_res.data))

    def test_login_non_existent_user(self):
        """Tests user login with non existent email&password"""
        user_details = {
            'email': "test@gmail.com",
            'password': "testpassword"
        }
        res = self.client().post('/auth/login/', data=user_details)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'],
                         "Invalid email or password, Please try again")

    def test_get_user_profile(self):
        """ Test loading of user profile"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # Get user profile
        res = self.client().get('/user',
                                headers=dict(
                                    Authorization="Bearer " + access_token))
        self.assertIn("test@gmail.com", str(res.data))

    def test_update_user_profile(self):
        """ Test update user profile"""
        user_details = {
            'email': "test@gmail.com",
            'password': "testpassword"
        }
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # Update user profile
        res = self.client().put('/user',
                                headers=dict(
                                    Authorization="Bearer " + access_token),
                                data=user_details)
        self.assertIn("Successfully updated profile", str(res.data))

    def test_update_short_password(self):
        """ Test update user profile short password supplied"""
        user_details = {
            'email': "test@gmail.com",
            'password': "test"
        }
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # Update user profile
        res = self.client().put('/user',
                                headers=dict(
                                    Authorization="Bearer " + access_token),
                                data=user_details)
        self.assertIn("password should be atleast 6 characters long", str(res.data))

    def test_update_invalid_email(self):
        """ Test update user profile invalid email"""
        user_details = {
            'email': "test@gmail.com.com",
            'password': "testpassword"
        }
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # Update user profile
        res = self.client().put('/user',
                                headers=dict(
                                    Authorization="Bearer " + access_token),
                                data=user_details)
        self.assertIn("Please provide a valid email address", str(res.data))

    def test_get_reset_token(self):
        """ Test successful get reset token"""
        user_email = {
            'email': "test@gmail.com"
            }
        self.register_user()
        res=self.client().post('/user/reset', data=user_email)
        self.assertEqual(res.status_code, 200)

    def test_get_reset_token_unregistered_user(self):
        """ Test unsuccessful get reset token"""
        user_email = {
            'email': "chris@gmail.com"
            }
        self.register_user()
        res=self.client().post('/user/reset', data=user_email)
        self.assertEqual(res.status_code, 400)

    def test_get_reset_token_no_email_provided(self):
        """ Test get reset token no email provided"""
        self.register_user()
        res=self.client().post('/user/reset')
        self.assertIn("Please fill email field", str(res.data))

    def test_reset_password(self):
        """ Test reset password"""
        user_email = {
            'email': "test@gmail.com"
            }
        user_password = {
            'password': "testpassword"
            }
        self.register_user()
        res=self.client().post('/user/reset', data=user_email)
        # Get reset access token
        result = json.loads(res.data.decode())
        response=self.client().put('/user/reset/password/{}'.format(result['reset_token']), data=user_password)
        self.assertEqual(response.status_code, 200)

    def test_reset_with_short_password(self):
        """ Test reset password"""
        user_email = {
            'email': "test@gmail.com"
            }
        user_password = {
            'password': "test"
            }
        self.register_user()
        res=self.client().post('/user/reset', data=user_email)
        # Get reset access token
        result = json.loads(res.data.decode())
        # test
        response=self.client().put('/user/reset/password/{}'.format(result['reset_token']), data=user_password)
        self.assertIn("password should be atleast 6 characters", str(response.data))
        
