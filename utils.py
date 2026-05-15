import re
from datetime import datetime
from typing import Tuple, List

class ProtectionUtils:
    
    @staticmethod
    def contains_link(text: str, allowed_domains: List[str] = None) -> Tuple[bool, str]:
        """Check if text contains any links"""
        if allowed_domains is None:
            allowed_domains = []
        
        # URL patterns
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r't\.me/[^\s]+',
            r'telegram\.me/[^\s]+'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Check if domain is allowed
                is_allowed = any(domain in match.lower() for domain in allowed_domains)
                if not is_allowed:
                    return True, match
        
        return False, None
    
    @staticmethod
    def contains_abusive_words(text: str, blocked_words: List[str]) -> Tuple[bool, str]:
        """Check if text contains abusive words"""
        text_lower = text.lower()
        
        for word in blocked_words:
            if word.lower() in text_lower:
                return True, word
        
        return False, None
    
    @staticmethod
    def contains_phone_number(text: str) -> Tuple[bool, str]:
        """Check if text contains phone number"""
        # Indian phone number patterns
        patterns = [
            r'[6-9]\d{9}',  # 10 digit number
            r'\+91[6-9]\d{9}',  # With +91
            r'0[6-9]\d{9}',  # With leading 0
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',  # Formatted numbers
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return True, matches[0]
        
        return False, None
    
    @staticmethod
    def contains_emoji(text: str, blocked_emojis: List[str] = None) -> Tuple[bool, str]:
        """Check if text contains blocked emojis"""
        if not blocked_emojis:
            return False, None
        
        for emoji in blocked_emojis:
            if emoji in text:
                return True, emoji
        
        return False, None
    
    @staticmethod
    def is_forwarded(message) -> bool:
        """Check if message is forwarded"""
        return bool(message.forward_from or message.forward_sender_name or message.forward_from_chat)
    
    @staticmethod
    def format_violation_message(violation_type: str, content: str, action: str) -> str:
        """Format violation message"""
        icons = {
            'forward': '📎',
            'link': '🔗',
            'abuse': '🤬',
            'emoji': '😡',
            'phone': '📞',
            'spam': '🔄',
            'flood': '💧'
        }
        
        icon = icons.get(violation_type, '⚠️')
        
        return (
            f"{icon} **Violation Detected!**\n\n"
            f"**Type:** `{violation_type.upper()}`\n"
            f"**Content:** `{content[:50]}`\n"
            f"**Action:** `{action.upper()}`\n\n"
            f"⚠️ Please follow group rules!"
        )
    
    @staticmethod
    def format_purge_progress(current: int, total: int) -> str:
        """Format purge progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int(percentage / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        return f"🗑️ **Purging Messages**\n\n`{bar}` {percentage:.1f}%\n\nDeleted: {current}/{total}"
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds into readable time"""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        if seconds: parts.append(f"{seconds}s")
        
        return " ".join(parts) if parts else "0s"
    
    @staticmethod
    def is_admin_command(cmd: str) -> bool:
        """Check if command is admin only"""
        admin_commands = [
            'ban', 'unban', 'mute', 'unmute', 'kick', 'purge', 'purgeall',
            'settings', 'set', 'warn', 'warnings', 'resetwarns', 'stats'
        ]
        return cmd in admin_commands
