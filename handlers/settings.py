from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from buttons import BotButtons
from utils import ProtectionUtils

def register_settings_handlers(app, db):
    
    @app.on_message(filters.command("settings") & filters.group)
    async def show_settings(client: Client, message: Message):
        """Show settings menu"""
        if not await is_admin(client, message):
            return
        
        settings = await db.get_group_settings(message.chat.id)
        stats = await db.get_stats(message.chat.id)
        
        settings_text = (
            "**⚙️ Group Manager Settings**\n\n"
            f"**Group:** {message.chat.title}\n"
            f"**Settings Version:** v2.0\n\n"
            "**Quick Stats:**\n"
            f"📊 Total Messages: {stats.get('total_messages', 0)}\n"
            f"🗑️ Deleted: {stats.get('deleted_messages', 0)}\n"
            f"⚠️ Warnings: {stats.get('warnings_issued', 0)}\n"
            f"🚫 Bans: {stats.get('bans_issued', 0)}\n\n"
            "**Configure your group protection below:**"
        )
        
        await message.reply_text(
            settings_text,
            reply_markup=BotButtons.main_menu()
        )
    
    @app.on_callback_query()
    async def handle_settings_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle all settings button callbacks"""
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        
        # Verify admin
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in ['administrator', 'creator']:
            await callback_query.answer("⚠️ Admin only!", show_alert=True)
            return
        
        settings = await db.get_group_settings(chat_id)
        
        # Main menu navigation
        if data == "menu_main":
            await callback_query.message.edit_text(
                "**⚙️ Group Manager Settings**\n\nChoose a category:",
                reply_markup=BotButtons.main_menu()
            )
        
        elif data == "menu_protection":
            await callback_query.message.edit_text(
                "**🛡️ Protection Settings**\n\n"
                "Configure what to filter in your group:\n"
                "✅ = Enabled | ❌ = Disabled",
                reply_markup=BotButtons.protection_menu(settings)
            )
        
        elif data == "menu_general":
            await callback_query.message.edit_text(
                "**⚙️ General Settings**\n\n"
                "Configure general bot behavior:",
                reply_markup=BotButtons.general_menu(settings)
            )
        
        elif data == "menu_autodelete":
            await callback_query.message.edit_text(
                "**🗑️ Auto-Delete Settings**\n\n"
                f"Current interval: **{settings.get('delete_interval', 10)} minutes**\n\n"
                "Messages will be automatically deleted after the selected time:",
                reply_markup=BotButtons.autodelete_menu(settings)
            )
        
        elif data == "menu_actions":
            await callback_query.message.edit_text(
                "**🔨 Action Settings**\n\n"
                "Choose what happens when a violation is detected:\n\n"
                f"Current action: **{settings.get('action_on_violation', 'delete').upper()}**\n"
                f"Warning limit: **{settings.get('warn_limit', 3)}**",
                reply_markup=BotButtons.actions_menu(settings)
            )
        
        elif data == "menu_stats":
            stats = await db.get_stats(chat_id)
            stats_text = (
                "**📊 Group Statistics**\n\n"
                f"📝 Total Messages: `{stats.get('total_messages', 0)}`\n"
                f"🗑️ Deleted Messages: `{stats.get('deleted_messages', 0)}`\n"
                f"⚠️ Warnings Issued: `{stats.get('warnings_issued', 0)}`\n"
                f"🚫 Bans Issued: `{stats.get('bans_issued', 0)}`\n\n"
                f"🕐 Last Updated: Just now"
            )
            await callback_query.message.edit_text(
                stats_text,
                reply_markup=BotButtons.stats_menu(stats)
            )
        
        # Toggle settings
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            current = settings.get(setting, False)
            await db.update_setting(chat_id, setting, not current)
            
            # Refresh menu
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.protection_menu(new_settings)
            )
            await callback_query.answer(f"{'Enabled' if not current else 'Disabled'} {setting}!")
        
        elif data.startswith("set_interval_"):
            minutes = int(data.replace("set_interval_", ""))
            await db.update_setting(chat_id, 'delete_interval', minutes)
            await db.update_setting(chat_id, 'auto_delete', True)
            await callback_query.answer(f"Auto-delete set to {minutes} minutes!")
            
            # Refresh menu
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.autodelete_menu(new_settings)
            )
        
        elif data.startswith("set_action_"):
            action = data.replace("set_action_", "")
            await db.update_setting(chat_id, 'action_on_violation', action)
            await callback_query.answer(f"Action set to {action}!")
            
            # Refresh menu
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.actions_menu(new_settings)
            )
        
        elif data == "toggle_auto_delete":
            current = settings.get('auto_delete', False)
            await db.update_setting(chat_id, 'auto_delete', not current)
            await callback_query.answer(f"Auto-delete {'enabled' if not current else 'disabled'}!")
            
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.autodelete_menu(new_settings)
            )
        
        elif data == "toggle_delete_commands":
            current = settings.get('delete_command_messages', True)
            await db.update_setting(chat_id, 'delete_command_messages', not current)
            await callback_query.answer(f"Command deletion {'enabled' if not current else 'disabled'}!")
            
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.general_menu(new_settings)
            )
        
        elif data == "toggle_delete_service":
            current = settings.get('delete_service_messages', True)
            await db.update_setting(chat_id, 'delete_service_messages', not current)
            await callback_query.answer(f"Service message deletion {'enabled' if not current else 'disabled'}!")
            
            new_settings = await db.get_group_settings(chat_id)
            await callback_query.message.edit_reply_markup(
                reply_markup=BotButtons.general_menu(new_settings)
            )
        
        elif data == "close":
            await callback_query.message.delete()
            await callback_query.answer()
        
        elif data == "refresh_stats":
            stats = await db.get_stats(chat_id)
            stats_text = (
                "**📊 Group Statistics**\n\n"
                f"📝 Total Messages: `{stats.get('total_messages', 0)}`\n"
                f"🗑️ Deleted Messages: `{stats.get('deleted_messages', 0)}`\n"
                f"⚠️ Warnings Issued: `{stats.get('warnings_issued', 0)}`\n"
                f"🚫 Bans Issued: `{stats.get('bans_issued', 0)}`\n\n"
                f"🕐 Last Updated: Just now"
            )
            await callback_query.message.edit_text(
                stats_text,
                reply_markup=BotButtons.stats_menu(stats)
            )
            await callback_query.answer("Statistics refreshed!")
    
    # Command to edit blocked words
    @app.on_message(filters.command("blockedwords") & filters.group)
    async def edit_blocked_words(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        
        if len(message.command) < 2:
            await message.reply_text(
                "**📝 Blocked Words Management**\n\n"
                "`/blockedwords add <word>` - Add blocked word\n"
                "`/blockedwords remove <word>` - Remove blocked word\n"
                "`/blockedwords list` - List all blocked words\n"
                "`/blockedwords clear` - Clear all blocked words"
            )
            return
        
        action = message.command[1].lower()
        settings = await db.get_group_settings(message.chat.id)
        blocked_words = settings.get('blocked_words', [])
        
        if action == "add" and len(message.command) > 2:
            word = message.command[2].lower()
            if word not in blocked_words:
                blocked_words.append(word)
                await db.update_setting(message.chat.id, 'blocked_words', blocked_words)
                await message.reply_text(f"✅ Added `{word}` to blocked words!")
        
        elif action == "remove" and len(message.command) > 2:
            word = message.command[2].lower()
            if word in blocked_words:
                blocked_words.remove(word)
                await db.update_setting(message.chat.id, 'blocked_words', blocked_words)
                await message.reply_text(f"✅ Removed `{word}` from blocked words!")
        
        elif action == "list":
            if blocked_words:
                words_list = "\n".join([f"• `{word}`" for word in blocked_words])
                await message.reply_text(f"**📝 Blocked Words:**\n\n{words_list}")
            else:
                await message.reply_text("❌ No blocked words configured!")
        
        elif action == "clear":
            await db.update_setting(message.chat.id, 'blocked_words', [])
            await message.reply_text("✅ Cleared all blocked words!")
    
    async def is_admin(client: Client, message: Message) -> bool:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
