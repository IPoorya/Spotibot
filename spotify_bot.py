import logging, os, re
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from spotify_downloader import SpotifySong, get_song_lyrics

# Enable logging
os.makedirs("log", exist_ok=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,
    handlers=[
        logging.FileHandler('log/spotify_bot.log'),
        logging.StreamHandler()
    ]
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


async def spotify_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends music file from provided spotify url."""
    message_text = update.message.text
    
    if "https://open.spotify.com/track/" in message_text:
        track_id = re.search(r"track/([a-zA-Z0-9]+)", message_text)
        track_id = track_id.group(1)
        keyboard = [
            [InlineKeyboardButton("Lyrics 📜", callback_data=f"song_ID:{track_id}")],
        ]   
        reply_markup = InlineKeyboardMarkup(keyboard)
        song = SpotifySong(track_id)
        filepath, coverpath = song.download_song('files/')
        caption = f"💽 {song.song_name} \n🗣 {song.song_artist}"
        await update.message.reply_audio(audio=open(filepath, 'rb'), 
                                         caption=caption,
                                         title=song.song_name,
                                         performer=song.song_artist,
                                         duration=song.song_duration,
                                         thumbnail=coverpath,
                                         reply_markup=reply_markup)    


async def lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends music lyrics when lyrics button clicked."""

    song_id = data.split(":")[1]

    # remove the button
    await query.edit_message_reply_markup(reply_markup=None)

    lyrics = get_song_lyrics(song_id) or "Lyrics not found."
    await query.message.reply_text(lyrics)


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """manages buttons."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("song_ID:"):
        lyrics(update, context)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Entity("url"), spotify_url))
    application.add_handler(CallbackQueryHandler(buttons))
    #application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
