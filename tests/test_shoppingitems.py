""" test_shoppingitems.py """
import unittest
import json
from app import create_app, db


class ShoppingItemsTestCases(unittest.TestCase):
    """Test cases for shopping items
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
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        self.assertIn("Bread", str(res.data))

    def test_shoppingitem_search(self):
        """ Test API can search a shopping item, GET"""
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        # Search item
        response = self.client().get("/shoppinglists/1/items?q=Br",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bread", str(response.data))

    def test_api_can_get_shoppingitems(self):
        """ Test API can get a shoppingitems, GET """
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # get all items
        response = self.client().get("/shoppinglists/1/items",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bread", str(response.data))

    def test_item_creation_twice(self):
        """ Test API gives an error on item creation twice """
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        res2 = self.client().post("/shoppinglists/1/items",
                                  headers=dict(
                                      Authorization="Bearer " + self.access_token),
                                  data=self.shoppingitem)
        self.assertEqual(res2.status_code, 302)
        self.assertIn("Item name already exists", str(res2.data))

    def test_item_creation_no_name(self):
        """ Test API gives an error when no name is supplied """
        item = {'name': ''}
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertEqual(res.status_code, 400)
        self.assertIn("provide an item name", str(res.data))

    def test_api_can_edit_item(self):
        """ Test API can edit an existing item """
        item = {'name': 'sugar'}
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # edit item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertEqual(res2.status_code, 200)
        self.assertIn("sugar", str(res2.data))

    def test_api_can_edit_non_existing_item(self):
        """ Test API can edit a non existing item """
        item = {'name': 'sugar'}
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # edit non-existing item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertEqual(res2.status_code, 404)
        self.assertIn("No such item", str(res2.data))

    def test_api_edit_no_name(self):
        """ Test API cannot edit with no item name provided """
        item = {'name': ''}
        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # edit item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertEqual(res2.status_code, 400)
        self.assertIn("enter an item name", str(res2.data))

    def test_api_can_delete_item(self):
        """ Test API can delete an item """

        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # delete item
        res2 = self.client().delete("/shoppinglists/1/items/1",
                                    headers=dict(
                                        Authorization="Bearer " + self.access_token))
        self.assertEqual(res2.status_code, 200)
        self.assertIn("Bread", str(res2.data))

    def test_api_can_delete_non_existing_item(self):
        """ Test API cannot delete non existing item """

        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # delete item
        res2 = self.client().delete("/shoppinglists/1/items/1",
                                    headers=dict(
                                        Authorization="Bearer " + self.access_token))
        self.assertEqual(res2.status_code, 404)
        self.assertIn("No such item", str(res2.data))

    def test_api_can_get_item(self):
        """ Test API can get an item """

        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=self.shoppingitem)
        self.assertEqual(res.status_code, 201)
        # get item
        res2 = self.client().get("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token))
        self.assertEqual(res2.status_code, 200)
        self.assertIn("Bread", str(res2.data))

    def test_api_can_get_non_existing_item(self):
        """ Test API cannot get non existing item """

        res = self.register_login_user_create_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # delete item
        res2 = self.client().get("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token))
        self.assertEqual(res2.status_code, 404)
        self.assertIn("No such item", str(res2.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
