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
    
    def add_group(self, chat_id: int, title: str):
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
    
    def get_group_settings(self, chat_id: int):
        group = self.groups.find_one({"chat_id": chat_id})
        if group:
            return group.get("settings", Config.DEFAULT_SETTINGS)
        return Config.DEFAULT_SETTINGS
    
    def update_setting(self, chat_id: int, setting: str, value):
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$set": {f"settings.{setting}": value}}
        )
    
    def get_all_groups(self):
        return list(self.groups.find({}))
    
    def warn_user(self, chat_id: int, user_id: int, reason: str, admin_id: int = None):
        warn_data = {
            "chat_id": chat_id, "user_id": user_id, "reason": reason,
            "admin_id": admin_id, "timestamp": datetime.now()
        }
        self.warnings.insert_one(warn_data)
        total_warnings = self.warnings.count_documents({"chat_id": chat_id, "user_id": user_id})
        self.groups.update_one({"chat_id": chat_id}, {"$inc": {"stats.warnings_issued": 1}})
        return total_warnings
    
    def get_warnings(self, chat_id: int, user_id: int):
        return list(self.warnings.find({"chat_id": chat_id, "user_id": user_id}))
    
    def clear_warnings(self, chat_id: int, user_id: int):
        self.warnings.delete_many({"chat_id": chat_id, "user_id": user_id})
    
    def log_message(self, chat_id: int, user_id: int, message_id: int):
        cutoff = datetime.now() - timedelta(seconds=60)
        self.messages_log.delete_many({"timestamp": {"$lt": cutoff}})
        self.messages_log.insert_one({
            "chat_id": chat_id, "user_id": user_id, "message_id": message_id, "timestamp": datetime.now()
        })
        return self.messages_log.count_documents({
            "chat_id": chat_id, "user_id": user_id, "timestamp": {"$gt": cutoff}
        })
    
    def ban_user(self, chat_id: int, user_id: int, reason: str, admin_id: int = None):
        self.banned_users.insert_one({
            "chat_id": chat_id, "user_id": user_id, "reason": reason, 
            "admin_id": admin_id, "banned_date": datetime.now()
        })
        self.groups.update_one({"chat_id": chat_id}, {"$inc": {"stats.bans_issued": 1}})
    
    def is_banned(self, chat_id: int, user_id: int):
        return bool(self.banned_users.find_one({"chat_id": chat_id, "user_id": user_id}))
    
    def unban_user(self, chat_id: int, user_id: int):
        self.banned_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    def mute_user(self, chat_id: int, user_id: int, duration: int = None, reason: str = None):
        mute_data = {"chat_id": chat_id, "user_id": user_id, "reason": reason, "muted_date": datetime.now()}
        if duration:
            mute_data["until"] = datetime.now() + timedelta(seconds=duration)
        self.muted_users.insert_one(mute_data)
    
    def is_muted(self, chat_id: int, user_id: int):
        return bool(self.muted_users.find_one({"chat_id": chat_id, "user_id": user_id}))
    
    def unmute_user(self, chat_id: int, user_id: int):
        self.muted_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    def update_stats(self, chat_id: int, stat_type: str):
        self.groups.update_one({"chat_id": chat_id}, {"$inc": {f"stats.{stat_type}": 1}})
    
    def get_stats(self, chat_id: int):
        group = self.groups.find_one({"chat_id": chat_id})
        return group.get("stats", {}) if group else {}
