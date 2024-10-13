import requests
import base64
import os
from dotenv import load_dotenv
from utils.logging import logger

load_dotenv()

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        logger.error(f"Failed to read image file: {e}")
        return None

def ask_claude(image_path):
    url = os.getenv("CLAUDE_API_ENDPOINT")
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not url or not api_key:
        logger.error("API endpoint or API key is missing in .env file")
        return None

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    payload = {
        "model": os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1024")),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please analyze this image with a liquid crystal display (LCD) and provide the numeric value of the kilometers traveled. The value should be at least 5 digits, potentially including a distinctive decimal part (e.g., .0 or .5), without any additional text."
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01")
    }

    logger.info("Sending request to Claude API")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")
        return None

    if response.status_code == 200:
        result = response.json()['content'][0]['text']
        logger.info(f"Successfully received response from Claude API")
        return result
    else:
        logger.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    image_path = os.getenv("ODOMETER_IMAGE_PATH")
    if not image_path:
        logger.error("ODOMETER_IMAGE_PATH is not set in .env file")
    else:
        logger.info(f"Processing image: {image_path}")
        result = ask_claude(image_path)
        if result:
            logger.info(f"The vehicle has traveled {result} kilometers.")
        else:
            logger.error("Failed to process the image")