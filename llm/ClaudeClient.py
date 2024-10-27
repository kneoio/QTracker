import json
import os
import logging
import anthropic

logger = logging.getLogger(__name__)


class ClaudeClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))

        if not self.api_key:
            raise ValueError("API key not found. Please set the ANTHROPIC_API_KEY environment variable.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def classify_image(self, image_data):
        logger.info("Sending image data to classify_image")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                        {"type": "text",
                         "text": "Please classify this image as 'fuel_pump', 'odometer', or 'undefined'. Respond only with a JSON object containing 'classification' and 'confidence' fields. If the image is not clearly a fuel pump or odometer, set 'classification' to 'undefined' with a confidence of 0.0."}
                    ]
                }
            ]
        )

        raw_text = response.content[0].text
        logger.info(f"Raw JSON response text: {raw_text}")

        try:
            result = json.loads(raw_text)
            classification = result.get("classification")
            confidence = result.get("confidence")
            logger.info(f"Classification: {classification}, Confidence: {confidence}")
            return json.dumps({"classification": classification, "confidence": confidence})
        except (json.JSONDecodeError, TypeError, KeyError):
            logger.error("Failed to parse JSON from Claude's response")
            return json.dumps({"classification": "undefined", "confidence": 0.0})

    def read_odometer(self, image_data):
        logger.info("Sending image data to read_odometer")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "Please read the odometer value from this image. Respond only with a JSON object like "
                                "{\"total_km\": <value>, \"confidence\": <value>}."
                                " Note that odometer readings are typically whole numbers, not decimal values. "
                                "Avoid outputs like 130.16; the correct reading should be 13060. Decimal values are rare, "
                                "and any fractional number generally has distinct visual indicators such as different colors, "
                                "spaces, or a visible dot. If uncertain, default to whole numbers."
                            )
                        }
                    ]
                }
            ]
        )

        raw_text = response.content[0].text
        logger.info(f"Raw JSON response text: {raw_text}")

        try:
            result = json.loads(raw_text)
            total_km = result.get("total_km")
            confidence = result.get("confidence")
            logger.info(f"Total KM: {total_km}, Confidence: {confidence}")
            return json.dumps({"total_km": total_km, "confidence": confidence})
        except (json.JSONDecodeError, TypeError, KeyError):
            logger.error("Failed to parse JSON from Claude's response for odometer")
            return json.dumps({"total_km": 0.0, "confidence": 0.0})

    def read_fuel_pump(self, image_data):
        logger.info("Sending image data to read_fuel_pump")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                        {"type": "text",
                         "text": "Please read the fuel volume, cost, and currency from this fuel pump image and respond"
                                 " only with a JSON object like "
                                 "{\"volume\": <value>, \"cost\": <value>, \"currency\": \"<currency>\", \"confidence\": <value>}."}
                    ]
                }
            ]
        )

        raw_text = response.content[0].text
        logger.info(f"Raw JSON response text: {raw_text}")

        try:
            result = json.loads(raw_text)
            volume = result.get("volume")
            cost = result.get("cost")
            currency = result.get("currency")
            confidence = result.get("confidence")
            logger.info(f"Volume: {volume}, Cost: {cost}, Currency: {currency}, Confidence: {confidence}")
            return json.dumps({
                "volume": volume,
                "cost": cost,
                "currency": currency,
                "confidence": confidence
            })
        except (json.JSONDecodeError, TypeError, KeyError):
            logger.error("Failed to parse JSON from Claude's response for fuel pump")
            return json.dumps({
                "volume": 0.0,
                "cost": 0.0,
                "currency": "unknown",
                "confidence": 0.0
            })
