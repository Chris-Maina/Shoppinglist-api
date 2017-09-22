""" test_shoppinglist.py """
import unittest
import json
from app import create_app, db


class ShoppinglistTestCase(unittest.TestCase):
    """This class represents the shoppinglist test case"""

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

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self):
        """Registers a user"""
        return self.client().post('/auth/register/', data=self.user_details)

    def login_user(self):
        """Registers a user"""
        return self.client().post('/auth/login/', data=self.user_details)

    def test_shoppinglist_creation(self):
        """ Test API can create a shopping list, POST"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_invalid_limit(self):
        """ Test invalid limit value provided, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # Limit the request
        response = self.client().get("/shoppinglists/?limit=one",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid limit value", str(response.data))

    def test_shoppinglist_negative_limit_provided(self):
        """ Test negative limit value provided, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # Limit the request
        response = self.client().get("/shoppinglists/?limit=-1",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppinglist_invalid_page(self):
        """ Test invalid page number provided, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # provide limit and page
        response = self.client().get("/shoppinglists/?limit=1&page=one",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid page", str(response.data))

    def test_shoppinglist_negative_page_number_provided(self):
        """ Test negative page number provided, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # provide limit and page
        response = self.client().get("/shoppinglists/?limit=1&page=-1",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppinglist_search(self):
        """ Test API can search a shopping list, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # Search shopping list
        response = self.client().get("/shoppinglists/?q=Back",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn("to school", str(response.data))

    def test_search_shoppinglist_name(self):
        """ Test API can search a non-existing shopping list, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # Search shopping list
        response = self.client().get("/shoppinglists/?q=Hike",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 404)
        self.assertIn("name does not exist", str(response.data))

    def test_api_can_get_shoppinglists(self):
        """Test API can get a shoppinglist, GET """
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        response = self.client().get(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get all shoppinglist, GET """
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        response = self.client().get(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_list_creation_no_name(self):
        """ Test API gives an error when no name is supplied """
        item = {'name': ''}
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=item)
        self.assertEqual(response.status_code, 400)
        self.assertIn("enter a shopping list", str(response.data))

    def test_list_creation_twice(self):
        """ Test API gives an error when an existing list name is supplied """
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        # create second shopping list
        response2 = self.client().post('/shoppinglists/',
                                       headers=dict(
                                           Authorization="Bearer " + access_token),
                                       data=self.shoppinglist)
        self.assertEqual(response2.status_code, 302)
        self.assertIn("List name already exists", str(response2.data))

    def test_api_can_get_list_by_id(self):
        """Test API can get a single shoppinglist by using it's id, GET"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        result_in_json = json.loads(
            response.data.decode('utf-8').replace("'", "\""))
        response = self.client().get(
            '/shoppinglists/{}'.format(result_in_json['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist, PUT"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket
        response = self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Easter shopping'})
        self.assertEqual(response.status_code, 201)
        response = self.client().put(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Christmass shopping'})
        self.assertEqual(response.status_code, 200)
        res = self.client().get('/shoppinglists/1',
                                headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Christmass', str(res.data))

    def test_shoppinglist_deletion(self):
        """ Test API can delete a shopping list, DELETE"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket
        response = self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Easter shopping'})
        self.assertEqual(response.status_code, 201)
        response = self.client().delete(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/shoppinglists/1',
                                   headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
