from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRestaurantOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = cls.env["restaurant.category"].create({
            "name": "Order Test Category",
        })

        cls.item = cls.env["restaurant.menu.item"].create({
            "name": "Order Test Meal",
            "category_id": cls.category.id,
            "sale_price": 5.0,
        })

        cls.table = cls.env["restaurant.table"].create({
            "name": "Test Table 01",
            "capacity": 4,
        })

    def _create_order(self):
        order = self.env["restaurant.order"].create({
            "order_type": "dine_in",
            "table_id": self.table.id,
        })

        self.env["restaurant.order.line"].create({
            "order_id": order.id,
            "menu_item_id": self.item.id,
            "quantity": 2,
            "price_unit": 5.0,
        })

        return order

    def test_create_and_confirm_order(self):
        order = self._create_order()

        self.assertEqual(order.state, "draft")
        self.assertEqual(order.amount_total, 10.0)

        order.action_confirm()

        self.assertEqual(order.state, "confirmed")

    def test_confirm_empty_order_is_rejected(self):
        order = self.env["restaurant.order"].create({
            "order_type": "dine_in",
            "table_id": self.table.id,
        })

        with self.assertRaises(UserError):
            order.action_confirm()

    def test_dine_in_requires_table(self):
        with self.assertRaises(ValidationError):
            self.env["restaurant.order"].create({
                "order_type": "dine_in",
            })

    def test_order_workflow(self):
        order = self._create_order()

        order.action_confirm()
        order.action_start_preparing()
        order.action_mark_ready()
        order.action_serve()

        self.assertEqual(order.state, "served")