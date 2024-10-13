import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import encode_image, send_to_claude

logger = logging.getLogger(__name__)

photos_data = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text('Please send a photo of the odometer first.')

# Photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Received a photo from user {user_id}.")

    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    photo_content = requests.get(file.file_path).content
    base64_image = encode_image(photo_content)

    if user_id not in photos_data:
        photos_data[user_id] = {"odometer_image": base64_image}
        await update.message.reply_text("Odometer photo received. Now, please send a photo of the fuel pump meter.")
    elif "fuel_meter_image" not in photos_data[user_id]:
        photos_data[user_id]["fuel_meter_image"] = base64_image
        await update.message.reply_text("Fuel pump meter photo received. Processing both photos...")

        odometer_result = await send_to_claude(photos_data[user_id]["odometer_image"], "Please analyze this odometer image and provide the numeric value of kilometers traveled.")
        fuel_result = await send_to_claude(photos_data[user_id]["fuel_meter_image"], "Please analyze this fuel pump meter image and extract the numeric value representing the fuel amount in liters.")

        odometer_reading = odometer_result[0].get('text') if odometer_result else None
        fuel_reading = fuel_result[0].get('text') if fuel_result else None

        if odometer_reading and fuel_reading:
            await update.message.reply_text(f"The vehicle has traveled {odometer_reading} kilometers.\nYou have filled {fuel_reading} liters of fuel.")
        else:
            await update.message.reply_text("Could not detect valid readings from one or both images. Please try again with clearer images.")

        del photos_data[user_id]
    else:
        await update.message.reply_text("You have already submitted both photos. Please start over by sending a new odometer photo.")

# Text message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text('Please send a photo of the odometer for analysis.')
