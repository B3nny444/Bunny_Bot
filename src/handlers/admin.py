from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from src.config import Config
from src.services.utils import restricted
from src.database import get_db

# Sync functions for checking admin/owner status
def is_admin(user_id):
    # Replace with actual logic to check if the user is an admin
    return user_id in Config.ADMIN_USER_IDS  # Example check

def is_owner(user_id):
    # Replace with actual logic to check if the user is an owner
    return user_id == Config.OWNER_USER_ID  # Example check

@restricted
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Bot Statistics", callback_data="bot_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="start_broadcast")],
    ]
    await update.message.reply_text(
        "🛠 *Admin Panel*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not (is_admin(user_id) or is_owner(user_id)):
        # If the user is neither admin nor owner, return an error
        await query.edit_message_text("❌ You do not have permission to access this panel.")
        return

    if query.data == "bot_stats":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_active > datetime('now', '-7 days')
            """)
            active_users = cursor.fetchone()[0]
            
            cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT DISTINCT user_id FROM users 
                WHERE last_active > datetime('now', '-1 day')
            )""")
            daily_active = cursor.fetchone()[0]
        
        stats_text = (
            "🤖 *Bot Statistics*\n\n"
            f"👥 Total Users: `{total_users}`\n"
            f"🟢 Active (7 days): `{active_users}`\n"
            f"🌞 Daily Active: `{daily_active}`"
        )
        await query.edit_message_text(
            stats_text,
            parse_mode="Markdown"
        )
    
    elif query.data == "start_broadcast":
        await query.edit_message_text(
            "📢 Send the message you want to broadcast to all users:",
            parse_mode="Markdown"
        )

def setup_admin(application):
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_button_handler))

async def backup_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    backup = export_db_to_json()  # Implement in database.py
    await update.message.reply_document(document=backup)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    user_id = context.args[0]
    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
