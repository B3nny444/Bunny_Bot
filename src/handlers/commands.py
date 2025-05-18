import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, Application
)

from src.database import (
    get_user_stats,
    add_points,
    get_leaderboard,
    get_achievements,
    update_user_activity,
    get_db
)
from src.achievements import check_achievements
from src.utils import escape_markdown

logger = logging.getLogger(__name__)

# ─────────────────────────────── COMMANDS ─────────────────────────────── #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        update_user_activity(user.id, user.username, user.first_name, user.last_name)
        await update.message.reply_text(
            escape_markdown("👋 Welcome! Use /help to see available commands."),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error(f"Start command failed: {str(e)}")
        await update.message.reply_text(
            escape_markdown("⚠️ Could not process command. Please try again later."),
            parse_mode="MarkdownV2"
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = escape_markdown("""
*Available Commands:*
/start - Start the bot
/profile - View your profile
/daily - Claim daily reward
/leaderboard - Top users
/help - Show this help message
""")
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Help command failed: {str(e)}")
        await update.message.reply_text(
            escape_markdown("⚠️ Could not show help. Please try again later."),
            parse_mode="MarkdownV2"
        )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        stats = get_user_stats(user.id) or {}

        if not stats:
            update_user_activity(user.id, user.username, user.first_name, user.last_name)
            stats = get_user_stats(user.id) or {}

        achievements = get_achievements(user.id) or []

        response = escape_markdown(
            f"👤 Profile: {user.first_name or 'User'}\n"
            f"🆔 ID: {user.id}\n"
            f"⭐ Points: {stats.get('points', 0)}\n"
            f"✉️ Messages: {stats.get('message_count', 0)}\n"
            f"🏆 Achievements: {len(achievements)}"
        )

        keyboard = [
            [InlineKeyboardButton("View Achievements", callback_data=f"achievements_{user.id}")],
            [InlineKeyboardButton("Claim Daily", callback_data="daily")]
        ]

        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error(f"Profile command failed: {str(e)}")
        await update.message.reply_text(
            escape_markdown("⚠️ Could not load profile. Please try again later."),
            parse_mode="MarkdownV2"
        )

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        stats = get_user_stats(user.id) or {}

        if not stats:
            update_user_activity(user.id, user.username, user.first_name, user.last_name)
            stats = get_user_stats(user.id) or {}

        last_daily = datetime.strptime(stats['last_daily'], "%Y-%m-%d %H:%M:%S") if stats.get('last_daily') else None

        if last_daily and (datetime.now() - last_daily).days < 1:
            remaining = 24 - (datetime.now() - last_daily).seconds // 3600
            await update.message.reply_text(
                escape_markdown(f"⏳ Come back in {remaining} hours to claim your next reward!"),
                parse_mode="MarkdownV2"
            )
            return

        points_added = add_points(user.id, 10)

        if points_added:
            with get_db() as conn:
                conn.execute(
                    "UPDATE users SET last_daily = datetime('now') WHERE user_id = ?", 
                    (user.id,)
                )
                conn.commit()

            achievement = check_achievements(user.id)
            response = escape_markdown("🎁 Daily Reward Claimed!\n\n+10 points")

            if achievement:
                response += escape_markdown(
                    f"\n\n🏆 New Achievement!\n"
                    f"{achievement['name']}: {achievement['description']}"
                )

            await update.message.reply_text(response, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(
                escape_markdown("⚠️ Could not add points. Please try again later."),
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        logger.error(f"Daily reward failed: {str(e)}")
        await update.message.reply_text(
            escape_markdown("⚠️ Could not process daily reward. Please try again later."),
            parse_mode="MarkdownV2"
        )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        top_users = get_leaderboard(limit=10)

        if not top_users:
            await update.message.reply_text(
                escape_markdown("🏆 No users on the leaderboard yet! Be the first!"),
                parse_mode="MarkdownV2"
            )
            return

        response = [escape_markdown("🏆 Top 10 Users")]
        for i, user in enumerate(top_users, 1):
            username = escape_markdown(
                user.get('username') or 
                f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or 
                f"User {user['user_id']}"
            )
            response.append(escape_markdown(f"{i}. {username}: {user['points']} points"))

        await update.message.reply_text("\n".join(response), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Leaderboard failed: {str(e)}")
        await update.message.reply_text(
            escape_markdown("⚠️ Could not load leaderboard. Please try again later."),
            parse_mode="MarkdownV2"
        )

# ───────────────────────────── CALLBACK HANDLER ───────────────────────────── #

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        if query.data.startswith("achievements_"):
            user_id = int(query.data.split("_")[1])
            achievements = get_achievements(user_id)

            if achievements:
                text = [escape_markdown("🏆 Your Achievements")]
                for a in achievements:
                    text.append(escape_markdown(f"• {a['name']} - {a['earned_date']}"))
                response = "\n".join(text)
            else:
                response = escape_markdown("You haven't earned any achievements yet!")

            await query.edit_message_text(response, parse_mode="MarkdownV2")

        elif query.data == "daily":
            await daily_reward(update, context)

    except Exception as e:
        logger.error(f"Button handler failed: {str(e)}")
        await query.edit_message_text(
            escape_markdown("⚠️ Action failed."),
            parse_mode="MarkdownV2"
        )

# ───────────────────────────── HANDLER REGISTRATION ───────────────────────────── #

def setup_commands(application: Application):
    try:
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_cmd))
        application.add_handler(CommandHandler("profile", profile))
        application.add_handler(CommandHandler("daily", daily_reward))
        application.add_handler(CommandHandler("leaderboard", leaderboard))
        application.add_handler(CallbackQueryHandler(button_handler))

        logger.info("Command handlers registered successfully")
    except Exception as e:
        logger.critical(f"Failed to register commands: {str(e)}")
        raise
