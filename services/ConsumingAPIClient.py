import json
import os
import logging
import requests
from dotenv import load_dotenv
from models.Owner import Owner

load_dotenv()

logger = logging.getLogger(__name__)


class ConsumingAPIClient:
    def __init__(self):
        self.jwt_token = os.getenv('JWT_TOKEN')
        self.api_base_url = os.getenv('API_BASE_URL')
        self.app_name = os.getenv('APP_NAME')
        self.headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }

    def get_events(self, telegram_name):
        try:
            response = requests.get(f"{self.api_base_url}/api/{self.app_name}/consumings/telegram/{telegram_name}", headers=self.headers)
            logger.info(f"Response content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if data and "payload" in data and "viewData" in data["payload"]:
                    doc_data = data["payload"]["viewData"]
                    return doc_data
            elif response.status_code == 404:
                logger.warning(f"User does not exist: {telegram_name}")
                return None
            else:
                return f"Error: {response.status_code}, Response: {response.text}"
        except requests.RequestException as e:
            logger.error(f"Error checking user by telegram name: {e}")
            return None
