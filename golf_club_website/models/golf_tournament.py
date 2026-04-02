# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GolfTournament(models.Model):
    _name = 'golf.tournament'
    _inherit = ['golf.tournament','website.published.mixin']
    
    def action_activate(self):
        super().action_activate()
        for record in self:
            self.website_published = True
            
    def action_cancel(self):
        super().action_cancel()
        for record in self:
            self.website_published = False

    @api.depends('name')
    def _compute_website_url(self):
        super(GolfTournament, self)._compute_website_url()
        slug = self.env['ir.http']._slug
        for tournament in self:
            if tournament.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                tournament.website_url = f'/golf/tournament/{slug(tournament)}'
            else:
                tournament.website_url = False
    
    def action_toggle_website_published(self):
        for record in self:
            record.website_published =  not record.website_published