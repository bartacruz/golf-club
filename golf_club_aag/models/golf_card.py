from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class GolfCard(models.Model):
    _inherits = 'golf.card'
    
    aag_external_reference = fields.Integer()
    aag_posted_date = fields.Datetime(string='AAG Posted')
    
    
    def get_external_data(self):
        scores = []
        data = {
            'Id': self.id,
            'EnrollmentNumber': self.player_license,
            'BatchNumber': 1,
            'IniHole': 1,
            'State': 1,
            'ScoreGrossTotal': self.gross_score,
            'ScoreGrossIda': self.gross_score_first,
            'ScoreGrossVta': self.gross_score_last,
        }
        for score in self.score_ids:
            data['ScoreGrossHole%02d' % score.hole_number] = score.score
        return data
    
    