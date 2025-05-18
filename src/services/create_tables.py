# create_tables.py
import sqlite3
from pathlib import Path

Path("db").mkdir(exist_ok=True)
conn = sqlite3.connect("db/bot_data.db")

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    join_date TIMESTAMP,
    last_active TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    text TEXT,
    date TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

conn.commit()
conn.close()