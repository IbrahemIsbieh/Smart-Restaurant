from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantRecipeLine(models.Model):
    _name = "restaurant.recipe.line"
    _description = "Restaurant Recipe Ingredient"
    _order = "menu_item_id, id"

    menu_item_id = fields.Many2one(
        comodel_name="restaurant.menu.item",
        string="Menu Item",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Ingredient",
        required=True,
        ondelete="restrict",
        domain=[("type", "=", "consu")],
    )

    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits="Product Unit of Measure",
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        store=True,
        readonly=True,
    )

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    "Ingredient quantity must be greater than zero."
                )

    _menu_ingredient_unique = models.Constraint(
        "UNIQUE(menu_item_id, product_id)",
        "An ingredient can only appear once in a menu item's recipe.",
    )