from telegram import Update
from telegram.ext import ContextTypes

from bot.constants import UNDEFINED


async def handle_conversation_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return UNDEFINED