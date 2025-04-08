import logging, os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
token = os.getenv("bot_token")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends a welcome meddage with home menu."""
    keyboard = [
        [InlineKeyboardButton("Connect Your Playlist 🔗", callback_data="1")],
        [InlineKeyboardButton("Your Playlists 📝", callback_data="2")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Welcome,\nJust send me a spotify track URL,\nor just use one of the options below:", reply_markup=reply_markup)






def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    #application.add_handler(CallbackQueryHandler(button))
    #application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
