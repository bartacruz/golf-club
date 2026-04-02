# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    golf_card_ids = fields.Many2many('golf.card', string='Golf Card', readonly=True, copy=False,compute='_compute_golf_cards')

    @api.depends('lines.golf_card_id')
    def _compute_golf_cards(self):
        for order in self:
            order.golf_card_ids = order.lines.mapped('golf_card_id')
            
    def _process_saved_order(self, draft):
        print("_process_saved_order self:",self,self.state,draft)
        ret = super()._process_saved_order(draft)
        # re-read the order.
        record = self.browse(ret)
        print("_process_saved_order ret:",record,record.state)
        if record.state in  ['paid','invoiced'] :
            green_fee_lines = record.lines.filtered(lambda line: line.product_id and line.product_id.product_tmpl_id.green_fee and not line.golf_card_id)
            print("_process_saved_order green fee lines:",green_fee_lines)
            card = green_fee_lines.create_golf_card()
            print("_process_saved_order card:",card) 
            drafts = record.golf_card_ids.filtered(lambda c: c.state == 'draft')
            drafts.write({'state':'active'})
            drafts.message_post(body=f"Golf Card activated from POS order {record.name}")
            record.golf_card_ids.write({'account_move_id': record.account_move.id})
        return ret               
    