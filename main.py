import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TERABOX_DOMAINS = [
    "terabox.com", "teraboxapp.com", "mirrobox.com", "nephobox.com",
    "freeterabox.com", "4funbox.com", "momerybox.com", "tibibox.com"
]

# Dummy HTTP server for Koyeb health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    server = HTTPServer(("0.0.0.0", 8000), HealthCheckHandler)
    logger.info("HTTP server started on port 8000")
    server.serve_forever()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message from user {update.effective_user.id}: {user_message}")

    if any(domain in user_message for domain in TERABOX_DOMAINS):
        try:
            await update.message.reply_text("Processing your Terabox link...")
            direct_url = await get_direct_url(user_message)
            
            if direct_url:
                logger.info(f"Sending video URL: {direct_url}")
                await update.message.reply_video(direct_url)
            else:
                await update.message.reply_text("Failed to extract direct URL")
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            await update.message.reply_text("An error occurred. Please try again.")
    
    else:
        await update.message.reply_text("Please send a valid Terabox link.")

async def get_direct_url(url: str) -> str:
    """Extract direct download URL from Terabox link"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for video source
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return video_tag["src"]
        
        # Look for download button
        download_button = soup.find("a", href=re.compile(r"(?i).*\.(mp4|mkv|avi|mov)"))
        if download_button and download_button.get("href"):
            return download_button["href"]
        
        return None
    
    except Exception as e:
        logger.error(f"Error in get_direct_url: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    # Start HTTP server for Koyeb health checks
    http_thread = Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Start Telegram bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running...")
    application.run_polling()
