from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aag_username = fields.Char(string="AAG Username", config_parameter='golf_club_aag.username')
    aag_api_key = fields.Char(string="AAG API Key", config_parameter='golf_club_aag.api_key')
