from datetime import timedelta

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class RestaurantOrderReportWizard(models.TransientModel):
    _name = "restaurant.order.report.wizard"
    _description = "Restaurant Order Report Wizard"

    date_from = fields.Date(
        string="From Date",
        required=True,
        default=fields.Date.context_today,
    )

    date_to = fields.Date(
        string="To Date",
        required=True,
        default=fields.Date.context_today,
    )

    order_type = fields.Selection(
        selection=[
            ("all", "All Orders"),
            ("dine_in", "Dine In"),
            ("takeaway", "Takeaway"),
            ("delivery", "Delivery"),
        ],
        string="Order Type",
        required=True,
        default="all",
    )

    include_cancelled = fields.Boolean(
        string="Include Cancelled Orders",
        default=False,
    )

    def action_view_orders(self):
        self.ensure_one()

        if self.date_to < self.date_from:
            raise ValidationError(
                _("The end date must be on or after the start date.")
            )

        start_datetime = fields.Datetime.to_datetime(self.date_from)
        end_datetime = fields.Datetime.to_datetime(
            self.date_to + timedelta(days=1)
        )

        domain = [
            ("date_order", ">=", start_datetime),
            ("date_order", "<", end_datetime),
        ]

        if self.order_type != "all":
            domain.append(("order_type", "=", self.order_type))

        if not self.include_cancelled:
            domain.append(("state", "!=", "cancelled"))

        return {
            "type": "ir.actions.act_window",
            "name": _("Restaurant Orders Report"),
            "res_model": "restaurant.order",
            "view_mode": "list,form",
            "domain": domain,
            "context": {
                "create": False,
            },
        }