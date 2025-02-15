import logging
from telegram import Update, Sticker
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the /start command
async def start(update: Update, context: CallbackContext) -> None:
    # Send a sticker on start
    await update.message.reply_sticker('CAACAgUAAxkBAAENzCVnsGoDRbVAg2EDLQzEFskMarYqjwACIRMAAudUOFQQ7nxQ8toG6DYE')  # replace with your sticker ID
    # Wait for 1 second and delete the sticker
    await update.message.delete()
    # Send a message asking for files/photos/videos
    await update.message.reply_text(
        "Send me a file, photo, or video, and I will give you a link. 🎥📁📸\n\nI will provide a link to your uploaded file. Please wait for the process to finish!",
        parse_mode=ParseMode.MARKDOWN_V2
    )

# Handle received files
async def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document or update.message.photo or update.message.video
    if file:
        file_id = file.file_id
        file_name = file.file_name if hasattr(file, 'file_name') else "unknown_file"

        # Upload file to a storage channel (simulate here by printing)
        print(f"Uploading {file_name} with ID: {file_id} to storage...")

        # Simulate generating a link for the uploaded file
        file_link = f"https://t.me/teraboxfiledownloadeasybot?start={file_id}"

        await update.message.reply_text(f"File uploaded successfully! You can download it here: {file_link}")
    else:
        await update.message.reply_text("Please send a valid file, photo, or video!")

# Error handling
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

async def main():
    # Bot's token
    token = '7938705422:AAH1MPF24jVPJ7rXH_FC3JMxC0sHTDOR7Gk'  # Replace with your actual bot token
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Photo.ALL | filters.Video.ALL, handle_file))
    application.add_error_handler(error)

    # Start the Bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
