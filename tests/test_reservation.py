from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRestaurantReservation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer = cls.env["res.partner"].create({
            "name": "Reservation Test Customer",
        })

        cls.table = cls.env["restaurant.table"].create({
            "name": "Reservation Test Table",
            "capacity": 4,
        })

        cls.start = fields.Datetime.to_datetime(
            "2026-11-01 12:00:00"
        )
        cls.end = fields.Datetime.to_datetime(
            "2026-11-01 13:00:00"
        )

    def _reservation_values(self):
        return {
            "partner_id": self.customer.id,
            "table_id": self.table.id,
            "date_start": self.start,
            "date_end": self.end,
            "guest_count": 2,
        }

    def test_create_and_confirm_reservation(self):
        reservation = self.env["restaurant.reservation"].create(
            self._reservation_values()
        )

        self.assertEqual(reservation.state, "draft")

        reservation.action_confirm()

        self.assertEqual(reservation.state, "confirmed")

    def test_overlapping_reservation_is_rejected(self):
        self.env["restaurant.reservation"].create(
            self._reservation_values()
        )

        overlapping_values = self._reservation_values()
        overlapping_values.update({
            "date_start": fields.Datetime.to_datetime(
                "2026-11-01 12:30:00"
            ),
            "date_end": fields.Datetime.to_datetime(
                "2026-11-01 13:30:00"
            ),
        })

        with self.assertRaises(ValidationError):
            self.env["restaurant.reservation"].create(
                overlapping_values
            )

    def test_guest_count_cannot_exceed_capacity(self):
        values = self._reservation_values()
        values["guest_count"] = 5

        with self.assertRaises(ValidationError):
            self.env["restaurant.reservation"].create(values)