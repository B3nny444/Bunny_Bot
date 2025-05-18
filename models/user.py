from typing import Dict
import json

def load_admins():
    with open("data/admins.json") as f:
        return json.load(f)

async def is_admin(user_id: int) -> bool:
    data = load_admins()
    return user_id in data.get("admins", [])

async def is_owner(user_id: int) -> bool:
    data = load_admins()
    return user_id == data.get("owner")


# In-memory user database (you can replace this with a real DB later)
users_db: Dict[int, dict] = {}

# Define user roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_OWNER = "owner"

# Your Telegram user ID (or set dynamically)
OWNER_ID = 1513565142  # Replace with your actual Telegram ID

def register_user(user_id: int, username: str):
    """
    Registers a user if not already registered.
    """
    if user_id not in users_db:
        role = ROLE_OWNER if user_id == OWNER_ID else ROLE_USER
        users_db[user_id] = {
            "username": username,
            "role": role,
            "active": True,
        }
        print(f"✅ New user registered: {username} ({role})")
    else:
        print(f"👤 User already registered: {username}")

def get_user_role(user_id: int) -> str:
    """
    Returns the user's role.
    """
    return users_db.get(user_id, {}).get("role", ROLE_USER)

def is_admin(user_id: int) -> bool:
    return get_user_role(user_id) in [ROLE_ADMIN, ROLE_OWNER]

def is_owner(user_id: int) -> bool:
    return get_user_role(user_id) == ROLE_OWNER

def deactivate_user(user_id: int):
    if user_id in users_db:
        users_db[user_id]["active"] = False

def activate_user(user_id: int):
    if user_id in users_db:
        users_db[user_id]["active"] = True

def is_user_active(user_id: int) -> bool:
    return users_db.get(user_id, {}).get("active", False)
