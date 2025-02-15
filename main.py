import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Replace with your bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# List of Terabox domains
TERABOX_DOMAINS = [
    "mirrobox.com", "nephobox.com", "freeterabox.com", "1024tera.com",
    "4funbox.co", "terabox.app", "terabox.com", "terabox.fun", "momerybox.com",
    "tibibox.com", "teraboxapp.com", "www.mirrobox.com", "www.nephobox.com",
    "www.freeterabox.com", "www.1024tera.com", "www.4funbox.com",
    "www.terabox.com", "www.momerybox.com", "www.tibibox.com", "www.teraboxapp.com"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if any(domain in message for domain in TERABOX_DOMAINS):
        try:
            await update.message.reply_text("Processing your Terabox link...")
            
            # Get direct download URL
            direct_url = await get_direct_url(message)
            
            if direct_url:
                await update.message.reply_video(direct_url)
            else:
                await update.message.reply_text("Failed to process the link")
                
        except Exception as e:
            logging.error(f"Error: {e}")
            await update.message.reply_text("Error processing your request")
    else:
        await update.message.reply_text("Please send a valid Terabox link")

async def get_direct_url(terabox_url: str) -> str:
    """Extract direct download URL from Terabox link"""
    try:
        # Send a request to the Terabox link
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(terabox_url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the direct download URL (this depends on Terabox's HTML structure)
        # Example: Look for <video> or <a> tags with download links
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return video_tag["src"]

        # If no video tag is found, look for other download links
        download_link = soup.find("a", href=re.compile(r"https?://.*\.(mp4|mkv|avi)"))
        if download_link and download_link.get("href"):
            return download_link["href"]

        return None
    except Exception as e:
        logging.error(f"Error extracting URL: {e}")
        return None

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Bot is running...")
    application.run_polling()
