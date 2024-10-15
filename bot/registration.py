import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.user_service import register_new_user
from bot.constants import REGISTER_VEHICLE, REGISTER_YEAR
from utils.localization import load_messages

logger = logging.getLogger(__name__)

# Load user's language or default to English
def get_user_language(context):
    return context.user_data.get('language_code', 'en')

# Registration flow step 1: Asking for name
async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    context.user_data['name'] = update.message.text
    await update.message.reply_text(messages['ask_vehicle_model'])
    return REGISTER_VEHICLE

# Registration flow step 2: Asking for vehicle model
async def register_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    context.user_data['vehicle_model'] = update.message.text
    await update.message.reply_text(messages['ask_vehicle_year'])
    return REGISTER_YEAR

# Registration flow step 3: Asking for year and registering the user
async def register_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    context.user_data['year'] = update.message.text
    telegram_name = update.effective_user.username
    name = context.user_data['name']
    vehicle_model = context.user_data['vehicle_model']
    year = context.user_data['year']

    # Register the user
    result = register_new_user(telegram_name, name, vehicle_model, year)
    if result:
        await update.message.reply_text(messages['registration_success'])
    else:
        await update.message.reply_text(messages['registration_failed'])

    # End the conversation
    return ConversationHandler.END

# Cancel registration
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language_code = get_user_language(context)
    messages = load_messages(language_code)

    await update.message.reply_text(messages['registration_canceled'])
    return ConversationHandler.END
