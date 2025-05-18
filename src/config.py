import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    App configuration loaded from .env or system environment.
    Validates presence of required variables.
    """

    # ✅ Required
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")

    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    if not COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY is required in .env file")

    # ✅ Admin IDs
    ADMIN_USER_IDS: List[int] = []
    admin_ids_raw = os.getenv("ADMIN_USER_IDS")
    if admin_ids_raw:
        try:
            ADMIN_USER_IDS = [int(id.strip()) for id in admin_ids_raw.split(",") if id.strip()]
        except Exception as e:
            raise ValueError("ADMIN_USER_IDS must be a comma-separated list of integers") from e

    # ✅ Database config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database.db")
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # ✅ Optional configs
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "10"))
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "20"))

    @classmethod
    def validate(cls):
        """Validate essential configuration fields"""
        required_vars = {
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_TOKEN,
            "COHERE_API_KEY": cls.COHERE_API_KEY,
        }

        for key, value in required_vars.items():
            if not value:
                raise ValueError(f"{key} is required in .env file")

        if not cls.DATABASE_URL.startswith("sqlite:///"):
            raise ValueError("DATABASE_URL must start with sqlite:///")

# Validate when imported
Config.validate()
