""" basetest.py """
import unittest
import json
from app import create_app, db


class BaseTest(unittest.TestCase):
    """This class represents the base test for all test files"""

    def setUp(self):
        """Define test env, test client and initialize them """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        # create test shoppinglist
        self.shoppinglist = {'name': 'Back to school'}

        # test user
        self.user_details = {
            'email': 'test@gmail.com',
            'password': 'password123'
        }

        # create test shopping item
        self.shoppingitem = {'name': 'Bread'}

        # access token
        self.access_token = None

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self):
        """Registers a user"""
        return self.client().post('/auth/register/', data=self.user_details)

    def login_user(self):
        """Login a user"""
        return self.client().post('/auth/login/', data=self.user_details)

    def test_shoppinglist(self):
        """ Test API can create a shopping list, POST"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        self.access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        return self.client().post('/shoppinglists/',
                                  headers=dict(
                                      Authorization="Bearer " + self.access_token),
                                  data=self.shoppinglist)

    def test_shoppingitem(self):
        """ Test API can create a shopping item, POST"""
        res = self.test_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        return self.client().post("/shoppinglists/1/items",
                                  headers=dict(
                                      Authorization="Bearer " + self.access_token),
                                  data=self.shoppingitem)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
