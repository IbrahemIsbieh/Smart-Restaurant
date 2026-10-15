from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantMenuItem(models.Model):
    _name = "restaurant.menu.item"
    _description = "Restaurant Menu Item"
    _order = "name"

    name = fields.Char(
        string="Item Name",
        required=True,
    )

    category_id = fields.Many2one(
        comodel_name="restaurant.category",
        string="Category",
        required=True,
        ondelete="restrict",
    )

    description = fields.Text(
        string="Description",
    )

    sale_price = fields.Monetary(
        string="Sale Price",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Finished Product",
        ondelete="restrict",
        help="Optional product representing the finished menu item.",
    )

    recipe_line_ids = fields.One2many(
        comodel_name="restaurant.recipe.line",
        inverse_name="menu_item_id",
        string="Recipe Ingredients",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.constrains("sale_price")
    def _check_sale_price(self):
        for item in self:
            if item.sale_price < 0:
                raise ValidationError(
                    "The sale price cannot be negative."
                )