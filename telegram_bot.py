import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
CLAUDE_API_ENDPOINT = os.getenv('CLAUDE_API_ENDPOINT')
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

photos_data = {}  # Store photos (odometer and fuel meter) for each user

# Helper function to encode image content to base64
def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text('Please send a photo of the odometer first.')

# Helper function to send a request to Claude API
async def send_to_claude(base64_image, task_description):
    payload = {
        "model": os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1024")),
        "system": task_description,
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
                        "text": task_description
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01")
    }

    try:
        response = requests.post(CLAUDE_API_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('content')
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None

# Photo handler for odometer and fuel pump meter
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Received a photo from user {username} (ID: {user_id}).")

    # Fetch photo from Telegram server
    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    photo_content = requests.get(file.file_path).content

    # Encode the image content to base64
    base64_image = encode_image(photo_content)

    # Check if we already have an odometer photo for this user
    if user_id not in photos_data:
        # First photo is for the odometer
        photos_data[user_id] = {"odometer_image": base64_image}
        await update.message.reply_text("Odometer photo received. Now, please send a photo of the fuel pump meter.")
    elif "fuel_meter_image" not in photos_data[user_id]:
        # Second photo is for the fuel pump meter
        photos_data[user_id]["fuel_meter_image"] = base64_image
        await update.message.reply_text("Fuel pump meter photo received. Processing both photos...")

        # Process the odometer image
        odometer_result = await send_to_claude(photos_data[user_id]["odometer_image"],
                                               "Please analyze this odometer image and provide the numeric value of kilometers traveled.")
        if odometer_result and isinstance(odometer_result, list):
            odometer_reading = odometer_result[0].get('text')
        else:
            odometer_reading = None

        fuel_result = await send_to_claude(
            photos_data[user_id]["fuel_meter_image"],
            "Please analyze this fuel pump meter image and extract the numeric value that represents the amount of fuel dispensed in liters. "
            "The correct value will be labeled with the word 'LITRES' or the letter 'L'. Ignore other numbers such as the cost or price per liter."
        )

        if fuel_result and isinstance(fuel_result, list):
            fuel_reading = fuel_result[0].get('text')
        else:
            fuel_reading = None

        # Display the results
        if odometer_reading and fuel_reading:
            await update.message.reply_text(f"The vehicle has traveled {odometer_reading} kilometers.\n"
                                            f"You have filled {fuel_reading} liters of fuel.")
        else:
            await update.message.reply_text("Could not detect valid readings from one or both images. Please try again with clearer images.")

        # Clear the user's photo data
        del photos_data[user_id]
    else:
        await update.message.reply_text("You have already submitted both photos. Please start over by sending a new odometer photo.")

# Text message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Received a text message from user {user_id}: {update.message.text}")
    await update.message.reply_text('Please send a photo of the odometer for analysis.')

if __name__ == '__main__':
    logger.info("Starting the bot...")

    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot is running...")
    app.run_polling()
