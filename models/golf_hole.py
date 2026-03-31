from odoo import models, fields, _, api

class GolfHole(models.Model):
    _name =  "golf.hole"
    _description =  "Golf Hole"
    _order = "field_id,number ASC"

    name = fields.Char(
        string="Name",
        required=True,
        compute="_compute_name",
        default="New",
        store=True,
    )

    field_id = fields.Many2one("golf.field", string="Field", required=True, ondelete="cascade", index=True, copy=False)
    number = fields.Integer()
    par = fields.Integer()
    handicap = fields.Integer()    
    length = fields.Integer(string=_("Length"))

    @api.depends("field_id", "number")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (rec.field_id.name, rec.number,)


    