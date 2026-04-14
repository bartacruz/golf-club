# -*- coding: utf-8 -*-
{
    'name': "Golf Club: AAG Integration",

    'summary': "Argentine AAG api integration for Golf Club module",
    'sequence': 2,
    'description': """
        Argentine AAG api integration for Golf Club module.
    """,

    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    'category': 'Sports',
    'version': '18.0.0.0.2',

    'depends': ['base','golf_club'],

    'data': [
        'views/golf_tournament.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    "development_status": "Alpha",
    'maintainers': ['bartacruz'],
}
