import logging
from telegram import Update, Sticker
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the /start command
def start(update: Update, context: CallbackContext) -> None:
    # Send a sticker on start
    update.message.reply_sticker('YOUR_STICKER_ID')  # replace with your sticker ID
    # Wait for 1 second and delete the sticker
    context.job_queue.run_once(lambda context: update.message.delete(), 1)
    # Send a message asking for files/photos/videos
    update.message.reply_text(
        "Send me a file, photo, or video, and I will give you a link. 🎥📁📸\n\nI will provide a link to your uploaded file. Please wait for the process to finish!",
        parse_mode=ParseMode.MARKDOWN_V2
    )

# Handle received files
def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document or update.message.photo or update.message.video
    if file:
        file_id = file.file_id
        file_name = file.file_name if file_name else "unknown_file"

        # Upload file to a storage channel (simulate here by printing)
        print(f"Uploading {file_name} with ID: {file_id} to storage...")

        # Simulate generating a link for the uploaded file
        file_link = f"https://t.me/DriveMaxBot?start={file_id}"

        update.message.reply_text(f"File uploaded successfully! You can download it here: {file_link}")
    else:
        update.message.reply_text("Please send a valid file, photo, or video!")

# Error handling
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Bot's token
    token = 'YOUR_BOT_TOKEN'  # Replace with your actual bot token
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.Document.ALL | filters.Photo.ALL | filters.Video.ALL, handle_file))
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
