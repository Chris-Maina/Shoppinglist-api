""" test_shoppinglist.py """
import json
from tests.basetest import BaseTest


class ShoppinglistTestCase(BaseTest):
    """This class represents the shoppinglist test case"""

    def test_shoppinglist_creation(self):
        """ Test API can create a shopping list, POST"""
        # create a shoppinglist
        response = self.test_shoppinglist()
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_invalid_limit(self):
        """ Test invalid limit value provided, GET"""
        # create a shoppinglist
        response = self.test_shoppinglist()
        # Limit the request
        response = self.client().get("/shoppinglists/?limit=one",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Invalid limit value", str(response.data))

    def test_shoppinglist_negative_limit_provided(self):
        """ Test negative limit value provided, GET"""
        # create a shoppinglist
        response = self.test_shoppinglist()
        # Limit the request
        response = self.client().get("/shoppinglists/?limit=-1",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppinglist_invalid_page(self):
        """ Test invalid page number provided, GET"""
        # create a shoppinglist
        response = self.test_shoppinglist()
        # provide limit and page
        response = self.client().get("/shoppinglists/?limit=1&page=one",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Invalid page", str(response.data))

    def test_shoppinglist_negative_page_number_provided(self):
        """ Test negative page number provided, GET"""
        # create a shoppinglist
        self.test_shoppinglist()
        # provide limit and page
        response = self.client().get("/shoppinglists/?limit=1&page=-1",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppinglist_search(self):
        """ Test API can search a shopping list, GET"""
        # create a shoppinglist
        self.test_shoppinglist()
        # Search shopping list
        response = self.client().get("/shoppinglists/?q=Back",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("to school", str(response.data))

    def test_search_shoppinglist_name(self):
        """ Test API can search a non-existing shopping list, GET"""
        # create a shoppinglist
        self.test_shoppinglist()
        # Search shopping list
        response = self.client().get("/shoppinglists/?q=Hike",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("name does not exist", str(response.data))

    def test_api_can_get_shoppinglists(self):
        """Test API can get all shoppinglist, GET """
        # create a shoppinglist
        self.test_shoppinglist()
        response = self.client().get(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + self.access_token))
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
        self.assertIn("enter a shopping list", str(response.data))

    def test_list_creation_special_characters(self):
        """ Test API gives an error when name has special characters """
        item = {'name': 'Graduation party!'}
        # Register,login user and get access token
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist
        response = self.client().post('/shoppinglists/',
                                      headers=dict(
                                          Authorization="Bearer " + access_token),
                                      data=item)
        self.assertIn("No special characters", str(response.data))

    def test_list_creation_twice(self):
        """ Test API gives an error when an existing list name is supplied """
        # create a shoppinglist
        self.test_shoppinglist()
        # create second shopping list with same name
        response2 = self.test_shoppinglist()
        self.assertIn("List name already exists", str(response2.data))

    def test_api_can_get_list_by_id(self):
        """Test API can get a single shoppinglist by using it's id, GET"""

        # create a shoppinglist
        response = self.test_shoppinglist()

        result_in_json = json.loads(
            response.data.decode('utf-8').replace("'", "\""))
        # Get specific shopping list by id
        response = self.client().get(
            '/shoppinglists/{}'.format(result_in_json['id']),
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn('Back to', str(response.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist, PUT"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shopping list
        self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Easter shopping'})
        self.client().put(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Christmass shopping'})
        res = self.client().get('/shoppinglists/1',
                                headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Christmass', str(res.data))

    def test_shoppinglist_edit_with_special_characters(self):
        """Test API can gives error when name has special characters, PUT"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shopping list
        self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Easter shopping'})
        response = self.client().put(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Christmass shopping+'})
        self.assertIn('No special characters', str(response.data))

    def test_shoppinglist_deletion(self):
        """ Test API can delete a shopping list, DELETE"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shopping list
        self.client().post(
            '/shoppinglists/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Easter shopping'})
        self.client().delete(
            '/shoppinglists/1', headers=dict(Authorization="Bearer " + access_token))
        # Test to see if it exists, should return a 404
        result = self.client().get('/shoppinglists/1',
                                   headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)
