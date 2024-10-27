import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from localization.TranslationLoader import TranslationLoader
from services.ConsumingAPIClient import ConsumingAPIClient

logger = logging.getLogger(__name__)


def get_user_language(context):
    return context.user_data.get('language_code', 'en')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    translations = TranslationLoader()
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text(translations.get_translation('send_odometer_and_pump_photo', language_code))


async def list_events(update: Update, context: CallbackContext):
    user_name = update.effective_user.username
    language_code = get_user_language(context)
    api_client = ConsumingAPIClient()
    events = api_client.get_events(user_name)

    if events:
        entries = events.get('entries', [])
        if entries:
            event_details = []
            for event in entries:
                event_text = (
                    f"Date: {event['regDate']}\n"
                    f"Last Liters: {event['lastLiters']}\n"
                    f"Total Km: {event['totalKm']}\n"
                    "-------------------------"
                )
                event_details.append(event_text)

            response_text = "\n".join(event_details)
            await update.message.reply_text(f"Your events:\n{response_text}")
        else:
            await update.message.reply_text("You have no events.")
