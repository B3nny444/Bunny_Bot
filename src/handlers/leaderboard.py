# src/handlers/leaderboard.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from src.database import get_leaderboard

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_leaderboard()
    if not data:
        await update.message.reply_text("📉 No leaderboard data available yet.")
        return

    message = "<b>🏆 Top Users Leaderboard:</b>\n\n"
    for i, user in enumerate(data, 1):
        name = user['username'] or user['first_name'] or "Anonymous"
        message += f"{i}. <code>{name}</code> – <b>{user['points']}</b> points\n"
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)
