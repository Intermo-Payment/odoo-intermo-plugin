from odoo.exceptions import UserError
from odoo import fields, models, api, _
from io import BytesIO
import qrcode
import base64
import json
import random
import logging
import requests
from .intermo_pos_request import IntermoPosRequest
import urllib.parse

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

_logger = logging.getLogger(__name__)

# Public key defined outside the function with correct formatting
public_key_pem = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAqdI6LO/cgCV7ySWEA+wL
VX7KO3ZFWDhh+uD8uWvDoSLUgsytRQ+cSVS+XHezUoSScz/2wAkMbKVSt3iypJIy
5ZTBprcsyQDB1AQx/35F4SVr5AFgEFQ+Y9VMQZ+XJUWImj6GlrxkYBPhiDr1UkO1
2hof/luaF5z5FHgtMAE64pUbR0rLseAy8QackpNMj9o/Nfp5wHM0hdGKTaQPCqe6
95y+HKyhrkMHrhq/Ybg2voi3vAUQ5iFOQG8/NoPvc/J16i+MLxy7FuwzINLDrs5L
rB027HTpCq5Jr4M/PdYNfCaEW9p8VgWPG0Ri7MadVokq6cyq8v3dOkhl5Ch1CRUB
X8ZGQGJrH6BeWXhif4Xh9nu08FKRpU6ifkj4y46Y2jnjN9raVMkIsIN56v+z1TkE
zNiqAURGokdxoP4zwqobd2mrWJXkOuEsMsGcEoIYo+eYKKspB8B/RjWFerxj8ZD+
XE+0MKGIEzlWYYNMaoasUheZli8BtZ5puFehOwMmHEBBBkFvokldCvxd5ZegmXq2
Q3VpYw6GCmwEdhH9d9TKtEdVkCKFn2GUtBXUJlRR4IJGjxW+NjaYT8hyTSfb1rgr
rgwZRLRw7vwvt6pud/KMzEgSx9qlfJ61MFD7UjqHZj2F7Iqz4qfkDfj3ckXjrenU
r1+bmORtoz6vFVADw10ptpsCAwEAAQ==
-----END PUBLIC KEY-----"""

    
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

    def _check_odoo_connection(self):
        """Check if Odoo is online."""
        try:
            self.env.cr.execute("SELECT 1")
            return True
        except Exception:
            return False

    def intermo_get_payment_status(self, data):
        """Fetch the payment status from Intermo, skipping for offline payments."""
        if not self._check_odoo_connection():
            return {'error': _("Offline Odoo - Unable to check payment status.")}

        #_logger.info(f"Checking payment status for data: {data}")

        # Fetch Intermo Gateway Configuration
        config = self.env['intermo.gateway.config'].search([], limit=1)
        if not config:
            raise UserError(_("Intermo Gateway Configuration is missing!"))

        # Determine if we're in sandbox or production mode
        if config.mode == "sandbox":
            public_key = config.sandbox_public_key
            secret_key = config.sandbox_secret
            authentication_key = config.sandbox_authentication_key
        elif config.mode == "live":
            public_key = config.production_public_key
            secret_key = config.production_secret
            authentication_key = config.production_authentication_key
        else:
            raise UserError(_("Invalid mode in Intermo Gateway Configuration!"))

        # Construct the API request
        url = f'http://localhost:7777/api/v1/pos/status/{data}'
        payload = json.dumps({
            "publicApiKey": public_key,
            "secretKey": secret_key,
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authentication_key}',
        }

        # Make the API request
        try:
            response = requests.get(url, headers=headers, data=payload)
            response.raise_for_status()
            #_logger.info(f"Response from Intermo: {response.text}")
            return json.loads(response.text).get('paymentStatus', 'Unknown')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching payment status: {e}")
            return {'error': _("Failed to fetch payment status. Please try again.")}

    def intermo_make_payment_request(self, data):
        """Create a payment request using Intermo."""
        intermo = IntermoPosRequest(self.env)
        #_logger.info(f"Initiating payment request with data: {data}")

        # Fetch the Intermo configuration dynamically
        config = self.env['intermo.gateway.config'].search([], limit=1)
        if not config:
            raise UserError(_("Intermo Gateway Configuration is missing!"))

        try:
            # Try to get the access token
            response = intermo._get_access_token(payload=data)
            #_logger.info(f"Payment request response: {response}")

            # Validate response
            if not response or 'paymentlink' not in response:
                _logger.warning("Invalid response from Intermo API. Falling back to offline mode.")
                raise Exception("Invalid API response")

            # Generate QR code for online payment
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
                'offline_mode': False ,
                'paylink':response['paymentlink']
            }

        except Exception as e:
            # Fallback to offline mode in case of any error
            _logger.error(f"Error during payment request: {e}")
            #_logger.info("Generating offline payment link.")

            is_sandbox = config.mode == 'sandbox'
            auth_key = config.sandbox_authentication_key if is_sandbox else config.production_authentication_key
            public_key = config.sandbox_public_key if is_sandbox else config.production_public_key
            secret_key = config.sandbox_secret if is_sandbox else config.production_secret

            sensitiveData = {
                'amount': data.get('amount'),
                'authKey': auth_key,
                'publicKey': public_key,
                'secretKey': secret_key,
                'currency': data.get('currency', 'XOF')
            }

            try:
                loaded_public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
                sensitive_data_json = json.dumps(sensitiveData)
                encrypted_data = loaded_public_key.encrypt(
                    sensitive_data_json.encode('utf-8'),
                    padding.PKCS1v15()
                )
                encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')
                encrypted_data_urlencoded = urllib.parse.quote(encrypted_data_base64)

                apiUrl = "http://localhost:7777/odoo_offline/pay"
                paymentLink = f"{apiUrl}?data={encrypted_data_urlencoded}"

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(paymentLink)
                qr.make(fit=True)

                buffer = BytesIO()
                qr.make_image(fill='black', back_color='white').save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                return {
                    'qr_code': img_base64,
                    'payment_link': paymentLink,
                    'offline_mode': True  # Offline payment mode
                }

            except Exception as offline_error:
                _logger.error(f"Error generating offline payment link: {offline_error}")
                raise UserError(_("Failed to generate offline payment link. Please try again."))

        