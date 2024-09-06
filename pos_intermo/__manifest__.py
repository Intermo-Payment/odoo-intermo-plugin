# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS Intermo Payment',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': -100,
    'author': 'Abdul Rahman S test final',
    'summary': 'Integrate Intermo payment gateway with Odoo POS',
    'description': 'This module integrates the Intermo payment gateway with Odoo POS.',
    'depends': ['base', 'point_of_sale','payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/intermo_config_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_intermo/static/src/js/pos_intermo.js',
        ],
    },
    'qweb': [
        'pos_intermo/static/src/js/IntermoKeyScreen.js',
        'pos_intermo/static/src/js/PosModel.js',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
