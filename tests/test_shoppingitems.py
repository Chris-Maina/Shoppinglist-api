""" test_shoppingitems.py """
from tests.basetest import BaseTest


class ShoppingItemsTestCases(BaseTest):
    """Test cases for shopping items
    """

    def test_shoppingitem_creation(self):
        """ Test API can create a shopping item, POST"""
        # create an item
        res = self.test_shoppingitem()
        self.assertIn("Bread", str(res.data))

    def test_shoppingitem_invalid_page(self):
        """ Test invalid page number provided, GET"""
        # create an item
        self.test_shoppingitem()
        # limit request, provide page
        response = self.client().get("/shoppinglists/1/items?limit=1&page=one",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Invalid page", str(response.data))

    def test_shoppingitem_negative_page_provided(self):
        """ Test negative page number provided, GET"""
        # create an item
        self.test_shoppingitem()
        # limit request, provide page
        response = self.client().get("/shoppinglists/1/items?limit=1&page=-1",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppingitem_invalid_limit(self):
        """ Test invalid limit value provided, GET"""
        # create an item
        self.test_shoppingitem()
        # limit request
        response = self.client().get("/shoppinglists/1/items?limit=one",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Invalid limit value", str(response.data))

    def test_shoppingitem_negative_limit(self):
        """ Test negative limit value provided, GET"""
        # create an item
        self.test_shoppingitem()
        # limit request
        response = self.client().get("/shoppinglists/1/items?limit=-1",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("must be a positive integer", str(response.data))

    def test_shoppingitem_search(self):
        """ Test API can search a shopping item, GET"""
        # create an item
        self.test_shoppingitem()
        # Search item
        response = self.client().get("/shoppinglists/1/items?q=Br",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Bread", str(response.data))

    def test_shoppingitem_search_non_existing_item(self):
        """ Test API can search a non existing shopping item, GET"""
        # create an item
        self.test_shoppingitem()
        # Search item
        response = self.client().get("/shoppinglists/1/items?q=Jui",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("item name does not exist", str(response.data))

    def test_api_can_get_shoppingitems(self):
        """ Test API can get a shoppingitems, GET """
        # create an item
        res = self.test_shoppingitem()
        self.assertEqual(res.status_code, 201)
        # get all items
        response = self.client().get("/shoppinglists/1/items",
                                     headers=dict(Authorization="Bearer " + self.access_token))
        self.assertIn("Bread", str(response.data))

    def test_item_creation_twice(self):
        """ Test API gives an error on item creation twice """
        # create an item
        res = self.test_shoppingitem()
        # create the same item twice
        res2 = self.client().post("/shoppinglists/1/items",
                                  headers=dict(
                                      Authorization="Bearer " + self.access_token),
                                  data=self.shoppingitem)
        self.assertIn("Item name already exists", str(res2.data))

    def test_item_creation_no_name(self):
        """ Test API gives an error when no name is supplied """
        item = {'name': '', 'price': '50', 'quantity': '10'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("provide an item name", str(res.data))

    def test_item_creation_no_price(self):
        """ Test API gives an error when no price is supplied """
        item = {'name': 'Juice', 'price': '', 'quantity': '10'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("provide a price value", str(res.data))

    def test_item_creation_no_quantity(self):
        """ Test API gives an error when no quantity is supplied """
        item = {'name': 'Juice', 'price': '60', 'quantity': ''}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("provide a quantity value", str(res.data))

    def test_item_creation_negative_quantity(self):
        """ Test API gives an error when negative quantity is supplied """
        item = {'name': 'Juice', 'price': '60', 'quantity': '-2'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("must be a positive integer", str(res.data))

    def test_item_creation_negative_price(self):
        """ Test API gives an error when negative price is supplied """
        item = {'name': 'Juice', 'price': '-60', 'quantity': '2'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("must be a positive integer", str(res.data))

    def test_item_creation_invalid_price(self):
        """ Test API gives an error when invalid price is supplied """
        item = {'name': 'Juice', 'price': 'one', 'quantity': '2'}
        # create a shopping list
        res = self.test_shoppinglist()
        self.assertEqual(res.status_code, 201)
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid price value", str(res.data))

    def test_item_creation_invalid_quantity(self):
        """ Test API gives an error when invalid quantity is supplied """
        item = {'name': 'Juice', 'price': '60', 'quantity': 'one'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("Invalid quantity value", str(res.data))

    def test_item_creation_with_special_characters(self):
        """ Test API gives an error when name has special characters """
        item = {'name': 'Jeep+', 'price': '1000', 'quantity': '10'}
        # create a shopping list
        res = self.test_shoppinglist()
        # create an item
        res = self.client().post("/shoppinglists/1/items",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("No special characters", str(res.data))

    def test_api_can_edit_item(self):
        """ Test API can edit an existing item """
        item = {'name': 'sugar'}
        # create an item
        res = self.test_shoppingitem()
        # edit item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("sugar", str(res2.data))

    def test_api_can_edit_non_existing_item(self):
        """ Test API can edit a non existing item """
        item = {'name': 'sugar'}
        # create a shoppinglist
        res = self.test_shoppinglist()
        # edit non-existing item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("No such item", str(res2.data))

    def test_api_edit_with_special_characters(self):
        """ Test API cannot edit with item name having special characters """
        item = {'name': 'Bread!'}
        # create an item
        res = self.test_shoppingitem()
        # edit item
        res2 = self.client().put("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token),
                                 data=item)
        self.assertIn("No special characters", str(res2.data))

    def test_api_can_delete_item(self):
        """ Test API can delete an item """
        # create an item
        res = self.test_shoppingitem()
        # delete item
        res2 = self.client().delete("/shoppinglists/1/items/1",
                                    headers=dict(
                                        Authorization="Bearer " + self.access_token))
        self.assertIn("Bread", str(res2.data))

    def test_api_can_delete_non_existing_item(self):
        """ Test API cannot delete non existing item """
        # create a shoppinglist
        self.test_shoppinglist()
        # delete item
        res2 = self.client().delete("/shoppinglists/1/items/1",
                                    headers=dict(
                                        Authorization="Bearer " + self.access_token))
        self.assertIn("No such item", str(res2.data))

    def test_api_can_get_item(self):
        """ Test API can get an item """
        # create an item
        res = self.test_shoppingitem()
        # get item
        res2 = self.client().get("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token))
        self.assertIn("Bread", str(res2.data))

    def test_api_can_get_non_existing_item(self):
        """ Test API cannot get non existing item """
        # create a shoppinglist
        self.test_shoppinglist()
        # delete item
        res2 = self.client().get("/shoppinglists/1/items/1",
                                 headers=dict(
                                     Authorization="Bearer " + self.access_token))
        self.assertIn("No such item", str(res2.data))
