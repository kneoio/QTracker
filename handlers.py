import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes
from utils import encode_image, send_to_claude

logger = logging.getLogger(__name__)

photos_data = {}


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text('Please send a photo of the odometer or the fuel pump meter.')


# Photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Received a photo from user {user_id}.")

    # Fetch and encode the photo from Telegram
    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    photo_content = requests.get(file.file_path).content
    base64_image = encode_image(photo_content)

    # Step 1: Send the image to Claude to determine its type (odometer or pump)
    image_type_prompt = """
    Please analyze this image and determine if it is an odometer or a fuel pump meter.
    Respond only with one word: "odometer" or "pump".
    """
    image_type_result = await send_to_claude(base64_image, image_type_prompt)

    if image_type_result:
        image_type_text = image_type_result[0].get('text', '').strip().lower()

        # Step 2: Force the result to either 'odometer' or 'pump'
        if image_type_text == 'odometer':
            if 'odometer_image' in photos_data.get(user_id, {}):
                await update.message.reply_text("You already submitted an odometer image. Please send a pump image.")
            else:
                photos_data.setdefault(user_id, {})['odometer_image'] = base64_image
                await update.message.reply_text(
                    "Odometer photo received. Now, please send a photo of the fuel pump meter.")

        elif image_type_text == 'pump':
            if 'fuel_meter_image' in photos_data.get(user_id, {}):
                await update.message.reply_text("You already submitted a pump image. Please send an odometer image.")
            else:
                photos_data.setdefault(user_id, {})['fuel_meter_image'] = base64_image
                await update.message.reply_text(
                    "Fuel pump meter photo received. Now, please send a photo of the odometer.")

        else:
            await update.message.reply_text(
                "The image could not be identified as an odometer or a pump. Please try again with a clearer image.")

    # Step 3: If both images are received, process them
    if 'odometer_image' in photos_data.get(user_id, {}) and 'fuel_meter_image' in photos_data.get(user_id, {}):
        await update.message.reply_text("Processing both photos...")

        # Analyze the odometer image for kilometers
        odometer_result = await send_to_claude(photos_data[user_id]["odometer_image"],
                                               "Please analyze this odometer image and provide the numeric value of kilometers traveled.")

        # Analyze the fuel pump image and distinguish between cost and liters
        fuel_result = await send_to_claude(photos_data[user_id]["fuel_meter_image"], """
        Please analyze this fuel pump meter image. It may show both the amount of fuel dispensed in liters and the total cost in currency. 
        Determine which number refers to liters by looking for labels such as 'liters', 'L', or 'gallons', and which number refers to cost by looking for 'cost', 'sale', or currency symbols. 
        Return the value corresponding to liters and confirm it is the fuel amount, not the cost.
        """)

        # Extract readings
        odometer_reading = odometer_result[0].get('text') if odometer_result else None
        fuel_reading = fuel_result[0].get('text') if fuel_result else None

        # Respond with results
        if odometer_reading and fuel_reading:
            await update.message.reply_text(
                f"The vehicle has traveled {odometer_reading} kilometers.\nYou have filled {fuel_reading} liters of fuel.")
        else:
            await update.message.reply_text(
                "Could not detect valid readings from one or both images. Please try again with clearer images.")

        # Clear the stored data for this user
        del photos_data[user_id]


# Text message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text('Please send a photo of the odometer or the fuel pump meter for analysis.')
