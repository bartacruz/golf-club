
from odoo import models, fields, api

class GolfCard(models.Model):
    _inherit = 'golf.card'
    
    pos_order_line_id = fields.Many2one('pos.order.line', string='POS Order line', readonly=True)
    pos_order_id = fields.Many2one('pos.order', related="pos_order_line_id.order_id")
    @api.model

    def _load_pos_data_fields(self, config_id):
        print("_load_pos_data_fields de Golf Card",config_id)
        return ['id', 'name', 'player_id', 'state', 'pos_order_line_id']

    def action_view_pos_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')
        #action["views"]= [[self.env.ref("point_of_sale.view_pos_pos_form").id, "form"]],
        
        # action["view_mode"] = 'form'
        # action['domain'] = [('id', '=', self.pos_order_id.id)]
        # action['res_id'] = 
        action.update({
            'views': [(self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')],
            'res_id': self.pos_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        })
        print("action",action)
        return action