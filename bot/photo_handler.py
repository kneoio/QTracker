import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes
from services.user_service import fetch_owner_by_telegram_name
from utils.llm import encode_image, send_to_claude
from utils.localization import load_translations

logger = logging.getLogger(__name__)

photos_data = {}

def get_user_language(context):
    return context.user_data.get('language_code', 'en')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_translations(language_code)
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text(messages['start_message'])

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_translations(language_code)
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(messages['start_message'])

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    telegram_name = update.effective_user.username
    language_code = get_user_language(context)
    bot_messages = load_translations(language_code)

    logger.info(f"Received a photo from user {user_id}.")

    owner = fetch_owner_by_telegram_name(telegram_name)
    await update.message.reply_text(bot_messages['hello'] + owner)

    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    photo_content = requests.get(file.file_path).content
    base64_image = encode_image(photo_content)

    image_type_prompt = bot_messages[
        'image_type_prompt']
    image_type_result = await send_to_claude(base64_image, image_type_prompt)

    if image_type_result:
        image_type_text = image_type_result[0].get('text', '').strip().lower()
        await handle_image_type(update, context, user_id, image_type_text, base64_image)


async def handle_image_type(update, context, user_id, image_type_text, base64_image):
    language_code = get_user_language(context)
    messages = load_translations(language_code)

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

    # Step 2: If it's something else, check if it's a vehicle or logo
    elif image_type_text == 'something else':
        # Further check if it's a vehicle or vehicle logo
        vehicle_check_prompt = messages['vehicle_check_prompt']  # "Check if this is a vehicle or logo."
        vehicle_check_result = await send_to_claude(base64_image, vehicle_check_prompt)

        if vehicle_check_result:
            vehicle_check_text = vehicle_check_result[0].get('text', '').strip().lower()

            if vehicle_check_text == 'vehicle':
                # Ask user to register the vehicle
                await update.message.reply_text(messages['vehicle_registration_prompt'])

            elif vehicle_check_text == 'logo':
                # Try to recognize the logo for registration
                logo_recognition_prompt = messages[
                    'logo_recognition_prompt']  # "Identify the vehicle manufacturer logo in this image."
                logo_result = await send_to_claude(base64_image, logo_recognition_prompt)
                logo_name = logo_result[0].get('text', '') if logo_result else messages['unknown_logo']
                await update.message.reply_text(
                    f"It looks like the logo of {logo_name}. Would you like to register a vehicle under this brand?")

            else:
                await update.message.reply_text(messages['image_not_identified'])

    if 'odometer_image' in photos_data.get(user_id, {}) and 'fuel_meter_image' in photos_data.get(user_id, {}):
        await process_images(update, context, user_id)

async def process_images(update, context, user_id):
    language_code = get_user_language(context)
    messages = load_translations(language_code)

    await update.message.reply_text(messages['process_complete'])

    # Analyze the odometer image for kilometers
    odometer_result = await send_to_claude(
        photos_data[user_id]["odometer_image"],
        "Please analyze this odometer image and provide the numeric value of kilometers or miles traveled based on the number displayed."
    )

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
