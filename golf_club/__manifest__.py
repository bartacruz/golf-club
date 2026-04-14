# -*- coding: utf-8 -*-
{
    'name': "Golf Club",

    'summary': "Golf Club Module",
    'sequence': 1,
    
    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    'category': 'Sports',
    'version': '18.0.0.0.1',

    'depends': ['base','mail','account','l10n_ar'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/golf_field.xml',
        'views/golf_hole.xml',
        'views/golf_card.xml',
        'views/golf_player.xml',
        'views/golf_tournament.xml',
        'views/product_template.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'views/menu.xml',
        'reports/golf_card_report.xml',
        'data/tournament_modes.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    "development_status": "Alpha",
    'assets': {
        'web.assets_backend': [
            # 'golf_club/static/src/js/golf_card_widget.js',
            'golf_club/static/src/components/**/*',
            'golf_club/static/src/js/debug.js',
            'golf_club/static/src/css/golf.scss',
        ],
        'web.report_assets_common': [
            'golf_club/static/src/css/card.scss',
        ],
        'web.assets_frontend': [
            'golf_club/static/src/css/golf.scss',
        ],
    },
    'maintainers': ['bartacruz'],
}
