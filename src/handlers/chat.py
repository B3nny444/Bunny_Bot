from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from models.ai_router import generate_with_fallback
from src.services.utils import rate_limited
from src.database import update_user_activity

@rate_limited()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    # Update user activity
    user = update.effective_user
    update_user_activity(
        user.id,
        user.username or "",
        user.first_name,
        user.last_name or ""
    )
    
    # Get AI response
    try:
        response = await generate_with_fallback(prompt)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def setup_chat(application):
    """Register message handler"""
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )