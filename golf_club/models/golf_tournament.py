from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

DEFAULT_START_HANDICAP = 0
DEFAULT_END_HANDICAP = 54
class GolfTournament(models.Model):
    _name = 'golf.tournament'
    _description = 'a golf tournament'
    _inherit = [
        'mail.thread', 
        'mail.activity.mixin'
    ]

    name = fields.Char(
        string='Name',
        required=True,
        default='New',
        copy=False
    )

    date = fields.Date(string='Date')
    parent_id = fields.Many2one('golf.tournament')
    child_ids = fields.One2many('golf.tournament', 'parent_id')
    field_ids = fields.Many2many(
        string='Fields',
        comodel_name='golf.field',
    )
    
    notes = fields.Text('Notes')
    
    card_ids = fields.One2many('golf.card','tournament_id',string='Cards')
    card_count = fields.Integer(compute = '_count_cards')
    active_card_count = fields.Integer(compute = '_count_cards')
    player_ids = fields.Many2many('res.partner', string='Players', domain=[("golf_player", "=", True)])

    default_product_id = fields.Many2one(
        string='Default Product',
        comodel_name='product.template',
        ondelete='restrict',
    )
    tournament_mode_id = fields.Many2one('golf.tournament_mode', string = 'Mode')
    
    state = fields.Selection(selection=[
            ('new', 'New'),
            ('active', 'Active'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='new')
    
    category = fields.Selection(selection=[('0','Caballeros'),('1','Damas')], default='0')
    start_handicap = fields.Integer('Start handicap', default=DEFAULT_START_HANDICAP)
    end_handicap = fields.Integer('End handicap', default=DEFAULT_END_HANDICAP)
    
    @api.onchange('date')
    def _default_product(self):
        if not self.date:
            return
        if self.date.weekday() > 4:
            self.default_product_id = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.tournament_product_weekend'))
        else:
            self.default_product_id = int(self.env['ir.config_parameter'].sudo().get_param('golf_club.tournament_product'))
    
    def action_activate(self):
        for record in self:
            self.state = 'active'
            self.message_post(body=_('Tournament activated'))
            _logger.info('Tournament %s activated', record.name)
    
    def action_finish(self):
        for record in self:
            self.state = 'finished'
            self.message_post(body=_('Tournament finished'))
            _logger.info('Tournament %s finished', record.name)

    def action_cancel(self):
        for record in self:
            self.state = 'cancelled'
            self.message_post(body=_('Tournament cancelled'))
            _logger.info('Tournament %s cancelled', record.name)
    
    @api.depends('card_ids')
    def _count_cards(self):
        for rec in self:
            rec.card_count = len(rec.card_ids)
            rec.active_card_count = len([x for x in rec.card_ids if x.net_score > 0])
            rec.player_ids |= rec.mapped("card_ids.player_id")
    
    def _check_name(self):
        for record in self:
            if record.name in [_('New'),'SPGC'] and record.tournament_mode_id and record.field_ids:
                if record.start_handicap != DEFAULT_START_HANDICAP or record.end_handicap != DEFAULT_END_HANDICAP:
                    record.name = '%s - Cat %d-%d' % (record.tournament_mode_id.name, record.start_handicap, record.end_handicap)    
                else:
                    record.name = '%s - %d hoyos' % (record.tournament_mode_id.name, len(record.get_holes()),)

    @api.model_create_multi
    def create(self,vals_list):
        tournaments = super(GolfTournament, self).create(vals_list)
        for tournament in tournaments:
            if tournament.name == _("New"):
                tournament._check_name()
        return tournaments
    
    def write(self, vals):
        t =  super().write(vals)
        if self.name== _("New"):
            self._check_name()
        return t
        
    def get_holes(self):
        holes = list(self.field_ids.mapped("hole_ids"))
        return holes

    def action_print_leaderboard(self):
        for tournament in self:
            print("PRINT LEADERBOARD",tournament)
                
    def action_open_leaderboard(self):
        for tournament in self:
            action = self.env.ref("golf_club.action_golf_leaderboard_act_window").read()[0]
            action["context"] = {}
            action["domain"] = ['&',("id", "in", tournament.card_ids.ids),("position",">",0)]
            return action

    def get_leaderboard(self):
        self.ensure_one()
        GolfCard = self.env['golf.card']
        leaderboard = sorted(GolfCard.sudo().search([('tournament_id','=',self.id),('position','>',0)]),key=lambda x: x.position)
        return leaderboard

    @api.onchange("card_ids")
    def action_leaderboard(self):
        self.tournament_mode_id._process_cards(self)

