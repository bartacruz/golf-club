{
    "name": "pos_golf_club",
    "summary": "Point of Sale for Golf Club module",
    "author": "Julio Santa Cruz",
    "website": "https://github.com/bartacruz/golf_club",
    "category": "Sports",
    "version": "18.0.0.0.2",
    "license": "AGPL-3",
    "depends": ["golf_club", "point_of_sale"],
    # always loaded
    "data": [
        "views/golf_card.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_golf_club/static/src/app/**/*",
        ],
    },
}
