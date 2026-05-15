from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Using AsyncIOMotorClient for non-blocking database operations
        self.client = AsyncIOMotorClient(Config.MONGODB_URI)
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
        if not await self.groups.find_one({"chat_id": chat_id}):
            await self.groups.insert_one({
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
        group = await self.groups.find_one({"chat_id": chat_id})
        if group:
            return group.get("settings", Config.DEFAULT_SETTINGS)
        return Config.DEFAULT_SETTINGS
    
    async def update_setting(self, chat_id: int, setting: str, value):
        """Update specific setting"""
        await self.groups.update_one(
            {"chat_id": chat_id},
            {"$set": {f"settings.{setting}": value}}
        )
    
    async def get_all_groups(self):
        """Get all groups"""
        cursor = self.groups.find({})
        return await cursor.to_list(length=1000)
    
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
        await self.warnings.insert_one(warn_data)
        
        # Get total warnings
        total_warnings = await self.warnings.count_documents({"chat_id": chat_id, "user_id": user_id})
        
        # Update stats
        await self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {"stats.warnings_issued": 1}}
        )
        
        return total_warnings
    
    async def get_warnings(self, chat_id: int, user_id: int):
        """Get all warnings for a user"""
        cursor = self.warnings.find({"chat_id": chat_id, "user_id": user_id})
        return await cursor.to_list(length=100)
    
    async def clear_warnings(self, chat_id: int, user_id: int):
        """Clear all warnings for a user"""
        await self.warnings.delete_many({"chat_id": chat_id, "user_id": user_id})
    
    # ========== Anti-Spam System ==========
    async def log_message(self, chat_id: int, user_id: int, message_id: int):
        """Log message for anti-spam"""
        # Clean old messages (older than 1 minute)
        cutoff = datetime.now() - timedelta(seconds=60)
        await self.messages_log.delete_many({"timestamp": {"$lt": cutoff}})
        
        # Log new message
        await self.messages_log.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "message_id": message_id,
            "timestamp": datetime.now()
        })
        
        # Check message frequency
        count = await self.messages_log.count_documents({
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": {"$gt": cutoff}
        })
        
        return count
    
    # ========== Ban/Mute System ==========
    async def ban_user(self, chat_id: int, user_id: int, reason: str, admin_id: int = None):
        """Ban user from group"""
        await self.banned_users.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "admin_id": admin_id,
            "banned_date": datetime.now()
        })
        
        await self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {"stats.bans_issued": 1}}
        )
    
    async def is_banned(self, chat_id: int, user_id: int):
        """Check if user is banned"""
        user = await self.banned_users.find_one({"chat_id": chat_id, "user_id": user_id})
        return bool(user)
    
    async def unban_user(self, chat_id: int, user_id: int):
        """Unban user"""
        await self.banned_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
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
        
        await self.muted_users.insert_one(mute_data)
    
    async def unmute_user(self, chat_id: int, user_id: int):
        """Unmute user"""
        await self.muted_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    # ========== Statistics ==========
    async def update_stats(self, chat_id: int, stat_type: str):
        """Update group statistics"""
        await self.groups.update_one(
            {"chat_id": chat_id},
            {"$inc": {f"stats.{stat_type}": 1}}
        )
    
    async def get_stats(self, chat_id: int):
        """Get group statistics"""
        group = await self.groups.find_one({"chat_id": chat_id})
        if group:
            return group.get("stats", {})
        return {}
