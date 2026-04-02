from odoo import models,fields,api,_
from . import aag_api
import re
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class GolfTournament(models.Model):
    _inherits = 'golf.tournament'

    aag_external_reference = fields.Integer()
    aag_posted_date = fields.Datetime(string='AAG Posted')
    
    def post_external(self):
        if not self.tournament_mode_id or not self.tournament_mode_id.external_reference:
            print("No se puede postear un torneo con un modo no soportado por AAG")
            return False
        if self.category:
            # hack para obtener el label del campo selection
            subtitle = dict(self._fields['category']._description_selection(self.env)).get(self.category)
        else:
            subtitle = ''
        
        # Torneo guardado correctamente con id: 93802{"Description":"Proceso ","ProcessStart":"2022-09-22T13:35:44.9020323-03:00","ProcessEnd":"2022-09-22T13:35:44.9020323-03:00","HasError":false,"Errors":[],"Comments":[]}
        cards = []
        data = {
            'Id': self.id,
            'Title': self.name,
            'Subtitle': subtitle,
            'GameMode': self.tournament_mode_id.external_reference,
            'BatchesCount': 1, # TODO: harcoded (numero de vueltas)
            'BatchesHoles': self.field_id.hole_count,
            'Category': int(self.category),
            'EndHandicap': self.end_handicap,
            'StartDate': datetime(self.date.year, self.date.month, self.date.day).isoformat(),
            'Field': self.field_id.external_reference,
            'TeeOut': 4532, # TODO: obtenerlo desde el campo
            'Active': self.state == 'active',
            'ScoreCards': cards,
        }
        
        posted_cards = self.card_ids.filtered(lambda card: card.player_id.golf_license_active and not card.posted and card.state == 'loaded')
        
        for card in posted_cards:
            if card.player_id.golf_license_active and not card.posted:
                cards.append(card.get_external_data())
        
        print(data)
        response = aag_api.post_tournament(data)
        print('response',response)
        # TODO: retornar un mensaje de ok/error o algo similar
        if type(response) == str:
            rr = re.search(r'Torneo guardado correctamente con id: (\d+)',response)
            if rr:
                self.external_reference = rr[1]
                self.posted=True
                posted_cards.action_posted()
                self.message_post(body=_('Tournament posted'))
                return True
        else:
            print('hasError',response.keys(),response.get('HasError'))
            self.message_post(body=_('Error posting tournament'))
        
        return False

    def fetch_tournament(self,tid=None):
        self.ensure_one()
        
        if not self.external_reference:
            return False
        
        t =aag_api.get_tournament(self.external_reference)
        print(t)
        self.tournament_mode_id = self.env['golf.tournament_mode'].search([('external_reference','=',t.get('GameMode'))]).id
        self.date = t.get('StartDate')
        # TODO: chequear si se puede crear en la AAG un campo para 9 hoyos.
        if t.get('BatchesHoles',0) == 9:
            self.field_id = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.default_field_9'))
        else:
            self.field_id = self.env['golf.field'].search([('external_reference','=',t.get('Field'))]).id
        
        # Hack para los que tienen titulo generico
        if t.get('Title') == 'SPGC':
            self._check_name()
        else:
            self.name = t.get('Title')
        
        if t.get('Active',False):
            self.state = 'active'
        else:
            self.state = 'finished'
    
        self.posted = True
        
        for card in t.get('ScoreCards'):
            if card.get('Status') not in ['Original','Ajuste']:
                continue
            player = self.env['res.partner'].search([('golf_license','=',card.get('EnrollmentNumber'))])
            if not player:
                print("creando desde aag",card.get('EnrollmentNumber'))
                player = self.env['res.partner'].create_from_external(card.get('EnrollmentNumber'))
            vals={
                'external_reference': card.get('Id'),
                'tournament_id': self.id,
                'player_id': player.id,
                'posted': True,
            }
            scorecard = self.env['golf.card'].create(vals)
            scorecard._set_handicap()
            scorecard.message_post(body='Tarjeta importada desde la AAG')
            
            for hole,score in {k:v for k,v in card.items() if k.startswith('ScoreGrossHole')}.items():
                hole_number=int(hole.replace('ScoreGrossHole',''))
                scorecard.set_score(hole_number,score)
        self.message_post(body='Torneo importado desde la AAG')    
        self._default_product()
        self.action_leaderboard()
        return self