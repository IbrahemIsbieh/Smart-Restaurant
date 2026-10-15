from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRestaurantPayment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        category = cls.env["restaurant.category"].create({
            "name": "Payment Test Category",
        })

        item = cls.env["restaurant.menu.item"].create({
            "name": "Payment Test Meal",
            "category_id": category.id,
            "sale_price": 10.0,
        })

        table = cls.env["restaurant.table"].create({
            "name": "Payment Test Table",
            "capacity": 4,
        })

        cls.order = cls.env["restaurant.order"].create({
            "order_type": "dine_in",
            "table_id": table.id,
        })

        cls.env["restaurant.order.line"].create({
            "order_id": cls.order.id,
            "menu_item_id": item.id,
            "quantity": 1,
            "price_unit": 10.0,
        })

        cls.order.action_confirm()

    def test_post_payment(self):
        payment = self.env["restaurant.payment"].create({
            "order_id": self.order.id,
            "amount": 4.0,
            "payment_method": "cash",
        })

        payment.action_post()

        self.assertEqual(payment.state, "posted")
        self.assertEqual(self.order.amount_paid, 4.0)
        self.assertEqual(self.order.amount_due, 6.0)

    def test_overpayment_is_rejected(self):
        payment = self.env["restaurant.payment"].create({
            "order_id": self.order.id,
            "amount": 11.0,
            "payment_method": "card",
        })

        with self.assertRaises(UserError):
            payment.action_post()