import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "premium_group_manager")
    
    # Bot Settings
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
    
    # Web Server Settings (for Render, Heroku, etc.)
    PORT = int(os.getenv("PORT", 8080))
    HOST = os.getenv("HOST", "0.0.0.0")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # Optional: for webhook mode
    
    # Protection Settings (Default)
    DEFAULT_SETTINGS = {
        # Basic protection
        'anti_forward': True,
        'anti_link': True,
        'anti_abuse': True,
        'anti_emoji': False,
        'anti_phone': True,
        'anti_spam': True,
        'anti_flood': True,
        
        # Auto-delete
        'auto_delete': False,
        'delete_interval': 10,  # minutes
        
        # Actions
        'action_on_violation': 'delete',  # delete, mute, ban, warn
        'warn_limit': 3,
        
        # Filters
        'allowed_domains': ['youtube.com', 't.me', 'instagram.com'],
        'blocked_words': ['fuck', 'shit', 'bitch', 'asshole', 'nigger'],
        'blocked_emojis': ['🔞', '💀', '🔫', '💣', '🔥'],
        
        # Other
        'delete_command_messages': True,
        'delete_service_messages': True,
    }
