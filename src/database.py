import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict
from src.config import Config



logger = logging.getLogger(__name__)

def list_users() -> List[Dict]:
    """Return a list of all users"""
    try:
        from src.database import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, first_name, last_name, join_date, last_active FROM users ORDER BY last_active DESC")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        import logging
        logging.error(f"Error listing users: {str(e)}")
        return []

def get_db() -> sqlite3.Connection:
    try:
        db_path = Config.DATABASE_URL.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def init_db() -> bool:
    try:
        with get_db() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                message_count INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                last_daily TIMESTAMP,
                notification_prefs TEXT DEFAULT '{}'
            ) STRICT;
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) STRICT;
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) STRICT;
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_message_logs_user_id ON message_logs(user_id)")

            conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def update_user_activity(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None) -> bool:
    try:
        with get_db() as conn:
            conn.execute("""
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, join_date, last_active)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (user_id, username, first_name, last_name))

            conn.execute("""
            UPDATE users SET 
                message_count = message_count + 1,
                last_active = datetime('now'),
                username = COALESCE(?, username),
                first_name = COALESCE(?, first_name),
                last_name = COALESCE(?, last_name)
            WHERE user_id = ?
            """, (username, first_name, last_name, user_id))

            conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to update user activity: {str(e)}")
        return False

def get_user_stats(user_id: int) -> Optional[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        return None

def add_points(user_id: int, points: int) -> bool:
    try:
        with get_db() as conn:
            conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
            conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to add points: {str(e)}")
        return False

def add_achievement(user_id: int, achievement_name: str) -> bool:
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO achievements (user_id, name) VALUES (?, ?)", (user_id, achievement_name))
            conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to add achievement: {str(e)}")
        return False

def get_achievements(user_id: int) -> List[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, strftime('%Y-%m-%d %H:%M:%S', earned_date) as earned_date 
                FROM achievements 
                WHERE user_id = ? 
                ORDER BY earned_date DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Failed to get achievements: {str(e)}")
        return []

def get_leaderboard(limit: int = 10) -> List[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, first_name, last_name, points, message_count
                FROM users 
                ORDER BY points DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Database error in get_leaderboard: {str(e)}")
        return []

def log_message(user_id: int, message_type: str, content: Optional[str] = None) -> bool:
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO message_logs (user_id, message_type, content) VALUES (?, ?, ?)", (user_id, message_type, content))
            conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to log message: {str(e)}")
        return False

def verify_database() -> bool:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            if cursor.fetchone()[0] != "ok":
                return False

            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('users', 'achievements', 'message_logs')
            """)
            return len({row['name'] for row in cursor.fetchall()}) == 3
    except sqlite3.Error as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

def get_all_users() -> List[Dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, first_name, last_name 
                FROM users ORDER BY last_active DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch all users: {str(e)}")
        return []

