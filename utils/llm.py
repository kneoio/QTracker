import os
import base64
import logging
import requests

logger = logging.getLogger(__name__)

# Utility function to encode image content to base64
def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

# Utility function to send a request to Claude API
async def send_to_claude(base64_image, task_description):
    payload = {
        "model": os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1024")),
        "system": task_description,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                {"type": "text", "text": task_description}
            ]
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
        "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01")
    }

    try:
        response = requests.post(os.getenv('CLAUDE_API_ENDPOINT'), json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('content')
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None
