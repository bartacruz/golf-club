from odoo import _,fields, models, api
from . import aag_secure_api

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    def create_from_external(self,golf_license):
        player = aag_secure_api.get_enrolled(golf_license)
        if not player:
            return
        # {'EnrollmentNumber': '101261', 'Active': True, 'FirstNames': 'JULIO', 'LastNames': 'SANTA CRUZ ', 'HandicapStandard': -99, 'HandicapEven3': -99, 'HandicapIndex': 15.6, 'LowestHandicapIndex': 18.1, 'OptionClubId': 365, 'Category': 0, 'BornDate': '27-8-1971', 'DocNumber': '22278642'}
        partner = self.search([
            ('firstname','ilike',player.get('FirstNames')),
            ('lastname','ilike',player.get('LastNames')),
        ])
        if not partner:
            partner = self.create({
                'firstname': player.get('FirstNames').title(),
                'lastname': player.get('LastNames').title(),
            })
            print("nuevo jugador",partner.name, player)
            
        partner.golf_license = int(player.get('EnrollmentNumber'))
        partner.update_from_external(player)
    
        return partner
            
            
    def update_from_external(self,data):
        self.ensure_one()
        print('update_from_external',data)
        if not data:
            self.golf_license_active=False
            return
        self.golf_player = True
        self.golf_license_active = data.get('Active')
        self.golf_handicap_index = data.get('HandicapIndex')
        self.golf_handicap = aag_secure_api.get_handicap(self.golf_handicap_index)
        if not self.golf_membership:
            club = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.club_id'))
            if data.get('OptionClubId',0) == club:
                membership = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.default_product'))
                self.golf_membership =  membership
        if not self.l10n_ar_afip_responsibility_type_id:
            self.l10n_ar_afip_responsibility_type_id = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.default_responsibility'))
        if not self.vat:
            try:
                self.l10n_latam_identification_type_id = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.default_identification_type'))
                self.vat = data.get('DocNumber')
            except:
                print("Error al setear el dni de ",self.name,': ', data.get('DocNumber'))
        
        
    def action_update_handicap(self):
        for record in self:
            if record.golf_license:
                # get data from AAG
                data = aag_secure_api.get_enrolled(record.golf_license)
                record.update_from_external(data)
