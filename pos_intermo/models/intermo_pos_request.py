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
            dict: The API response.
        """
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

        _logger.info(f"Sending request to URL: http://localhost:7777/SandBox/v1/api/GetAccessToken with payload: {payload}")
        response = requests.post("http://localhost:7777/SandBox/v1/api/GetAccessToken", json=payload, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Error fetching access token: {response.text}")

        _logger.info(f"Received response: {response.json()}")
        return response.json()
