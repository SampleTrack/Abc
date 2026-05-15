from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from datetime import datetime, timedelta

def register_admin_handlers(app, db):
    
    @app.on_message(filters.command("ban") & filters.group)
    async def ban_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to ban them!")
            return
        
        user = message.reply_to_message.from_user
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else "No reason"
        
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await db.ban_user(message.chat.id, user.id, reason, message.from_user.id)
            
            await message.reply_text(
                f"✅ **Banned!**\n\n"
                f"User: {user.mention}\n"
                f"Reason: {reason}\n"
                f"Admin: {message.from_user.mention}"
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to ban: {str(e)}")
    
    @app.on_message(filters.command("unban") & filters.group)
    async def unban_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text("❌ Usage: /unban <user_id> or reply to user")
            return
        
        try:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
            else:
                user_id = int(message.command[1])
            
            await client.unban_chat_member(message.chat.id, user_id)
            await db.unban_user(message.chat.id, user_id)
            await message.reply_text(f"✅ User `{user_id}` has been unbanned!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to unban: {str(e)}")
    
    @app.on_message(filters.command("mute") & filters.group)
    async def mute_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to mute them!")
            return
        
        user = message.reply_to_message.from_user
        duration = 3600  # 1 hour default
        
        if len(message.command) > 1:
            time_str = message.command[1]
            if time_str.endswith('h'):
                duration = int(time_str[:-1]) * 3600
            elif time_str.endswith('m'):
                duration = int(time_str[:-1]) * 60
            elif time_str.endswith('d'):
                duration = int(time_str[:-1]) * 86400
        
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        
        try:
            until_date = datetime.now() + timedelta(seconds=duration)
            await client.restrict_chat_member(
                message.chat.id, 
                user.id, 
                permissions,
                until_date=until_date
            )
            
            await db.mute_user(message.chat.id, user.id, duration, "Muted by admin")
            
            await message.reply_text(
                f"🔇 **Muted!**\n\n"
                f"User: {user.mention}\n"
                f"Duration: {duration // 60} minutes"
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to mute: {str(e)}")
    
    @app.on_message(filters.command("unmute") & filters.group)
    async def unmute_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to unmute them!")
            return
        
        user = message.reply_to_message.from_user
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        
        try:
            await client.restrict_chat_member(message.chat.id, user.id, permissions)
            await db.unmute_user(message.chat.id, user.id)
            await message.reply_text(f"🔊 {user.mention} has been unmuted!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to unmute: {str(e)}")
    
    @app.on_message(filters.command("kick") & filters.group)
    async def kick_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to kick them!")
            return
        
        user = message.reply_to_message.from_user
        
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"👢 {user.mention} has been kicked!")
        except Exception as e:
            await message.reply_text(f"❌ Failed to kick: {str(e)}")
    
    @app.on_message(filters.command("warn") & filters.group)
    async def warn_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to warn them!")
            return
        
        user = message.reply_to_message.from_user
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else "No reason"
        
        warn_count = await db.warn_user(message.chat.id, user.id, reason, message.from_user.id)
        settings = await db.get_group_settings(message.chat.id)
        warn_limit = settings.get('warn_limit', 3)
        
        await message.reply_text(
            f"⚠️ **Warning Issued!**\n\n"
            f"User: {user.mention}\n"
            f"Reason: {reason}\n"
            f"Warnings: {warn_count}/{warn_limit}\n"
            f"Admin: {message.from_user.mention}"
        )
        
        if warn_count >= warn_limit:
            await client.ban_chat_member(message.chat.id, user.id)
            await db.ban_user(message.chat.id, user.id, "Exceeded warning limit", message.from_user.id)
            await message.reply_text(f"🚫 {user.mention} has been banned for exceeding warning limit!")
    
    @app.on_message(filters.command("warnings") & filters.group)
    async def warnings_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to see their warnings!")
            return
        
        user = message.reply_to_message.from_user
        warnings = await db.get_warnings(message.chat.id, user.id)
        
        if not warnings:
            await message.reply_text(f"✅ {user.mention} has no warnings!")
            return
        
        warn_text = f"⚠️ **Warnings for {user.first_name}:**\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"{i}. {warn['reason']} (by {warn.get('admin_id', 'System')})\n"
        
        await message.reply_text(warn_text)
    
    @app.on_message(filters.command("resetwarns") & filters.group)
    async def reset_warnings_command(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to reset their warnings!")
            return
        
        user = message.reply_to_message.from_user
        await db.clear_warnings(message.chat.id, user.id)
        await message.reply_text(f"✅ Cleared all warnings for {user.mention}!")
    
    @app.on_message(filters.command("stats") & filters.group)
    async def stats_command(client: Client, message: Message):
        stats = await db.get_stats(message.chat.id)
        
        stats_text = (
            "**📊 Group Statistics**\n\n"
            f"📝 Total Messages: `{stats.get('total_messages', 0)}`\n"
            f"🗑️ Deleted Messages: `{stats.get('deleted_messages', 0)}`\n"
            f"⚠️ Warnings Issued: `{stats.get('warnings_issued', 0)}`\n"
            f"🚫 Bans Issued: `{stats.get('bans_issued', 0)}`\n\n"
            f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await message.reply_text(stats_text)
    
    async def is_admin(client: Client, message: Message) -> bool:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
