import logging
from telegram import Update
from telegram.ext import ContextTypes
from localization.TranslationLoader import TranslationLoader

logger = logging.getLogger(__name__)

def get_user_language(context):
    return context.user_data.get('language_code', 'en')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    translations = TranslationLoader()
    logger.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text(translations.get_translation('send_odometer_and_pump_photo', language_code))