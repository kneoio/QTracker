import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes
from services.user_service import fetch_owner_by_telegram_name, fetch_vehicle_by_owner_id
from bot.constants import REGISTER_NAME
from utils.llm import encode_image, send_to_claude
from utils.localization import load_messages

logger = logging.getLogger(__name__)

photos_data = {}


# Load user's language or default to English
def get_user_language(context):
    return context.user_data.get('language_code', 'en')


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text(messages['start_message'])


# Handle text messages that are not commands
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(messages['start_message'])


# Photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    telegram_name = update.effective_user.username
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    logger.info(f"Received a photo from user {user_id}.")

    # Check if the user exists by Telegram username
    owner = fetch_owner_by_telegram_name(telegram_name)
    if not owner:
        await update.message.reply_text(messages['registration_prompt'])
        return REGISTER_NAME

    # Fetch the vehicle information for the existing user
    vehicle_info = fetch_vehicle_by_owner_id(owner.id)
    if vehicle_info:
        brand = vehicle_info.get('brand')
        model = vehicle_info.get('model')
        vin = vehicle_info.get('vin')
        fuel_type = vehicle_info.get('fuel_type')

        await update.message.reply_text(
            f"Welcome back, {owner.telegram_name}! Here is your vehicle information:\n"
            f"Brand: {brand}\nModel: {model}\nVIN: {vin}\nFuel Type: {fuel_type}"
        )
    else:
        await update.message.reply_text(messages['vehicle_info_not_found'])

    # Fetch and encode the photo from Telegram
    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    photo_content = requests.get(file.file_path).content
    base64_image = encode_image(photo_content)

    # Send the image to Claude to determine its type (odometer or pump)
    image_type_prompt = messages['image_type_prompt']
    image_type_result = await send_to_claude(base64_image, image_type_prompt)

    if image_type_result:
        image_type_text = image_type_result[0].get('text', '').strip().lower()

        # Handle image type
        await handle_image_type(update, context, user_id, image_type_text, base64_image)


# Handle image type logic
async def handle_image_type(update, context, user_id, image_type_text, base64_image):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    if image_type_text == 'odometer':
        if 'odometer_image' in photos_data.get(user_id, {}):
            await update.message.reply_text(messages['odometer_exists'])
        else:
            photos_data.setdefault(user_id, {})['odometer_image'] = base64_image
            await update.message.reply_text(messages['odometer_received'])

    elif image_type_text == 'pump':
        if 'fuel_meter_image' in photos_data.get(user_id, {}):
            await update.message.reply_text(messages['pump_exists'])
        else:
            photos_data.setdefault(user_id, {})['fuel_meter_image'] = base64_image
            await update.message.reply_text(messages['pump_received'])
    else:
        await update.message.reply_text(messages['image_not_identified'])

    # Process both images if received
    if 'odometer_image' in photos_data.get(user_id, {}) and 'fuel_meter_image' in photos_data.get(user_id, {}):
        await process_images(update, context, user_id)


# Process odometer and fuel pump images
async def process_images(update, context, user_id):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    await update.message.reply_text(messages['process_complete'])

    # Analyze the odometer image for kilometers
    odometer_result = await send_to_claude(
        photos_data[user_id]["odometer_image"],
        "Please analyze this odometer image and provide the numeric value of kilometers or miles traveled based on the number displayed."
    )

    # Analyze the fuel pump image and distinguish between cost and liters
    fuel_result = await send_to_claude(
        photos_data[user_id]["fuel_meter_image"],
        """
        Please analyze this fuel pump meter image. It typically shows both the amount of fuel dispensed (in liters or gallons) and the total cost (in currency).
        Identify and extract the fuel volume, ensuring it corresponds to a unit like liters ('L') or gallons, not the cost.
        """
    )

    # Extract readings and respond with results
    odometer_reading = odometer_result[0].get('text') if odometer_result else None
    fuel_reading = fuel_result[0].get('text') if fuel_result else None

    if odometer_reading and fuel_reading:
        await update.message.reply_text(
            f"The vehicle has traveled {odometer_reading} kilometers/miles.\nYou have filled {fuel_reading} liters/gallons of fuel."
        )
    else:
        await update.message.reply_text(messages['invalid_readings'])

    # Clear the stored data for this user
    del photos_data[user_id]
