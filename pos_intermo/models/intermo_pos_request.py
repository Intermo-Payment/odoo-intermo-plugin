import requests
import logging

_logger = logging.getLogger(__name__)

class IntermoPosRequest:
    def __init__(self, env):
        """
        Initialize the IntermoPosRequest class with the Odoo environment.
        """
        self.env = env

    def _get_access_token(self, payload):
        """
        Retrieve access token for Intermo integration.
        This method uses the Intermo Gateway configuration in Odoo.

        Args:
            payload (dict): The payload to send for authentication.

        Returns:
            dict: The API response or an error message.
        """
        try:
            config = self.env['intermo.gateway.config'].search([], limit=1)
            if not config:
                raise ValueError("No Intermo Gateway Configuration found")

            # Determine the endpoint based on the mode
            # url = (
            #     config.sandbox_public_key
            #     if config.mode == 'sandbox'
            #     else config.production_public_key
            # )
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.sandbox_authentication_key if config.mode == "sandbox" else config.production_authentication_key}',
            }

            #_logger.info(f"Sending request to URL: http://localhost:7777/SandBox/v1/api/GetAccessToken with payload: {payload}")
            response = requests.post("http://localhost:7777/SandBox/v1/api/GetAccessToken", json=payload, headers=headers)
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

            #_logger.info(f"Received response: {response.json()}")
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            _logger.error(f"HTTP error occurred: {http_err}")
            return {'error': f"HTTP error occurred: {http_err}"}
        except requests.exceptions.ConnectionError as conn_err:
            _logger.error(f"Connection error occurred: {conn_err}")
            return {'error': f"Connection error occurred: {conn_err}"}
        except requests.exceptions.Timeout as timeout_err:
            _logger.error(f"Timeout error occurred: {timeout_err}")
            return {'error': f"Timeout error occurred: {timeout_err}"}
        except Exception as err:
            _logger.error(f"An error occurred: {err}")
            return {'error': f"An error occurred: {err}"}

