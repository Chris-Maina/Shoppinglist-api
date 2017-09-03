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
        response = self.client().post('/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_search(self):
        """ Test API can search a shopping list, GET"""
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
                                      data=self.shoppinglist)
        # Search shopping list
        response = self.client().get("/shoppinglists/?q=Back",
                                     headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn("to school", str(response.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get a shoppinglist, GET """
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(Authorization="Bearer " + access_token), data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        response = self.client().get(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_api_can_get_shoppinglist_by_id(self):
        """Test API can get a single shoppinglist by using it's id, GET"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket
        response = self.client().post('/shoppinglists/',
                                      headers=dict(Authorization="Bearer " + access_token), data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        result_in_json = json.loads(
            response.data.decode('utf-8').replace("'", "\""))
        response = self.client().get(
            '/shoppinglists/{}'.format(result_in_json['id']), headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist, PUT"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket
        response = self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token), data={'name': 'Easter shopping'})
        self.assertEqual(response.status_code, 201)
        response = self.client().put(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token), data={'name': 'Christmass shopping'})
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
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token), data={'name': 'Easter shopping'})
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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
