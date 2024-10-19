import json
import os
import logging
import requests
from dotenv import load_dotenv
import anthropic
from models.owner import Owner

logger = logging.getLogger(__name__)
load_dotenv()

JWT_TOKEN = os.getenv('JWT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL')
APP_NAME = os.getenv('APP_NAME')

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
USER_CHECK_ENDPOINT = f"{API_BASE_URL}/api/{APP_NAME}/owners/telegram"
USER_REGISTRATION_ENDPOINT = f"{API_BASE_URL}/api/{APP_NAME}/owners/telegram/"
USER_VEHICLE_ENDPOINT = f"{API_BASE_URL}/api/{APP_NAME}/users/{{user_id}}/vehicles"  # Use 'vehicles' instead of 'vehicle'
tools = []

def load_tool_definitions(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as file:
                tools.append(json.load(file))
    return tools


def fetch_vehicle_by_owner_id(telegram_name, email=None, phone=None, country=None, birth_date=None):
    messages = [
        {"role": "user",
         "content": f"Check if user with telegram name '{telegram_name}' exists. If not, register the user."}
    ]

    while True:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=messages,
            tools=tools
        )

        if response.stop_reason == "tool_use":
            tool_use = response.content[-1]

            if tool_use.name == "check_user":
                url = f"{USER_CHECK_ENDPOINT}/{tool_use.input['telegramName']}"
                logger.info(f"Sending GET request to: {url}")
                logger.info(f"Request payload: {json.dumps(tool_use.input, indent=2)}")

                try:
                    api_response = requests.get(url)
                    logger.info(f"Response status code: {api_response.status_code}")
                    logger.info(f"Response content: {api_response.text}")

                    if api_response.status_code == 200:
                        data = api_response.json()
                        if data and "payload" in data and "docData" in data["payload"]:
                            doc_data = data["payload"]["docData"]
                            return Owner(
                                telegram_name=doc_data.get('telegramName')
                            )
                    elif api_response.status_code == 404:
                        logger.warning(f"User does not exist: {telegram_name}")
                    else:
                        logger.error(f"Error: {api_response.status_code}, Response: {api_response.text}")
                        return None
                except requests.RequestException as e:
                    logger.error(f"Error fetching owner by telegram name: {e}")
                    return None

            elif tool_use.name == "register_user":
                if not all([email, phone, country, birth_date]):
                    logger.error("Missing required information for registration")
                    return None
                payload = {
                    "telegramName": telegram_name
                }

                logger.info(f"Sending POST request to register new user: {json.dumps(payload, indent=2)}")

                try:
                    api_response = requests.post(USER_REGISTRATION_ENDPOINT, json=payload)
                    logger.info(f"Response status code: {api_response.status_code}")
                    logger.info(f"Response content: {api_response.text}")

                    if api_response.status_code == 200:
                        return fetch_owner_by_telegram_name(telegram_name)  # Fetch the newly registered user
                    else:
                        logger.error(
                            f"Error registering user: {api_response.status_code}, Response: {api_response.text}")
                        return None
                except requests.RequestException as e:
                    logger.error(f"Error registering new user: {e}")
                    return None

            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": "Tool execution completed."
                }]
            })
        else:
            logger.warning("No tool use in response")
            return None

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
tools = load_tool_definitions('tools')