import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv

from bot.photo_handler import start, handle_text, handle_photo
from bot.registration import register_name, register_vehicle, register_year, cancel
from bot.constants import REGISTER_NAME, REGISTER_VEHICLE, REGISTER_YEAR
from utils.localization import load_messages

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle setting the user's preferred language
async def set_language(update, context):
    # Extract the language code from the message (assuming /setlanguage <lang_code>)
    if len(context.args) > 0:
        language_code = context.args[0].lower()
        # Store the language preference (you can save it in user data or a database)
        context.user_data['language_code'] = language_code
        await update.message.reply_text(f"Language set to {language_code}.")
    else:
        await update.message.reply_text("Please provide a valid language code (e.g., 'en', 'pt').")

if __name__ == '__main__':
    logger.info("Starting the bot...")

    app = ApplicationBuilder().token(API_TOKEN).build()

    # Load the default language messages (you can make this dynamic per user in practice)
    language_code = 'en'  # Default to English
    messages = load_messages(language_code)

    # Conversation handler for registration
    registration_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REGISTER_VEHICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_vehicle)],
            REGISTER_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_year)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Register handlers
    app.add_handler(CommandHandler('start', start))  # Handles the /start command
    app.add_handler(CommandHandler('setlanguage', set_language))  # Handles /setlanguage <lang_code>
    app.add_handler(registration_conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  # Handles generic text messages

    logger.info("Bot is running...")
    app.run_polling()
