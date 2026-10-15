from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRestaurantStock(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = cls.env["restaurant.category"].create({
            "name": "Stock Test Category",
        })

        cls.menu_item = cls.env["restaurant.menu.item"].create({
            "name": "Stock Test Meal",
            "category_id": cls.category.id,
            "sale_price": 4.0,
        })

        template = cls.env["product.template"].create({
            "name": "Test Burger Bun",
            "type": "consu",
        })

        cls.ingredient = template.product_variant_id

    def test_create_recipe_ingredient(self):
        recipe_line = self.env["restaurant.recipe.line"].create({
            "menu_item_id": self.menu_item.id,
            "product_id": self.ingredient.id,
            "quantity": 1.0,
        })

        self.assertEqual(recipe_line.menu_item_id, self.menu_item)
        self.assertEqual(recipe_line.product_id, self.ingredient)
        self.assertEqual(recipe_line.quantity, 1.0)

    def test_zero_ingredient_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["restaurant.recipe.line"].create({
                "menu_item_id": self.menu_item.id,
                "product_id": self.ingredient.id,
                "quantity": 0,
            })