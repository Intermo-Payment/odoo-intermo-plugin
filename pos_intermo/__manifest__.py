# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Intermo',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': -9999999,
    'summary': 'Integrate your POS with Intermo Payment Gateway terminals',
    'author': 'Intermo Developer Team',
    'description': """
        POS Intermo Integration
        ==============================

        This module allows customers to pay with debit/credit cards and wallets through Intermo POS terminals.
        Transactions are processed by Intermo POS, requiring a valid Intermo merchant account.

        Features:
        * Quick payments via card swipe, scan, or QR code.
        * Supported payment methods include Visa, MasterCard, Sama Money, and other Wallets.

        For more information, visit [intermo.net](https://intermo.net).
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/intermo_gateway_config_form_view.xml',
        'views/intermo_order_views.xml',
        'views/menu_api_keys.xml',
    ],
    'depends': ['point_of_sale'],
    'assets': {
        'web.assets_backend': [
            'pos_intermo/static/src/js/jquery.js',
            'pos_intermo/static/src/js/intermo.js',
        ],
        'point_of_sale._assets_pos': [
            'pos_intermo/static/**/*',
        ],
    },
    'license': 'LGPL-3',
    'website': 'https://intermo.net',
    'images': ['static/description/icon.png'],  # Path to the module's icon
    'installable': True,
}
