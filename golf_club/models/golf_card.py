import math
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
import pytz


class GolfCard(models.Model):
    _name = 'golf.card'
    _description = 'a golf card'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        default='New',
        copy=False
    )

    date = fields.Date(string='Date', default=fields.datetime.now().date())
    tournament_id = fields.Many2one('golf.tournament',
                                    string='Tournament',
                                    required=True,
                                    ondelete='cascade',
                                    index=True,
                                    copy=False,
                                    default=lambda self: self._default_tournament_id(),
                                    )
    player_id = fields.Many2one('res.partner', string='Player', required=True,
                                ondelete='cascade', index=True, copy=False, domain=[("golf_player", "=", True)])
    marker_id = fields.Many2one('res.partner', string='Marker', domain=[
                                ("golf_player", "=", True)])

    score_ids = fields.One2many("golf.score", 'card_id', string='Scores')

    gross_score = fields.Integer(compute='_calculate_score', store=True)
    net_score = fields.Integer(compute='_calculate_score', store=True)

    gross_score_first = fields.Integer(string='First 9',compute='_calculate_score', store=True)
    gross_score_last = fields.Integer(string='Last 9',compute='_calculate_score', store=True)
    
    player_handicap = fields.Integer(string='Handicap')
    player_license = fields.Integer(string='Golf license')
    player_license_active = fields.Boolean(string='License Active', related='player_id.golf_license_active', readonly=True)

    position = fields.Integer(default=0)
    position_tied = fields.Boolean()
    position_label = fields.Char(compute='_compute_position_label', store=True)

    account_move_id = fields.Many2one(
        'account.move', string='Invoice', readonly=True, copy=False)

    state = fields.Selection(selection=[
        ('draft','Draft'),
        ('active','Active'), # is paid or forced
        ('loaded','Loaded'), # all holes with score > 0
        ('posted','Posted'), # Presented to the club.
        ('cancelled','Cancelled'),
        ], default='draft')
    
    is_paid = fields.Boolean(string='Paid', compute="_compute_is_paid", store=True)
    
    def set_score(self,hole_number,score):
        golf_score = self.score_ids.filtered(lambda s: s.hole_number == hole_number)
        golf_score.score = score

    @api.depends('account_move_id.state')
    def _compute_is_paid(self):
        for record in self:
            if record.account_move_id and record.account_move_id.payment_state == 'paid':
                record.is_paid = True
                if record.state == 'draft':
                    record.state = 'active'
            
    @api.depends('position', 'position_tied')
    def _compute_position_label(self):
        for record in self:
            if record.position > 0:
                tied = 'T' if record.position_tied else ''
                record.position_label = '%s%s' % (tied, record.position, )
            else:
                record.position_label = None


    def _default_tournament_id(self):
        tournament_ids = self.env["golf.tournament"].search(
            [],
            order="date desc",
            limit=1,
        )
        if tournament_ids:
            return tournament_ids[0]
        else:
            raise ValidationError(
                _("You must create an golf tournament first."))
                    
    def _calculate_handicap(self,fields, player):
        if player.golf_handicap_index > 0:
            hcp = player.golf_handicap_index
            slope_rating = sum(fields.mapped("slope_rating_total")) /len(fields)
            course_rating = sum(fields.mapped("course_rating_total"))
            field_par = sum(fields.mapped("par"))
            handicap = round(hcp * (slope_rating/113) + course_rating-field_par)
        else:
            handicap = player.golf_handicap
        
        # TODO: revisar esto porque en algunos clubes toman el handicap de la vuelta con el handcap 1
        # if sum(fields.mapped('hole_count')) == 9:
        #     higher = field.hole_ids.search_count([('handicap', '=', 1)])
        #     if higher:
        #         handicap = math.ceil(handicap/2)
        #     else:
        #         handicap = math.floor(handicap/2)
        return handicap

    def _check_handicap(self):
        player_handicap= self._calculate_handicap(self.tournament_id.field_ids,self.player_id)
        if player_handicap < self.tournament_id.start_handicap:
            raise ValidationError(
                _('Player %(player)s has a smaller handicap (%(player_handicap)s) than tournament category %(tournament_handicap)s.',
                    player=self.player_id.name,
                    player_handicap = player_handicap,
                    tournament_handicap = self.tournament_id.start_handicap)
            )
        if player_handicap > self.tournament_id.end_handicap:
            raise ValidationError(
                _('Player %(player)s has a bigger handicap (%(player_handicap)s) than tournament category %(tournament_handicap)s.',
                    player = self.player_id.name,
                    player_handicap = player_handicap,
                    tournament_handicap = self.tournament_id.end_handicap)
            )
        return player_handicap
    
    @api.onchange('player_id')
    def _set_handicap(self):
        for record in self:
            if record.state in ['posted','cancelled']:
                return
            if not record.player_id:
                return
            player = record.player_id
            record.player_handicap = record._check_handicap()
            record.player_license = player.golf_license
            print("_set_handicap",record,record.player_id.name,record.player_handicap,record.player_license)
            

    @api.depends("score_ids.score", "player_handicap")
    def _calculate_score(self):
        for rec in self:
            if rec.state != "posted":
                return
            net = rec.net_score  # save it to detect changes
            rec.gross_score = sum(c.score for c in rec.score_ids)
            rec.gross_score_first = sum(c.score for c in rec.score_ids[0:9])
            rec.gross_score_last = sum(c.score for c in rec.score_ids[9:18])
            if rec.gross_score > 0:
                rec.net_score = rec.gross_score - rec.player_handicap
            else:
                rec.net_score = 0

            if net != rec.net_score:
                rec.tournament_id.action_leaderboard()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("golf.card")
        cards = super(GolfCard, self).create(vals_list)
        for card in cards:
            for hole in card.tournament_id.field_ids.mapped('hole_ids'):
                values = {
                    'card_id': card.id,
                    'hole_id': hole.id,
                }
                self.env["golf.score"].sudo().create(values)
        return cards
    
    def write(self, vals):
        r = super().write(vals)
        
        if self.state == "active" and not self.score_ids.filtered(lambda s: s.score == 0):
            print("tarjeta cargada!", [s.score for s in self.score_ids])
            self.state = 'loaded'
            self.message_post(body=_('Card scores loaded'))
            return True
        return r
    
    
    def action_post(self):
        for record in self:
            if record.state != 'loaded':
                raise ValidationError(_('Only cards with all scores loaded can be posted.'))
            self.state = 'posted'
            self.message_post(body=_('Card posted'))
                    
    def action_view_invoice(self):
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["views"] = [(self.env.ref("account.view_move_form").id, "form")]
        action["res_id"] = self.account_move_id.id
        return action

    def action_golf_card_invoice(self):
        self.ensure_one()
        timezone = pytz.timezone(self._context.get(
            'tz') or self.env.user.tz or 'UTC')

        # TODO: use categories for products
        product = self.tournament_id.default_product_id
        player = self.player_id
        if player.property_product_pricelist:
            price = player.property_product_pricelist.get_product_price(
                product, 1, player)
            name = '%s - %s' % (product.display_name,
                                player.property_product_pricelist.name,)
        else:
            price = product.list_price
            name = product.name
        invoice_line = {
            'product_id': product.id,
            'quantity': 1,
            'price_unit': price,
            'name': name,
            'tax_ids': [(6, 0, product.taxes_id.ids)],
        }
        narration = '%s - %s' % (product.display_name,
                                 self.tournament_id.name,)
        move_vals = {
            'payment_reference': self.name,
            'invoice_origin': self.tournament_id.name,
            'state': 'draft',
            'move_type': 'out_invoice',
            'ref': self.name,
            'partner_id': player.id,
            'narration': narration,
            'invoice_user_id': self.env.context.get('user_id', self.env.user.id),
            'invoice_date': self.date,
            'invoice_line_ids': [(0, None, invoice_line)],

        }

        new_move = self.env['account.move'].sudo().with_context(
            default_move_type=move_vals['move_type']).create(move_vals)
        self.write({'account_move_id': new_move.id})
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': new_move.id,
        }


class GolfScore(models.Model):
    _name = 'golf.score'
    _description = 'a golf hole score'

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
        copy=False,
        compute="_compute_name",
        default='New',
        store=True,
    )

    card_id = fields.Many2one('golf.card', string='Card',
                              required=True, ondelete='cascade', index=True, copy=False)
    hole_id = fields.Many2one('golf.hole', string='Hole',
                              required=True, ondelete='cascade', index=True, copy=False)
    hole_number = fields.Integer(related='hole_id.number',readonly=True,store=True)
    field_name = fields.Char(compute='_set_field_name', store=True)
    handicap = fields.Integer(related='hole_id.handicap', readonly=True, store=True)
    length = fields.Integer(related='hole_id.length', readonly=True, store=True)
    par = fields.Integer(related='hole_id.par', readonly=True, store=True)
    score = fields.Integer(string='Score')

    @api.depends('card_id', 'hole_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s - %s' % (rec.card_id.name, rec.hole_id.name,)
    
    @api.depends("hole_id")
    def _set_field_name(self):
        for rec in self:
            rec.field_name = rec.hole_id.field_id.name

    def get_field_name(self):
        return self.hole_id.field_id.name
