from .commands import setup_commands
from .admin import setup_admin
from .chat import setup_chat
#from .user import register_user_handlers
 # ✅ make sure this exists

def setup_handlers(application):
    setup_commands(application)
    setup_admin(application)
    setup_chat(application)
    register_user_handlers(application)  # ✅ register user handlers
