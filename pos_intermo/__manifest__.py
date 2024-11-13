# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Intermo',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a intermo payment terminal',
    'description': """
Allow intermo POS payments
==============================

This module allows customers to pay for their orders with debit/credit
cards and UPI. The transactions are processed by intermo POS. A intermo merchant account is necessary. It allows the
following:

* Fast payment by just swiping/scanning a credit/debit card or a QR code while on the payment screen
* Supported cards: Visa, MasterCard, Rupay, UPI
    """,
    'data': [
        # 'views/pos_payment_method_views.xml',
        "security/ir.model.access.csv",
        'views/pos_payment_views.xml',
        'views/pos_payment_method_views.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
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
}
