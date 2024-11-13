from odoo.exceptions import UserError
from odoo import fields, models, api, _
from odoo.http import request
from .intermo_pos_request import IntermoPosRequest
import qrcode
from io import BytesIO
import base64
import requests
import random
import logging
import json

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('intermo_public_key')
        result['search_params']['fields'].append('intermo_plugin_key')
        result['search_params']['fields'].append('intermo_auth_key')
        result['search_params']['fields'].append('intermo_secret_key')
        result['search_params']['fields'].append('intermo_secret_key')
        return result

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    intermo_mode = fields.Selection([('test', 'Sandbox'), ('live', 'Production')])
    intermo_public_key = fields.Char('Intermo Public Key')

    def _get_default_plugin_key_intermo(self):

        # Function to generate a random 18-digit number
        def generate_random_18_digit(number_of_digit):
            return random.randint((10 ** (number_of_digit - 1)), ((10 ** number_of_digit) - 1))

        # Generate and print the number
        random_number = generate_random_18_digit(18)
        return random_number


    intermo_plugin_key = fields.Char('Intermo Plugin Key', default=_get_default_plugin_key_intermo)
    intermo_auth_key = fields.Char('Intermo Auth Token')
    intermo_secret_key = fields.Char('Intermo Secret Key')




    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('intermo', 'Intermo')]

    def intermo_get_payment_status(self, data):
        _logger.info(f"check {data}")
        
        url = f'https://prodapi.intermo.net/api/v1/pos/status/{data}'
        # return "payment_successed"
        if self.intermo_mode == 'test':
            url = f'http://localhost:7777/api/v1/pos/status/{data}'
        else:
            url = f'http://localhost:7777/api/v1/pos/status/{data}'

        payload = json.dumps({
            "publicApiKey": self.intermo_public_key,
            "secretKey": self.intermo_secret_key
            # 'pluginkey' : self.intermo_plugin_key
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.intermo_auth_key}'
        }

        _logger.info("Testing on line 73 code...........")
        # Use `params` instead of `data` for GET requests
        #response = requests.request("GET",url, headers=headers, data=payload)
        # url = "http://localhost:7777/api/v1/pos/status/eyJhbGciOiJIUzI1NiJ9.eyJpcEFkZHJlc3MiOiIwOjA6MDowOjA6MDowOjEiLCJtX0lkIjoxMDAwMjcsInR4bl9pZCI6Im9zRzE2ZkdhbHdmT25BOWIiLCJzYW5kYm94TW9kZSI6dHJ1ZSwiaWF0IjoxNzMwNzMxOTUxLCJleHAiOjE3MzA3MzU1NTF9.wv3F0YDN-Fe87t6RfeBiHOfJU81t5VoqHsCRQYnfI-8"

        # payload = json.dumps({
        # "publicApiKey": "Cxdhpfa1PXOEpSC4OolJ6P46Yg4a5tBvtEcKnejOj0",
        # "secretKey": "bvmUXhOGYodJY9l9qJtCBXlQZYdKz7TbyMlfPF9HaQ"
        # })
        # headers = {
        # 'Content-Type': 'application/json',
        # 'Authorization': 'Bearer AztlQdnChLPRTC6HWcivlaKfusDkXiV29bU3MnHalQ'
        # }

        response = requests.request("GET", url, headers=headers, data=payload)
        # _logger.info("Response :: ", response.text)
        # Print the response to see the result
        return json.loads(response.text)['paymentStatus']
        return "payment_successed"


    def intermo_make_payment_request(self, data):
        intermo = IntermoPosRequest(self)
        body = data
        response = intermo._call_intermo(endpoint="pay", payload=body, token=self.intermo_auth_key, intermo_mode=self.intermo_mode)
        print("=----------------33333--------", data)
        if response.get('paymentlink') and not response.get('errorCode'):

            qr = qrcode.QRCode(
                version=1,  # Controls the size of the QR code
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
                box_size=10,  # Size of each box in pixels
                border=4,  # Border size in boxes
            )

            value_after_pay = response['paymentlink'].split('/pay/')[1]

            # Add data (URL) to the QR code
            qr.add_data(response['paymentlink'])
            _logger.info(f"QR Code Payment Link {response['paymentlink']}")
            _logger.info(f"JWT Token {value_after_pay}")
            qr.make(fit=True)

            # Create an image from the QR code
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Get the bytes of the image
            img_bytes = buffer.getvalue()

            # Convert the image bytes to a base64 string
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            return {'qr_code': img_base64,'jwt_token': value_after_pay }

        default_error_msg = _('Intermo POS payment request expected errorCode not found in the response')
        error = response.get('errorMessage') or default_error_msg
        return {'error': str(error)}


    def intermo_cancel_payment_request(self, data):

        return {'errorMessage': ""}
