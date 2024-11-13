import requests
import logging

from odoo import _
REQUEST_TIMEOUT = 10

_logger = logging.getLogger(__name__)

class IntermoPosRequest:
    def __init__(self, payment_method):
        self.payment_method = payment_method
        self.session = requests.Session()

    def _intermo_get_endpoint(self, intermo_mode):
        if intermo_mode == 'test':
            return 'http://localhost:7777/SandBox/v1/api/GetAccessToken'
        else:
            return 'http://localhost:7777/SandBox/v1/api/GetAccessToken'


    def _call_intermo(self, endpoint, payload, token, intermo_mode):
       
        endpoint = f"{self._intermo_get_endpoint(intermo_mode)}"
        try:
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = self.session.post(endpoint, json=payload, headers=headers)
            print("==================-----------------", response)
            response.raise_for_status()
            res_json = response.json()
        except requests.exceptions.RequestException as error:
            _logger.warning("Cannot connect with Intermo POS. Error: %s", error)
            return {'errorMessage': str(error)}
        except ValueError as error:
            _logger.warning("Cannot decode response json. Error: %s", error)
            return {'errorMessage': _("Cannot decode Intermo POS response")}
        return res_json
