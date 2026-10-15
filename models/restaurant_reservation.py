from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RestaurantReservation(models.Model):
    _name = "restaurant.reservation"
    _description = "Restaurant Reservation"
    _order = "date_start asc, id desc"

    name = fields.Char(
        string="Reservation Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        ondelete="restrict",
    )

    table_id = fields.Many2one(
        comodel_name="restaurant.table",
        string="Table",
        required=True,
        ondelete="restrict",
    )

    date_start = fields.Datetime(
        string="Start",
        required=True,
    )

    date_end = fields.Datetime(
        string="End",
        required=True,
    )

    guest_count = fields.Integer(
        string="Guests",
        required=True,
        default=2,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("done", "Done"),
        ],
        string="Status",
        required=True,
        default="draft",
    )

    notes = fields.Text(
        string="Notes",
    )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    sequence.next_by_code("restaurant.reservation")
                    or "New"
                )
        return super().create(vals_list)

    @api.constrains("date_start", "date_end", "guest_count", "table_id")
    def _check_reservation(self):
        for reservation in self:
            if reservation.date_start and reservation.date_end:
                if reservation.date_end <= reservation.date_start:
                    raise ValidationError(
                        _("The reservation end must be after its start.")
                    )

            if reservation.guest_count <= 0:
                raise ValidationError(
                    _("Guest count must be greater than zero.")
                )

            if (
                reservation.table_id
                and reservation.guest_count > reservation.table_id.capacity
            ):
                raise ValidationError(
                    _("Guest count exceeds the table capacity.")
                )

    @api.constrains("table_id", "date_start", "date_end", "state")
    def _check_overlapping_reservations(self):
        for reservation in self:
            if (
                reservation.state not in ("draft", "confirmed")
                or not reservation.table_id
                or not reservation.date_start
                or not reservation.date_end
            ):
                continue

            overlapping = self.search_count([
                ("id", "!=", reservation.id),
                ("table_id", "=", reservation.table_id.id),
                ("state", "in", ("draft", "confirmed")),
                ("date_start", "<", reservation.date_end),
                ("date_end", ">", reservation.date_start),
            ])

            if overlapping:
                raise ValidationError(
                    _(
                        "This table already has a reservation "
                        "during the selected period."
                    )
                )

    def action_confirm(self):
        for reservation in self:
            if reservation.state != "draft":
                raise ValidationError(
                    _("Only draft reservations can be confirmed.")
                )
            reservation.state = "confirmed"

    def action_cancel(self):
        for reservation in self:
            if reservation.state == "done":
                raise ValidationError(
                    _("Completed reservations cannot be cancelled.")
                )
            reservation.state = "cancelled"