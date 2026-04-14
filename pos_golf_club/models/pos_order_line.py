# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    golf_card_id = fields.Many2one('golf.card', string='Golf Card', readonly=True)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['golf_card_id']
        return fields
    
    def create_golf_card(self):
        tournament_id = self.env['golf.tournament'].search([ ('state','=','active')],limit=1)
        if not tournament_id:
            return
        cards = self.env['golf.card']
        for record in self:
            if record.golf_card_id:
                continue
            player_id = record.order_id.partner_id
            card = self.env['golf.card'].create({
                "tournament_id":tournament_id.id,
                "player_id": player_id.id,
                "pos_order_line_id": record.id,
            })
            cards |= card
            record.golf_card_id = card.id
            _logger.info(f"Golf Card {card.id} created for POS order line {record.id}")
            card.message_post(body=f"Golf Card created from POS order {record.order_id.name}")
        return cards