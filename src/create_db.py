import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from src.database import init_db

# Create db directory if not exists
Path("db").mkdir(exist_ok=True)

# Initialize database
init_db()
print("✅ Database initialized successfully at db/bot_data.db")