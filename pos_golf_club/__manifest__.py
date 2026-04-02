# -*- coding: utf-8 -*-
{
    'name': "pos_golf_club",

    'summary': "Point of Sale for Golf Club module",

    'description': """
Point of Sale for Golf Club module
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sports',
    'version': '18.0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['golf_club', 'point_of_sale'],

    # always loaded
    'data': [
        'views/golf_card.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_golf_club/static/src/app/**/*',
        ],
    },
}

