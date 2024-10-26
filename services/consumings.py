import os
import requests
import logging

logger = logging.getLogger(__name__)


class VehicleDataAPIClient:
    def __init__(self):
        self.jwt_token = os.getenv('JWT_TOKEN')
        self.api_base_url = os.getenv('API_BASE_URL')
        self.app_name = os.getenv('APP_NAME')

        if not all([self.jwt_token, self.api_base_url, self.app_name]):
            raise ValueError("Required environment variables are not set.")

    def send_data(self, payload):
        url = f"{self.api_base_url}/api/{self.app_name}/consumings/"
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }

        try:
            logger.info(f"Sending data to {url}")
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                logger.info(f"Data sent successfully: {response.status_code} - {response.text}")
                return response
            else:
                logger.warning(f"Unexpected response code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send data: {e}")
            return None
