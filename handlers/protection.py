from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from datetime import datetime, timedelta
from utils import ProtectionUtils
import asyncio

def register_protection_handlers(app, db):
    
    @app.on_message(filters.group & ~filters.service, group=1)
    async def check_message_protection(client: Client, message: Message):
        """Check all protections before message is processed"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # Skip if user is admin
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
        
        # Check if user is banned
        if await db.is_banned(chat_id, user_id):
            await message.delete()
            return
        
        # Get settings
        settings = await db.get_group_settings(chat_id)
        
        # Log message for anti-spam
        msg_count = await db.log_message(chat_id, user_id, message.id)
        
        # Check each protection
        violations = []
        
        # 1. Anti-Forward
        if settings.get('anti_forward', False) and ProtectionUtils.is_forwarded(message):
            violations.append(('forward', 'Forwarded message'))
        
        # 2. Anti-Link
        if settings.get('anti_link', False) and message.text:
            has_link, link = ProtectionUtils.contains_link(
                message.text, 
                settings.get('allowed_domains', [])
            )
            if has_link:
                violations.append(('link', link))
        
        # 3. Anti-Abuse
        if settings.get('anti_abuse', False) and message.text:
            has_abuse, word = ProtectionUtils.contains_abusive_words(
                message.text,
                settings.get('blocked_words', [])
            )
            if has_abuse:
                violations.append(('abuse', word))
        
        # 4. Anti-Phone
        if settings.get('anti_phone', False) and message.text:
            has_phone, phone = ProtectionUtils.contains_phone_number(message.text)
            if has_phone:
                violations.append(('phone', phone))
        
        # 5. Anti-Emoji
        if settings.get('anti_emoji', False) and message.text:
            has_emoji, emoji = ProtectionUtils.contains_emoji(
                message.text,
                settings.get('blocked_emojis', [])
            )
            if has_emoji:
                violations.append(('emoji', emoji))
        
        # 6. Anti-Spam (multiple messages)
        if settings.get('anti_spam', False) and msg_count > 5:
            violations.append(('spam', f'{msg_count} messages in 60s'))
        
        # 7. Anti-Flood (same message repeated)
        if settings.get('anti_flood', False) and message.text:
            # Check for same message in last 10 messages
            async for msg in client.get_chat_history(chat_id, limit=10):
                if msg.text == message.text and msg.from_user.id == user_id:
                    violations.append(('flood', 'Repeated message'))
                    break
        
        # Handle violations
        if violations:
            await handle_violation(client, message, violations[0], settings, db)
            return False
        
        return True
    
    async def handle_violation(client: Client, message: Message, violation: tuple, settings: dict, db):
        """Handle protection violations"""
        violation_type, content = violation
        action = settings.get('action_on_violation', 'delete')
        
        # Format warning message
        warning_msg = ProtectionUtils.format_violation_message(violation_type, content, action)
        
        # Take action based on settings
        if action == 'delete':
            await message.delete()
            warn_msg = await message.reply_text(warning_msg)
            await asyncio.sleep(5)
            await warn_msg.delete()
            
        elif action == 'warn':
            await message.delete()
            warn_count = await db.warn_user(message.chat.id, message.from_user.id, violation_type)
            
            warning_msg += f"\n\n⚠️ **Warning {warn_count}/{settings.get('warn_limit', 3)}**"
            
            if warn_count >= settings.get('warn_limit', 3):
                # Auto-ban/mute after max warnings
                await client.ban_chat_member(message.chat.id, message.from_user.id)
                warning_msg += "\n\n🚫 **User has been banned for exceeding warning limit!**"
                await db.ban_user(message.chat.id, message.from_user.id, "Exceeded warning limit")
            
            await message.reply_text(warning_msg)
            
        elif action == 'mute':
            await message.delete()
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            await client.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                permissions,
                until_date=datetime.now() + timedelta(minutes=30)
            )
            await db.mute_user(message.chat.id, message.from_user.id, 1800, violation_type)
            await message.reply_text(warning_msg)
            
        elif action == 'ban':
            await message.delete()
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await db.ban_user(message.chat.id, message.from_user.id, violation_type)
            await message.reply_text(warning_msg)
        
        # Update statistics
        await db.update_stats(message.chat.id, 'deleted_messages')
