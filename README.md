# 🤖 Premium Group Manager Bot

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-red.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.5.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**A Powerful, Feature-Rich Telegram Group Management Bot with Advanced Protection**

[Features](#✨-features) • [Commands](#📝-commands) • [Deployment](#🚀-deployment) • [Configuration](#⚙️-configuration) • [Support](#📞-support)

</div>

---

## 📸 Screenshots

<div align="center">
  <img src="https://via.placeholder.com/400x800?text=Settings+Menu" width="200" alt="Settings Menu" />
  <img src="https://via.placeholder.com/400x800?text=Protection+Settings" width="200" alt="Protection Settings" />
  <img src="https://via.placeholder.com/400x800?text=Auto+Delete" width="200" alt="Auto Delete" />
  <img src="https://via.placeholder.com/400x800?text=Statistics" width="200" alt="Statistics" />
</div>

---

## ✨ Features

### 🛡️ **Advanced Protection System**
- ✅ **Anti-Forward** - Block forwarded messages
- ✅ **Anti-Link** - Block URL sharing (whitelist allowed domains)
- ✅ **Anti-Abuse** - Filter profanity and abusive words
- ✅ **Anti-Emoji** - Block specific emojis
- ✅ **Anti-Phone** - Detect and block phone numbers
- ✅ **Anti-Spam** - Prevent message spamming
- ✅ **Anti-Flood** - Stop repeated messages

### 🎮 **Admin Controls**
- 👢 **Ban/Unban** - Ban users permanently
- 🔇 **Mute/Unmute** - Mute users with time duration
- 👞 **Kick** - Kick users from group
- ⚠️ **Warning System** - Warn users with auto-ban on limit
- 🗑️ **Advanced Purge** - Delete messages (normal, all, user-specific)
- 📌 **Pin/Unpin** - Pin important messages

### ⚙️ **Customizable Settings**
- 🎛️ **Interactive UI** - Beautiful inline button menus
- 🔄 **Real-time Toggles** - Enable/disable features instantly
- ⏰ **Auto-Delete** - Automatic message deletion (5min to 6hr)
- 📊 **Statistics** - Track group activity
- 📝 **Custom Filters** - Auto-respond to keywords
- 📔 **Notes System** - Save and retrieve notes

### 🎨 **User Experience**
- 💎 **Premium UI** - Clean, modern interface with emojis
- ⚡ **Fast Response** - Instant action on violations
- 📱 **Mobile Friendly** - Perfect on all devices
- 🔔 **Real-time Updates** - Live settings changes
- 📈 **Progress Bars** - Visual feedback for long operations

---

## 📝 Commands

### 🔐 **Admin Only Commands**

| Command | Description | Usage |
|---------|-------------|--------|
| `/settings` | Open settings panel | `/settings` |
| `/ban` | Ban a user | Reply to message: `/ban <reason>` |
| `/unban` | Unban a user | `/unban <user_id>` or reply |
| `/mute` | Mute a user | Reply: `/mute 1h` (1h/1m/1d) |
| `/unmute` | Unmute a user | Reply to muted user |
| `/kick` | Kick a user | Reply to user |
| `/purge` | Delete messages | Reply to message: `/purge` |
| `/purge all` | Delete ALL messages | `/purge all` (requires confirmation) |
| `/purge user` | Delete user's messages | Reply to user |
| `/warn` | Warn a user | Reply: `/warn <reason>` |
| `/warnings` | View user warnings | Reply to user |
| `/resetwarns` | Clear user warnings | Reply to user |
| `/stats` | View group statistics | `/stats` |
| `/setdelete` | Set auto-delete interval | `/setdelete 10` (minutes) |
| `/blockedwords` | Manage blocked words | `/blockedwords add <word>` |

### 👥 **User Commands**

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help message |
| `/rules` | View group rules |
| `/report` | Report a user (reply to message) |
| `/id` | Get user/chat ID |
| `/ping` | Check bot latency |

---

## 🚀 Deployment

### 📋 **Prerequisites**

- Python 3.10 or higher
- MongoDB Database (MongoDB Atlas recommended)
- Telegram API ID & Hash (from [my.telegram.org](https://my.telegram.org))
- Bot Token (from [@BotFather](https://t.me/BotFather))

### 🖥️ **Local Deployment**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/premium-group-manager.git
cd premium-group-manager
