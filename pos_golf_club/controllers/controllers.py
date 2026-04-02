# -*- coding: utf-8 -*-
# from odoo import http


# class PosGolfClub(http.Controller):
#     @http.route('/pos_golf_club/pos_golf_club', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_golf_club/pos_golf_club/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_golf_club.listing', {
#             'root': '/pos_golf_club/pos_golf_club',
#             'objects': http.request.env['pos_golf_club.pos_golf_club'].search([]),
#         })

#     @http.route('/pos_golf_club/pos_golf_club/objects/<model("pos_golf_club.pos_golf_club"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_golf_club.object', {
#             'object': obj
#         })

