# -*- coding: utf-8 -*-
{
    'name': "Komisi Jamaah",

    'summary': """
        Generate Komisi Jamaah""",

    'description': """
        Generate Komisi Jamaah
    """,

    'author': "Rifqi Aditya",
    'website': "https://www.linkedin.com/in/rifqiadeetya/",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'sale', 'account', 'sale_umroh'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/generate_komisi.xml',
        'views/views.xml',
        'views/komisi_menu.xml',
        'views/commision_rate.xml',
        'views/generate_commision_button.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/inisial_komisi_msafar/static/src/js/generate_button.js',
            '/inisial_komisi_msafar/static/src/xml/generate_button.xml',
        ]
    },
}
