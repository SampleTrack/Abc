from pyrogram import Client, filters
from pyrogram.types import Message
from utils import ProtectionUtils
import asyncio

def register_purge_handlers(app, db):
    
    @app.on_message(filters.command("purge") & filters.group)
    async def purge_messages(client: Client, message: Message):
        """Purge messages from replied message to current"""
        if not await is_admin(client, message):
            return
        
        reply = message.reply_to_message
        if not reply:
            await message.reply_text(
                "❌ **Usage:** Reply to a message to purge from there!\n\n"
                "**Examples:**\n"
                "`/purge` - Delete from replied message to now\n"
                "`/purge all` - Delete ALL messages in group\n"
                "`/purge user` - Delete all messages from a specific user"
            )
            return
        
        # Check for special commands
        if len(message.command) > 1:
            if message.command[1].lower() == 'all':
                await purge_all_messages(client, message)
                return
            elif message.command[1].lower() == 'user':
                await purge_user_messages(client, message)
                return
        
        # Normal purge
        await normal_purge(client, message, reply)
    
    async def normal_purge(client: Client, message: Message, reply: Message):
        """Normal purge from replied message to current"""
        status_msg = await message.reply_text("🗑️ **Purging messages...**")
        
        messages_to_delete = []
        async for msg in client.get_chat_history(message.chat.id, limit=500):
            if msg.id == message.id:
                continue
            messages_to_delete.append(msg.id)
            if msg.id == reply.id:
                break
        
        if messages_to_delete:
            await client.delete_messages(message.chat.id, messages_to_delete)
            await status_msg.edit_text(f"✅ **Purged {len(messages_to_delete)} messages!**")
            await asyncio.sleep(3)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ No messages to purge!")
    
    async def purge_all_messages(client: Client, message: Message):
        """Delete ALL messages from day one"""
        confirm_msg = await message.reply_text(
            "⚠️ **DANGER ZONE!** ⚠️\n\n"
            "This will delete **ALL MESSAGES** from this group since day one!\n\n"
            "This action is **IRREVERSIBLE**!\n\n"
            "Type `/confirm` within 30 seconds to proceed."
        )
        
        # Wait for confirmation
        try:
            confirm = await client.wait_for_message(
                message.chat.id,
                filters=filters.text & filters.user(message.from_user.id),
                timeout=30
            )
            
            if confirm.text == '/confirm':
                await confirm.delete()
                await confirm_purge_all(client, message, confirm_msg)
            else:
                await confirm_msg.edit_text("❌ Purge cancelled!")
        except asyncio.TimeoutError:
            await confirm_msg.edit_text("❌ Timeout! Purge cancelled.")
    
    async def confirm_purge_all(client: Client, message: Message, status_msg: Message):
        """Execute full purge after confirmation"""
        await status_msg.edit_text("🗑️ **Starting full purge...**")
        
        total_deleted = 0
        progress_msg = await message.reply_text("Starting purge...")
        
        try:
            # Delete in batches
            async for msg in client.get_chat_history(message.chat.id, limit=10000):
                try:
                    await msg.delete()
                    total_deleted += 1
                    
                    # Update progress every 100 messages
                    if total_deleted % 100 == 0:
                        await progress_msg.edit_text(
                            ProtectionUtils.format_purge_progress(total_deleted, total_deleted + 100)
                        )
                except:
                    pass
                
                await asyncio.sleep(0.1)  # Rate limiting
            
            await progress_msg.edit_text(
                f"✅ **Full purge completed!**\n\n"
                f"🗑️ Total deleted: **{total_deleted} messages**\n"
                f"💾 Freed up chat history completely!"
            )
            
            # Log the purge
            await db.update_stats(message.chat.id, 'deleted_messages')
            
        except Exception as e:
            await progress_msg.edit_text(f"❌ Error during purge: {str(e)}")
    
    async def purge_user_messages(client: Client, message: Message):
        """Delete all messages from a specific user"""
        if not message.reply_to_message:
            await message.reply_text("❌ Reply to a user to purge their messages!")
            return
        
        target_user = message.reply_to_message.from_user
        status_msg = await message.reply_text(f"🗑️ Purging messages from {target_user.first_name}...")
        
        deleted = 0
        async for msg in client.get_chat_history(message.chat.id, limit=5000):
            if msg.from_user and msg.from_user.id == target_user.id:
                try:
                    await msg.delete()
                    deleted += 1
                except:
                    pass
        
        await status_msg.edit_text(
            f"✅ **Purged {deleted} messages** from {target_user.mention}!"
        )
    
    async def is_admin(client: Client, message: Message) -> bool:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
