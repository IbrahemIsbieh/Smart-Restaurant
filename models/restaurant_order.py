from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RestaurantOrder(models.Model):
    _name = "restaurant.order"
    _description = "Restaurant Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_order desc, id desc"

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )

    order_type = fields.Selection(
        [
            ("dine_in", "Dine In"),
            ("takeaway", "Takeaway"),
            ("delivery", "Delivery"),
        ],
        string="Order Type",
        required=True,
        default="dine_in",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("preparing", "Preparing"),
            ("ready", "Ready"),
            ("served", "Served"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        default="draft",
        tracking=True,
    )

    date_order = fields.Datetime(
        string="Order Date",
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        tracking=True,
        ondelete="restrict",
    )

    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Delivery Address",
        ondelete="restrict",
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        required=True,
    )

    table_id = fields.Many2one(
        comodel_name="restaurant.table",
        string="Table",
        ondelete="restrict",
    )

    order_line_ids = fields.One2many(
        comodel_name="restaurant.order.line",
        inverse_name="order_id",
        string="Order Lines",
        copy=True,
    )

    payment_ids = fields.One2many(
        comodel_name="restaurant.payment",
        inverse_name="order_id",
        string="Payments",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )

    amount_untaxed = fields.Monetary(
        string="Subtotal",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )

    amount_total = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )

    amount_paid = fields.Monetary(
        string="Amount Paid",
        currency_field="currency_id",
        compute="_compute_amount_paid",
    )

    amount_due = fields.Monetary(
        string="Amount Due",
        currency_field="currency_id",
        compute="_compute_amount_due",
    )

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="restaurant_order_stock_picking_rel",
        column1="order_id",
        column2="picking_id",
        string="Inventory Transfers",
        copy=False,
        readonly=True,
    )

    @api.depends("order_line_ids.price_subtotal")
    def _compute_amounts(self):
        for order in self:
            order.amount_untaxed = sum(
                order.order_line_ids.mapped("price_subtotal")
            )
            order.amount_total = order.amount_untaxed

    @api.depends("payment_ids.amount", "payment_ids.state")
    def _compute_amount_paid(self):
        for order in self:
            order.amount_paid = sum(
                payment.amount
                for payment in order.payment_ids
                if payment.state == "posted"
            )

    @api.depends("amount_total", "amount_paid")
    def _compute_amount_due(self):
        for order in self:
            order.amount_due = max(
                order.amount_total - order.amount_paid,
                0.0,
            )

    @api.constrains("order_type", "table_id", "partner_shipping_id")
    def _check_order_requirements(self):
        for order in self:
            if order.order_type == "dine_in" and not order.table_id:
                raise ValidationError(
                    _("A table is required for dine-in orders.")
                )

            if order.order_type != "dine_in" and order.table_id:
                raise ValidationError(
                    _("Only dine-in orders can have a table.")
                )

            if order.order_type == "delivery" and not order.partner_shipping_id:
                raise ValidationError(
                    _("A delivery address is required for delivery orders.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    sequence.next_by_code("restaurant.order")
                    or "New"
                )
        return super().create(vals_list)

    def _check_can_change_state(self):
        for order in self:
            if order.state == "cancelled":
                raise UserError(
                    _("A cancelled order cannot be changed.")
                )

    def action_confirm(self):
        for order in self:
            order._check_can_change_state()

            if not order.order_line_ids:
                raise UserError(
                    _("Add at least one item before confirming the order.")
                )

            order.state = "confirmed"

    def action_start_preparing(self):
        for order in self:
            if order.state != "confirmed":
                raise UserError(
                    _("Only confirmed orders can be prepared.")
                )
            order.state = "preparing"

    def action_mark_ready(self):
        for order in self:
            if order.state != "preparing":
                raise UserError(
                    _("Only orders being prepared can be marked ready.")
                )
            order.state = "ready"

    def action_serve(self):
        for order in self:
            if order.state != "ready":
                raise UserError(
                    _("Only ready orders can be served.")
                )
            order.state = "served"

    def action_cancel(self):
        for order in self:
            if order.state == "cancelled":
                continue

            if order.picking_ids.filtered(
                lambda picking: picking.state == "done"
            ):
                raise UserError(
                    _(
                        "This order has completed inventory transfers. "
                        "Reverse the inventory operation before cancelling."
                    )
                )

            order.state = "cancelled"