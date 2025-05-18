from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from src.config import Config
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()

# Then modify your generate_response to check cache first

def restricted(func):
    """Restrict access to the command"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("⚠️ Unauthorized access. Admin only.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def rate_limited(rate_limit: int = Config.RATE_LIMIT):
    """Rate limit decorator"""
    def decorator(func):
        user_timestamps = {}
        
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            now = update.message.date
            
            if user_id not in user_timestamps:
                user_timestamps[user_id] = []
            
            # Remove old timestamps (keep only last minute)
            user_timestamps[user_id] = [
                t for t in user_timestamps[user_id] 
                if (now - t).total_seconds() < 60
            ]
            
            if len(user_timestamps[user_id]) >= rate_limit:
                await update.message.reply_text(
                    "⚠️ You're sending messages too fast. Please wait a minute."
                )
                return
            
            user_timestamps[user_id].append(now)
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator