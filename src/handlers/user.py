from telegram import Update
from telegram.ext import ContextTypes
from src.database import get_all_users
from src.config import Config

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.OWNER_ID:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    msg = "👥 *Bot Users:*\n\n"
    for user in users:
        name = user['username'] or user['first_name'] or "Unknown"
        msg += f"• `{user['user_id']}` - {name}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")
