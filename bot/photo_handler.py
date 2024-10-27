import json
import logging

import requests
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from cnst.conversation_state import FIRST_PHOTO
from llm.ClaudeClient import ClaudeClient
from localization.TranslationLoader import TranslationLoader
from models import VehicleData
from models.ImageInfo import ImageInfo
from services.UserAPIClient import UserAPIClient
from services.VehicleDataAPIClient import VehicleDataAPIClient
from utils.image_helper import encode_image, resize_image_data

logger = logging.getLogger(__name__)
translations = TranslationLoader()
photos_data = {}


def get_user_language(context):
    return context.user_data.get('language_code', 'en')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(translations.get_translation('start_message', language_code))


async def handle_photo(update, context):
    user_name = update.effective_user.username
    language_code = get_user_language(context)
    claude_client = ClaudeClient()
    user_api_client = UserAPIClient()
    owner = user_api_client.check_user(user_name)
    if owner is None:
        owner = user_api_client.register_user(user_name)

    print(owner.get_first_vehicle())
    context.user_data['owner'] = owner
    if not context.user_data.get('odometer') and not context.user_data.get('fuel_pump'):
        file_id = update.message.photo[-1].file_id
        file = await context.bot.get_file(file_id)
        photo_content = requests.get(file.file_path).content
        base64_image = encode_image(photo_content)
        response = claude_client.classify_image(base64_image)
        first_image_entity = ImageInfo(
            imageData=base64_image,
            type=json.loads(response).get("classification"),
            confidence=json.loads(response).get("confidence", 0.0),
            numOfSeq=1
        )
        context.user_data[first_image_entity.type] = first_image_entity
        await update.message.reply_text(translations.get_translation('please_send_second_photo', language_code))

        return FIRST_PHOTO

    else:
        file_id = update.message.photo[-1].file_id
        file = await context.bot.get_file(file_id)
        photo_content = requests.get(file.file_path).content
        base64_image = encode_image(photo_content)
        claude_client = ClaudeClient()
        response = claude_client.classify_image(base64_image)
        first_image_entity = ImageInfo(
            imageData=base64_image,
            type=json.loads(response).get("classification"),
            confidence=json.loads(response).get("confidence", 0.0),
            numOfSeq=2
        )
        context.user_data[first_image_entity.type] = first_image_entity
        await process_images(update, context, user_name)
        return ConversationHandler.END


async def process_images(update, context, user_id):
    language_code = get_user_language(context)
    claude_client = ClaudeClient()
    vehicle_data_api_client = VehicleDataAPIClient()
    await update.message.reply_text(translations.get_translation('photo_processing', language_code))
    owner = context.user_data['owner']
    vehicle_data = VehicleData(
        vehicleId=owner.get_first_vehicle()['id'],
        totalKm=0,
        lastLiters=0,
        lastCost=0,
        addInfo={"service": "Image processing", "location": "Automated"}
    )

    photos_keys = ['fuel_pump', 'odometer']
    for key in photos_keys:
        photo = context.user_data[key]

        if key == 'fuel_pump':
            result = json.loads(claude_client.read_fuel_pump(photo.imageData))
            vehicle_data.lastLiters = result["volume"]
            vehicle_data.lastCost = result["cost"]
        elif key == 'odometer':
            result = json.loads(claude_client.read_odometer(photo.imageData))
            vehicle_data.totalKm = result["total_km"]

        vehicle_data.add_image(photo, True)

    response = vehicle_data_api_client.send_data(vehicle_data.to_dict())
    if response:
        try:
            response_json = response.json()
            liters = response_json.get('litersPerHundred')
            if liters > 0:
                formatted_response = (
                    f"Total Trip: {response_json.get('totalTrip')}\n"
                    f"Liters Per Hundred: {liters}"
                )
            else:
                formatted_response = translations.get_translation('not_enough_data', language_code)
        except ValueError:
            formatted_response = f"Response Text: {response.text}"

        await update.message.reply_text(formatted_response)
    else:
        print(response)
        await update.message.reply_text(translations.get_translation('process_failed', language_code))

    for key in ['fuel_pump', 'odometer']:
        del context.user_data[key]
