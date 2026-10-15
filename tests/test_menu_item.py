from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRestaurantMenuItem(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = cls.env["restaurant.category"].create({
            "name": "Test Meals",
        })

    def test_create_menu_item(self):
        item = self.env["restaurant.menu.item"].create({
            "name": "Test Burger",
            "category_id": self.category.id,
            "sale_price": 3.50,
        })

        self.assertEqual(item.name, "Test Burger")
        self.assertEqual(item.sale_price, 3.50)
        self.assertTrue(item.active)

    def test_negative_sale_price_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["restaurant.menu.item"].create({
                "name": "Invalid Item",
                "category_id": self.category.id,
                "sale_price": -1.0,
            })