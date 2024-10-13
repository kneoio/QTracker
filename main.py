import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import start, handle_photo, handle_text

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Main function
if __name__ == '__main__':
    logger.info("Starting the bot...")

    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot is running...")
    app.run_polling()
