import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.constants import REGISTER_VEHICLE, REGISTER_YEAR


logger = logging.getLogger(__name__)

# Load user's language or default to English
def get_user_language(context):
    return context.user_data.get('language_code', 'en')


# Registration flow step 2: Asking for vehicle model
async def register_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_translations(language_code)

    context.user_data['vehicle_model'] = update.message.text
    await update.message.reply_text(messages['ask_vehicle_year'])
    return REGISTER_YEAR


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_translations(language_code)

    await update.message.reply_text(messages['registration_canceled'])
    return ConversationHandler.END
