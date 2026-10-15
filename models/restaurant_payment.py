from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RestaurantPayment(models.Model):
    _name = "restaurant.payment"
    _description = "Restaurant Payment"
    _order = "date desc, id desc"

    order_id = fields.Many2one(
        comodel_name="restaurant.order",
        string="Order",
        required=True,
        ondelete="restrict",
    )

    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id",
        store=True,
        readonly=True,
    )

    payment_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("card", "Card"),
        ],
        string="Payment Method",
        required=True,
        default="cash",
    )

    date = fields.Datetime(
        string="Payment Date",
        required=True,
        default=fields.Datetime.now,
    )

    reference = fields.Char(
        string="Reference",
        copy=False,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        default="draft",
    )

    @api.constrains("amount")
    def _check_amount(self):
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(
                    _("Payment amount must be greater than zero.")
                )

    def action_post(self):
        for payment in self:
            if payment.state != "draft":
                raise UserError(
                    _("Only draft payments can be posted.")
                )

            if payment.order_id.state in ("draft", "cancelled"):
                raise UserError(
                    _("Payments require a confirmed, active order.")
                )

            if payment.amount > payment.order_id.amount_due:
                raise UserError(
                    _("The payment exceeds the remaining amount due.")
                )

            payment.state = "posted"

    def action_cancel(self):
        for payment in self:
            if payment.state == "posted":
                raise UserError(
                    _(
                        "Posted payments cannot be cancelled directly. "
                        "A refund or reversal workflow is required."
                    )
                )

            payment.state = "cancelled"