import json
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from bot.photo_handler import start, handle_text, handle_photo
from bot.constants import REGISTER_NAME, REGISTER_VEHICLE, REGISTER_YEAR
from bot.registration import cancel
from utils.localization import load_translations

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_language(update, context):
    if len(context.args) > 0:
        language_code = context.args[0].lower()
        context.user_data['language_code'] = language_code
        await update.message.reply_text(f"Language set to {language_code}.")
    else:
        await update.message.reply_text("Please provide a valid language code (e.g., 'en', 'pt').")

if __name__ == '__main__':
    logger.info("Starting the bot...")

    app = ApplicationBuilder().token(API_TOKEN).build()
    language_code = 'en'
    bot_messages = load_translations(language_code)
    registration_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
#            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
#            REGISTER_VEHICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_vehicle)],
#            REGISTER_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_year)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('setlanguage', set_language))
    app.add_handler(registration_conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot is running...")
    app.run_polling()
