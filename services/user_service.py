import requests
import logging

from models.owner import Owner

logger = logging.getLogger(__name__)

USER_CHECK_ENDPOINT = "https://your-api-endpoint/users"  # Replace with your actual endpoint
USER_REGISTRATION_ENDPOINT = "https://your-api-endpoint/users/register"  # Replace with your actual endpoint
USER_VEHICLE_ENDPOINT = "https://your-api-endpoint/users/{user_id}/vehicle"  # Replace with your actual endpoint

def fetch_owner_by_telegram_name(telegram_name):
    """Fetch owner data from the API by Telegram name."""
    try:
        response = requests.get(f"{USER_CHECK_ENDPOINT}?telegramName={telegram_name}")
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        if data:
            return Owner.from_response(data)
        else:
            logger.warning(f"No owner found with telegram name: {telegram_name}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching owner by telegram name: {e}")
        return None

def register_new_user(telegram_name, name, vehicle_model, year):
    """Register a new user by sending a POST request with the user details."""
    payload = {
        "telegramName": telegram_name,
        "name": name,
        "vehicleModel": vehicle_model,
        "year": year
    }

    try:
        response = requests.post(USER_REGISTRATION_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()  # Return the response, assuming it contains the new user's data
    except requests.RequestException as e:
        logger.error(f"Error registering new user: {e}")
        return None


def fetch_vehicle_by_owner_id(owner_id):
    """Fetch vehicle data for the given owner ID."""
    try:
        response = requests.get(USER_VEHICLE_ENDPOINT.format(user_id=owner_id))
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        vehicle_data = response.json()  # Parse the JSON response
        return {
            "owner_id": vehicle_data.get('ownerId'),
            "vin": vehicle_data.get('vin'),
            "vehicle_type": vehicle_data.get('vehicleType'),
            "brand": vehicle_data.get('brand'),
            "model": vehicle_data.get('model'),
            "fuel_type": vehicle_data.get('fuelType'),
            "status": vehicle_data.get('status'),
            "localized_name": vehicle_data.get('localizedName')
        }
    except requests.RequestException as e:
        logger.error(f"Error fetching vehicle data for user {owner_id}: {e}")
        return None
