from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BotButtons:
    
    @staticmethod
    def main_menu():
        """Main settings menu buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛡️ Protection", callback_data="menu_protection"),
                InlineKeyboardButton("⚙️ General", callback_data="menu_general")
            ],
            [
                InlineKeyboardButton("🗑️ Auto-Delete", callback_data="menu_autodelete"),
                InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")
            ],
            [
                InlineKeyboardButton("⚠️ Warnings", callback_data="menu_warnings"),
                InlineKeyboardButton("🔨 Actions", callback_data="menu_actions")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])
    
    @staticmethod
    def protection_menu(settings: dict):
        """Protection settings buttons"""
        buttons = []
        
        # Row 1
        row = []
        status = "✅" if settings.get('anti_forward') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Forward", callback_data="toggle_anti_forward"))
        status = "✅" if settings.get('anti_link') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Link", callback_data="toggle_anti_link"))
        buttons.append(row)
        
        # Row 2
        row = []
        status = "✅" if settings.get('anti_abuse') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Abuse", callback_data="toggle_anti_abuse"))
        status = "✅" if settings.get('anti_emoji') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Emoji", callback_data="toggle_anti_emoji"))
        buttons.append(row)
        
        # Row 3
        row = []
        status = "✅" if settings.get('anti_phone') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Phone", callback_data="toggle_anti_phone"))
        status = "✅" if settings.get('anti_spam') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Spam", callback_data="toggle_anti_spam"))
        buttons.append(row)
        
        # Row 4
        row = []
        status = "✅" if settings.get('anti_flood') else "❌"
        row.append(InlineKeyboardButton(f"{status} Anti-Flood", callback_data="toggle_anti_flood"))
        buttons.append(row)
        
        # Navigation
        buttons.append([
            InlineKeyboardButton("◀️ Back", callback_data="menu_main"),
            InlineKeyboardButton("📝 Edit Filters", callback_data="edit_filters")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def general_menu(settings: dict):
        """General settings buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.get('delete_command_messages') else '❌'} Delete Commands",
                    callback_data="toggle_delete_commands"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.get('delete_service_messages') else '❌'} Delete Service Msgs",
                    callback_data="toggle_delete_service"
                )
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="menu_main"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])
    
    @staticmethod
    def autodelete_menu(settings: dict):
        """Auto-delete settings buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"{'✅' if settings.get('auto_delete') else '❌'} Auto-Delete",
                    callback_data="toggle_auto_delete"
                )
            ],
            [
                InlineKeyboardButton("⏰ 5 min", callback_data="set_interval_5"),
                InlineKeyboardButton("⏰ 10 min", callback_data="set_interval_10"),
                InlineKeyboardButton("⏰ 30 min", callback_data="set_interval_30")
            ],
            [
                InlineKeyboardButton("⏰ 1 hour", callback_data="set_interval_60"),
                InlineKeyboardButton("⏰ 6 hours", callback_data="set_interval_360")
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="menu_main"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])
    
    @staticmethod
    def actions_menu(settings: dict):
        """Action settings buttons"""
        action = settings.get('action_on_violation', 'delete')
        
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"{'✅' if action == 'delete' else '◻️'} Delete Message",
                    callback_data="set_action_delete"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if action == 'warn' else '◻️'} Warn User",
                    callback_data="set_action_warn"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if action == 'mute' else '◻️'} Mute User",
                    callback_data="set_action_mute"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if action == 'ban' else '◻️'} Ban User",
                    callback_data="set_action_ban"
                )
            ],
            [
                InlineKeyboardButton("⚠️ Warn Limit: " + str(settings.get('warn_limit', 3)),
                                   callback_data="adjust_warn_limit")
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="menu_main"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ])
    
    @staticmethod
    def stats_menu(stats: dict):
        """Statistics display buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                InlineKeyboardButton("◀️ Back", callback_data="menu_main")
            ]
        ])
    
    @staticmethod
    def warnings_menu(user_id: int, warnings: list):
        """Warnings management buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_{user_id}"),
                InlineKeyboardButton("🔇 Mute User", callback_data=f"mute_{user_id}")
            ],
            [
                InlineKeyboardButton("✅ Clear Warnings", callback_data=f"clear_warnings_{user_id}"),
                InlineKeyboardButton("◀️ Back", callback_data="menu_main")
            ]
        ])
    
    @staticmethod
    def confirmation_menu(action: str, user_id: int):
        """Confirmation buttons for dangerous actions"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}_{user_id}"),
                InlineKeyboardButton("❌ No", callback_data="cancel")
            ]
        ])
