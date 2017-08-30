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

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_shoppinglist_creation(self):
        """ Test API can create a shopping list, POST"""
        response = self.client().post('/shoppinglists/', data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Back to', str(response.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get a shoppinglist, GET """
        response = self.client().post('/shoppinglists/', data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        response = self.client().get('/shoppinglists/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_api_can_get_shoppinglist_by_id(self):
        """Test API can get a single shoppinglist by using it's id, GET"""
        response = self.client().post('/shoppinglists/', data=self.shoppinglist)
        self.assertEqual(response.status_code, 201)
        result_in_json = json.loads(response.data.decode('utf-8').replace("'", "\""))
        response = self.client().get('/shoppinglists/{}'.format(result_in_json['id']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist, PUT"""
        response = self.client().post('/shoppinglists/', data={'name':'Easter shopping'})
        self.assertEqual(response.status_code, 201)
        response = self.client().put('/shoppinglists/1', data={'name':'Christmass shopping'})
        self.assertEqual(response.status_code, 200)
        res = self.client().get('/shoppinglists/1')
        self.assertIn('Christmass', str(res.data))

    def test_shoppinglist_deletion(self):
        """ Test API can delete a shopping list, DELETE"""
        response = self.client().post('/shoppinglists/', data={'name':'Easter shopping'})
        self.assertEqual(response.status_code, 201)
        response = self.client().delete('/shoppinglists/1')
        self.assertEqual(response.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/shoppinglists/1')
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
