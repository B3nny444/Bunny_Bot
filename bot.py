import logging
import time
import signal
import sys
import asyncio
from threading import Lock

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from src.database import init_db, update_user_activity, list_users
from models.ai_router import generate_with_fallback
from models import user
from src.config import Config
from src.handlers import setup_commands
from src.handlers.admin import setup_admin

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Rate limiter to prevent spam
class RateLimiter:
    def __init__(self):
        self.user_timestamps = {}
        self.lock = Lock()

    def check_user(self, user_id: int) -> bool:
        with self.lock:
            current_time = time.time()
            last_time = self.user_timestamps.get(user_id, 0)
            if current_time - last_time < 5:
                return False
            self.user_timestamps[user_id] = current_time
            return True

rate_limiter = RateLimiter()

# Handle text messages with AI response
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        update_user_activity(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        if not rate_limiter.check_user(user.id):
            await update.message.reply_text("\u23F3 Please wait 5 seconds between messages.", parse_mode="Markdown")
            return

        prompt = update.message.text
        response = await generate_with_fallback(prompt)
        if len(response) > 4000:
            # Break into parts to avoid Telegram limits
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i + 4000], parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Message processing failed: {str(e)}", exc_info=True)
        await update.message.reply_text("\u26A0 An error occurred while processing your request.", parse_mode="Markdown")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Bot error: {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text("\u26A0 An unexpected error occurred.", parse_mode="Markdown")

# Admin-only: list users
async def handle_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_USER_IDS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    users = list_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    text = "👥 *Bot Users:*\n\n"
    for user in users[:30]:
        name = user.get('first_name') or user.get('username') or "Unknown"
        text += f"- `{user['user_id']}` [{name}](tg://user?id={user['user_id']})\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# Post-startup
async def post_init(application):
    logger.info("Bot starting up...")
    await application.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Get help information"),
        ("admin", "Admin controls"),
        ("users", "List all users")
    ])

# Shutdown
async def post_shutdown(application):
    logger.info("Bot shutting down...")

def handle_sigterm():
    logger.info("Received shutdown signal.")
    sys.exit(0)

# Main bot runner
def main():
    try:
        if not Config.TELEGRAM_TOKEN:
            logger.critical("Telegram token missing!")
            sys.exit(1)

        if not init_db():
            logger.critical("Database failed to initialize!")
            sys.exit(1)

        signal.signal(signal.SIGINT, lambda s, f: handle_sigterm())
        signal.signal(signal.SIGTERM, lambda s, f: handle_sigterm())

        application = ApplicationBuilder() \
            .token(Config.TELEGRAM_TOKEN) \
            .post_init(post_init) \
            .post_shutdown(post_shutdown) \
            .build()

        setup_commands(application)
        setup_admin(application)

        application.add_handler(CommandHandler("users", handle_list_users))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        logger.info("Starting bot...")
        application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Startup error: {str(e)}", exc_info=True)
    finally:
        logger.info("Bot process exited.")

if __name__ == '__main__':
    if not init_db():
        logger.critical("Database failed to initialize.")
        sys.exit(1)
    main()
