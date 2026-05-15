from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

def register_autodelete_handlers(app, db):
    
    @app.on_message(filters.group & ~filters.service)
    async def schedule_auto_delete(client: Client, message: Message):
        """Schedule messages for auto-deletion"""
        chat_id = message.chat.id
        settings = await db.get_group_settings(chat_id)
        
        if settings.get('auto_delete', False):
            interval = settings.get('delete_interval', 10) * 60  # Convert to seconds
            
            # Schedule deletion
            asyncio.create_task(delete_after_delay(client, message, interval))
    
    async def delete_after_delay(client: Client, message: Message, delay: int):
        """Delete message after specified delay"""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass
    
    @app.on_message(filters.command("setdelete") & filters.group)
    async def set_auto_delete(client: Client, message: Message):
        """Set auto-delete interval (admin only)"""
        if not await is_admin(client, message):
            return
        
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Usage:** `/setdelete <minutes>`\n\n"
                "**Examples:**\n"
                "`/setdelete 5` - Delete after 5 minutes\n"
                "`/setdelete 10` - Delete after 10 minutes\n"
                "`/setdelete 0` - Disable auto-delete"
            )
            return
        
        try:
            minutes = int(message.command[1])
            if minutes == 0:
                await db.update_setting(message.chat.id, 'auto_delete', False)
                await message.reply_text("✅ Auto-delete **disabled**!")
            else:
                await db.update_setting(message.chat.id, 'auto_delete', True)
                await db.update_setting(message.chat.id, 'delete_interval', minutes)
                await message.reply_text(
                    f"✅ Auto-delete **enabled**!\n\n"
                    f"⏰ Messages will be deleted after **{minutes} minutes**"
                )
        except ValueError:
            await message.reply_text("❌ Please provide a valid number!")
    
    async def is_admin(client: Client, message: Message) -> bool:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
