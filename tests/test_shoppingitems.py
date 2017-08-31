""" test_shoppingitems.py """
import unittest
import json
from app import create_app, db


class ShoppingItemsTestCases(unittest.TestCase):
    """
    """

    def setUp(self):
        """Define test env, test client and initialize them """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        # create a shoppinglist dictionary
        self.shoppinglist = {'name': 'Back to school'}

        # test user
        self.user_details = {
            'email': 'test@gmail.com',
            'password': 'password123'
        }

        # create a shopping item
        self.shoppingitem = {'name': 'Bread'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_login_user_create_shoppinglist(self):
        """Registers a user, login and create a shopping list"""
        # register user
        self.client().post('/auth/register/', data=self.user_details)

        # login user
        result = self.client().post('/auth/login/', data=self.user_details)

        # get token
        access_token = json.loads(result.data.decode())['access_token']

        # create a global access token variable
        self.access_token = access_token

        # create a shopping list
        return self.client().post("/shoppinglists/",
                                  headers=dict(
                                      Authorization="Bearer " + access_token),
                                  data=self.shoppinglist)

    def test_shoppingitem_creation(self):
        """ Test API can create a shopping item, POST"""
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items", headers=dict(Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        self.assertIn("Bread", str(res.data))

    def test_api_can_get_shoppingitems(self):
        """ Test API can get a shoppingitems, GET """
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items", headers=dict(Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # get all items
        response = self.client().get("/shoppinglists/1/items",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bread", str(response.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
