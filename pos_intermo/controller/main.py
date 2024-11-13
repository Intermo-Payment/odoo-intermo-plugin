# coding: utf-8
import logging
import json
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosVivaWalletController(http.Controller):

    @http.route('/pos_intermo/notification', type='json', auth='none', csrf=False)
    def notification(self, **post):
        # TODO : check the status of payment
        # Extract JSON data from the request
        json_data = json.loads(request.httprequest.get_data().decode('utf-8'))

        # Get values from the JSON payload
        order_id = json_data.get('order_id')
        status = json_data.get('status')

        # Check if the order exists
        order = request.env['pos.payment.txn'].sudo().search([('name', '=', order_id)])
        if not order:
            # Create a new order if not found
            request.env['pos.payment.txn'].sudo().create({
                'name': order_id,
                'status': status
            })
        else:
            # Update the status if order exists
            order.status = status

        return {'success': True, 'message': 'Order processed successfully'}