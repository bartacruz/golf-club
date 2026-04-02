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

    # any module necessary for this one to work correctly
    'depends': ['base','golf_club'],

    # always loaded
    'data': [
        'views/golf_card.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    "development_status": "Alpha",
#    'images': ['static/description/golf-icon.png'],
    'maintainers': ['bartacruz'],
}
