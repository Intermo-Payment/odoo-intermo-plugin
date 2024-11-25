from odoo.exceptions import UserError
from odoo import fields, models, api, _
from io import BytesIO
import qrcode
import base64
import json
import random
import logging
from .intermo_pos_request import IntermoPosRequest
import requests

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        """Extend loader parameters to include additional Intermo fields."""
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'] += [
            'intermo_public_key',
            'intermo_plugin_key',
            'intermo_auth_key',
            'intermo_secret_key',
        ]
        return result


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    #icon = fields.Binary(string="Payment Method Icon", attachment=True)

    intermo_mode = fields.Selection(
        [('test', 'Sandbox'), ('live', 'Production')],
        default='test',
        string="Mode"
    )
    intermo_public_key = fields.Char('Intermo Public Key')
    intermo_plugin_key = fields.Char(
        'Intermo Plugin Key',
        default=lambda self: self._get_default_plugin_key_intermo()
    )
    intermo_auth_key = fields.Char('Intermo Auth Token')
    intermo_secret_key = fields.Char('Intermo Secret Key')

    @staticmethod
    def _get_default_plugin_key_intermo():
        """Generate a random 18-digit number as the default plugin key."""
        return ''.join(random.choices('0123456789', k=18))

    def _get_payment_terminal_selection(self):
        """Add 'Intermo' as a payment terminal option."""
        return super()._get_payment_terminal_selection() + [('intermo', 'Intermo')]

    def intermo_get_payment_status(self, data):
        """Fetch the payment status from Intermo."""
        _logger.info(f"Checking payment status for data: {data}")

        url = f'http://localhost:7777/api/v1/pos/status/{data}'
        config = self.env['intermo.gateway.config'].search([], limit=1)
        if not config:
            raise UserError("Intermo Gateway Configuration is missing!")

        payload = json.dumps({
            "publicApiKey": config.sandbox_public_key,
            "secretKey": config.sandbox_secret,
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.sandbox_authentication_key}',
        }

        try:
            response = requests.get(url, headers=headers, data=payload)
            response.raise_for_status()
            _logger.info(f"Response from Intermo: {response.text}")
            return json.loads(response.text).get('paymentStatus', 'Unknown')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching payment status: {e}")
            raise UserError(_("Failed to fetch payment status. Please try again."))

    def intermo_make_payment_request(self, data):
        """Create a payment request using Intermo."""
        intermo = IntermoPosRequest(self.env)
        _logger.info(f"Initiating payment request with data: {data}")

        response = intermo._get_access_token(payload=data)
        _logger.info(f"Payment request response: {response}")

        if response.get('paymentlink') and not response.get('errorCode'):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(response['paymentlink'])
            qr.make(fit=True)

            buffer = BytesIO()
            qr.make_image(fill='black', back_color='white').save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return {
                'qr_code': img_base64,
                'jwt_token': response['paymentlink'].split('/pay/')[1],
            }

        error = response.get('errorMessage') or _("An unexpected error occurred.")
        return {'error': str(error)}

    def intermo_cancel_payment_request(self, data):
        """Cancel a payment request."""
        _logger.info(f"Canceling payment request with data: {data}")
        return {'errorMessage': ""}