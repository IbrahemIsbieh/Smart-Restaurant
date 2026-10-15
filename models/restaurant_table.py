from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantTable(models.Model):
    _name = "restaurant.table"
    _description = "Restaurant Table"
    _order = "name"

    name = fields.Char(
        string="Table Name",
        required=True,
    )

    capacity = fields.Integer(
        string="Capacity",
        required=True,
        default=4,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    reservation_ids = fields.One2many(
        comodel_name="restaurant.reservation",
        inverse_name="table_id",
        string="Reservations",
    )

    @api.constrains("capacity")
    def _check_capacity(self):
        for table in self:
            if table.capacity <= 0:
                raise ValidationError(
                    "Table capacity must be greater than zero."
                )

    _table_name_unique = models.Constraint(
        "UNIQUE(name)",
        "Table names must be unique.",
    )