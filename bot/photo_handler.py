import json
import logging
import os

import requests
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from cnst.conversation_state import FIRST_PHOTO
from llm.ClaudeClient import ClaudeClient
from localization.TranslationLoader import TranslationLoader
from models import VehicleData
from models.ImageInfo import ImageInfo
from utils.image_helper import encode_image, resize_image_data
from typing import Dict

logger = logging.getLogger(__name__)
translations = TranslationLoader()
photos_data = {}

JWT_TOKEN = os.getenv('JWT_TOKEN')

def get_user_language(context):
    return context.user_data.get('language_code', 'en')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    logger.info(f"Received a text message from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(translations.get_translation('start_message', language_code))


async def handle_photo(update, context):
    user_id = update.effective_user.id
    language_code = get_user_language(context)
    claude_client = ClaudeClient()

    if not context.user_data.get('odometer') and not context.user_data.get('fuel_pump'):
        file_id = update.message.photo[-1].file_id
        file = await context.bot.get_file(file_id)
        photo_content = requests.get(file.file_path).content
        base64_image = encode_image(photo_content)
        response = claude_client.classify_image(base64_image)
        first_image_entity = ImageInfo (
            imageData=base64_image,
            type= json.loads(response).get("classification"),
            confidence= json.loads(response).get("confidence", 0.0)
        )
        context.user_data[first_image_entity.type] = first_image_entity
        await update.message.reply_text(translations.get_translation('first_photo_received', language_code))
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
            confidence=json.loads(response).get("confidence", 0.0)
        )
        context.user_data[first_image_entity.type] = first_image_entity
        await update.message.reply_text(translations.get_translation('second_photo_received', language_code))
        await process_images(update, context, user_id)
        del context.user_data['photos']
        return ConversationHandler.END


async def process_images(update, context, user_id):
    language_code = get_user_language(context)
    claude_client = ClaudeClient()

    vehicle_data = VehicleData(
        vehicleId="7ea1d394-c739-4c77-9428-8b93e6535981",
        totalKm=0,
        lastLiters=0,
        lastCost=0,
        addInfo={"service": "Image processing", "location": "Automated"}
    )
    all_results = []

    photos_keys = ['fuel_pump', 'odometer']
    for key in photos_keys:
        if key == 'fuel_pump':
            photo = context.user_data[key]
            fuel_pump_result = claude_client.read_fuel_pump(photo.imageData)
            result = json.loads(fuel_pump_result)
            vehicle_data.lastLiters = result["volume"]
            all_results.append(fuel_pump_result)
            vehicle_data.add_image(
                image_data=resize_image_data(photo.imageData, 400),
                image_type="fuel_pump",
                confidence=result["confidence"],
                description="Fuel pump reading",
                add_info={}
            )
        elif key == 'odometer':
            photo = context.user_data[key]
            odometer_result = claude_client.read_fuel_pump(photo.imageData)
            result = json.loads(odometer_result)
            vehicle_data.lastLiters = result["volume"]
            all_results.append(odometer_result)
            vehicle_data.add_image(
                image_data=resize_image_data(photo.imageData, 400),
                image_type="odometer",
                confidence=result["confidence"],
                description="Odometer reading",
                add_info={}
            )

    print("All results:")
    print(json.dumps(all_results, indent=2))

    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = vehicle_data.to_dict()
    print(payload)
    # esponse = requests.post(f"{API_BASE_URL}/api/{APP_NAME}/consumings/", json=payload, headers=headers)

    await update.message.reply_text(translations.get_translation('process_complete', language_code))


