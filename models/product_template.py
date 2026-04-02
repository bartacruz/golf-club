from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    green_fee = fields.Boolean(
        string="Green Fee",
        store=True,
        readonly=False,
    )
