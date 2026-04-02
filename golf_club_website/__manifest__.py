# -*- coding: utf-8 -*-
{
    'name': "Golf Club: Website",

    'summary': "Website for Golf Club module",
    'sequence': 2,
    'description': """
        Website for Golf Club module.
    """,

    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    'category': 'Sports',
    'version': '18.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['website','golf_club'],

    # always loaded
    'data': [
        'views/website_golf.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    "development_status": "Alpha",
    'maintainers': ['bartacruz'],
}
