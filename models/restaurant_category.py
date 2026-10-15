from odoo import fields, models


class RestaurantCategory(models.Model):
    _name = "restaurant.category"
    _description = "Restaurant Category"
    _order = "name"

    name = fields.Char(
        string="Category Name",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    menu_item_ids = fields.One2many(
        comodel_name="restaurant.menu.item",
        inverse_name="category_id",
        string="Menu Items",
    )

    menu_item_count = fields.Integer(
        string="Number of Menu Items",
        compute="_compute_menu_item_count",
    )

    def _compute_menu_item_count(self):
        for category in self:
            category.menu_item_count = len(category.menu_item_ids)