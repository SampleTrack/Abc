from pymongo import MongoClient
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.DATABASE_NAME]
        
        # Collections
        self.groups = self.db.groups
        self.users = self.db.users
        self.warnings = self.db.warnings
        self.messages_log = self.db.messages_log
        self.banned_users = self.db.banned_users
        self.muted_users = self.db.muted_users
    
    # ========== Group Management ==========
    async def add_group(self, chat_id: int, title: str):
        """Add new group with default settings"""
        if not self.groups.find_one({"chat_id": chat_id}):
            self.groups.insert_one({
                "chat_id": chat_id,
                "title": title,
                "joined_date": datetime.now(),
                "settings": Config.DEFAULT_SETTINGS.copy(),
                "stats": {
                    "total_messages": 0,
                    "deleted_messages": 0,
                    "warnings_issued": 0,
                    "bans_issued": 0
                }
            })
            return True
        return False
    
    async def get_group_settings(self, chat_id: int):
        """Get group settings"""
        group = self.groups.find_one({"chat_id": chat_id})
        if group:
            return group.get("settings", Config.DEFAULT_SETTINGS)
        return Config.DEFAULT_SETTINGS
    
    async def update_setting(self, chat_id: int, setting: str, value):
        """Update specific setting"""
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$set": {f"settings.{setting}": value}}
        )
    
    async def get_all_groups(self):
        """Get all groups"""
        return list(self.groups.find({}))
    
    # ========== Warning System ==========
    async def warn_user(self, chat_id: int, user_id: int, reason: str, admin_id: int = None):
        """Warn a user"""
        warn_data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "admin_id": admin_id,
            "timestamp": datetime.now()
        }
        self.warnings.insert_one(warn_data)
        
        # Get total warnings
        total_warnings = self.warnings.count_documents({"chat_id": chat_id, "user_id": user_id})
        
        # Update stats
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {"stats.warnings_issued": 1}}
        )
        
        return total_warnings
    
    async def get_warnings(self, chat_id: int, user_id: int):
        """Get all warnings for a user"""
        return list(self.warnings.find({"chat_id": chat_id, "user_id": user_id}))
    
    async def clear_warnings(self, chat_id: int, user_id: int):
        """Clear all warnings for a user"""
        self.warnings.delete_many({"chat_id": chat_id, "user_id": user_id})
    
    async def reset_warnings(self, chat_id: int):
        """Reset all warnings in a group"""
        self.warnings.delete_many({"chat_id": chat_id})
    
    # ========== Anti-Spam System ==========
    async def log_message(self, chat_id: int, user_id: int, message_id: int):
        """Log message for anti-spam"""
        # Clean old messages (older than 1 minute)
        cutoff = datetime.now() - timedelta(seconds=60)
        self.messages_log.delete_many({"timestamp": {"$lt": cutoff}})
        
        # Log new message
        self.messages_log.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "message_id": message_id,
            "timestamp": datetime.now()
        })
        
        # Check message frequency
        count = self.messages_log.count_documents({
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": {"$gt": cutoff}
        })
        
        return count
    
    async def clear_messages(self, chat_id: int):
        """Clear all logged messages"""
        self.messages_log.delete_many({"chat_id": chat_id})
    
    # ========== Ban/Mute System ==========
    async def ban_user(self, chat_id: int, user_id: int, reason: str, admin_id: int = None):
        """Ban user from group"""
        self.banned_users.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "admin_id": admin_id,
            "banned_date": datetime.now()
        })
        
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {"stats.bans_issued": 1}}
        )
    
    async def is_banned(self, chat_id: int, user_id: int):
        """Check if user is banned"""
        return bool(self.banned_users.find_one({"chat_id": chat_id, "user_id": user_id}))
    
    async def unban_user(self, chat_id: int, user_id: int):
        """Unban user"""
        self.banned_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    async def mute_user(self, chat_id: int, user_id: int, duration: int = None, reason: str = None):
        """Mute user"""
        mute_data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "muted_date": datetime.now()
        }
        if duration:
            mute_data["until"] = datetime.now() + timedelta(seconds=duration)
        
        self.muted_users.insert_one(mute_data)
    
    async def is_muted(self, chat_id: int, user_id: int):
        """Check if user is muted"""
        return bool(self.muted_users.find_one({"chat_id": chat_id, "user_id": user_id}))
    
    async def unmute_user(self, chat_id: int, user_id: int):
        """Unmute user"""
        self.muted_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    # ========== Statistics ==========
    async def update_stats(self, chat_id: int, stat_type: str):
        """Update group statistics"""
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {f"stats.{stat_type}": 1}}
        )
    
    async def get_stats(self, chat_id: int):
        """Get group statistics"""
        group = self.groups.find_one({"chat_id": chat_id})
        if group:
            return group.get("stats", {})
        return {}
