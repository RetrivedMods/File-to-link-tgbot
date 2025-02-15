import logging
import os
from telegram import Update, ParseMode, Sticker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv  # Importing dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get sensitive data from environment variables
TOKEN = os.getenv("BOT_TOKEN")  # Load token from the .env file
STORAGE_CHANNEL = os.getenv("STORAGE_CHANNEL")  # Load channel from the .env file

# Sticker to send when the bot starts
START_STICKER = 'CAACAgQAAxkBAAIQXWFNcmfQ_oY1Brk8ZekmySYHZgdlAAnI_wAC7NCSXMUm4uC55QoslgE'

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_sticker(START_STICKER)
    time.sleep(1)
    update.message.reply_text(
        f"<b>Send Me File/Photos/Videos</b> 📂🎥, I will give you a link. "
        "The file will be stored safely! 🔐",
        parse_mode=ParseMode.HTML
    )


# Function to handle receiving files
def handle_file(update: Update, context: CallbackContext) -> None:
    file_id = None

    if update.message.video:
        file_id = update.message.video.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id  # Get the highest resolution photo
    elif update.message.document:
        file_id = update.message.document.file_id

    if file_id:
        # Download the file to upload it to the storage channel
        file = context.bot.get_file(file_id)
        file.download(f"temp_{file_id}")

        # Upload the file to the storage channel
        uploaded_file = context.bot.send_document(STORAGE_CHANNEL, open(f"temp_{file_id}", 'rb'))

        # Generate a link with the file ID
        file_link = f"https://t.me/{update.message.from_user.username}?start={file_id}"

        # Send a message with the file link as a spoiler
        update.message.reply_text(
            f"Here is your file ID: <a href='{file_link}'>Click here</a> 👇"
            f"\nYour file has been safely stored! 🔒",
            parse_mode=ParseMode.HTML,
        )

        # Clean up by deleting the temporary file
        os.remove(f"temp_{file_id}")


# Error handling function
def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main() -> None:
    # Set up the Updater and Dispatcher
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video, handle_file))
    
    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()


if __name__ == '__main__':
    main()
