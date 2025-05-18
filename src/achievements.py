from src.database import get_user_stats, add_achievement

ACHIEVEMENTS = {
    "first_message": {
        "name": "Chat Starter",
        "description": "Send your first message",
        "check": lambda stats: stats.get('message_count', 0) >= 1
    },
    "daily_user": {
        "name": "Daily User",
        "description": "Use the bot for 7 consecutive days",
        "check": lambda stats: stats.get('active_days', 0) >= 7
    },
    "power_user": {
        "name": "Power User",
        "description": "Send 100 messages",
        "check": lambda stats: stats.get('message_count', 0) >= 100
    }
}

def check_achievements(user_id: int):
    stats = get_user_stats(user_id)
    existing = {a['name'] for a in get_achievements(user_id)}
    
    for achievement_id, data in ACHIEVEMENTS.items():
        if data['name'] not in existing and data['check'](stats):
            add_achievement(user_id, data['name'])
            return data  # Return the earned achievement
    
    return None