from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantOrderLine(models.Model):
    _name = "restaurant.order.line"
    _description = "Restaurant Order Line"
    _order = "id"

    order_id = fields.Many2one(
        comodel_name="restaurant.order",
        string="Order",
        required=True,
        ondelete="cascade",
    )

    menu_item_id = fields.Many2one(
        comodel_name="restaurant.menu.item",
        string="Menu Item",
        required=True,
        ondelete="restrict",
    )

    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
    )

    price_unit = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
        required=True,
    )

    discount = fields.Float(
        string="Discount (%)",
        default=0.0,
    )

    cost_unit = fields.Monetary(
        string="Unit Cost Snapshot",
        currency_field="currency_id",
        default=0.0,
        help="Cost snapshot at the time of the order.",
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id",
        store=True,
        readonly=True,
    )

    price_subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="currency_id",
        compute="_compute_price_subtotal",
        store=True,
    )

    @api.depends("quantity", "price_unit", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (
                line.quantity
                * line.price_unit
                * (1.0 - line.discount / 100.0)
            )

    @api.onchange("menu_item_id")
    def _onchange_menu_item_id(self):
        if self.menu_item_id:
            self.price_unit = self.menu_item_id.sale_price

    @api.constrains("quantity", "price_unit", "discount", "cost_unit")
    def _check_line_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    "Order quantity must be greater than zero."
                )

            if line.price_unit < 0 or line.cost_unit < 0:
                raise ValidationError(
                    "Price and cost cannot be negative."
                )

            if not 0 <= line.discount <= 100:
                raise ValidationError(
                    "Discount must be between 0 and 100 percent."
                )