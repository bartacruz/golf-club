# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        url_for = self.env['ir.http']._url_for
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_('Tournaments'), url_for('/golf'), 'golf'))
        return suggested_controllers
