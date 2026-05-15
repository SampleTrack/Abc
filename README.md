# 🤖 Telegram Group Ad Bot

A clean, production-ready Telegram bot for **group moderation** and **automated ad delivery** — built with Python, Pyrogram, and MongoDB.

---

## ✨ Features

### 👮 Group Moderation
- Auto welcome message for new members
- Custom welcome message per group
- Warn system with auto-ban after max warnings
- Ban / Mute / Unmute commands

### 📢 Ad Management (Owner Only)
- Schedule ads to all groups at custom intervals
- One-time broadcast to all groups
- List and stop active ads
- Background scheduler — fully automatic

---

## 🗂 Project Structure

```
telegram-group-ad-bot/
│
├── main.py                     # Entry point
├── config.py                   # Loads environment variables
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── .env.example                # Environment variable template
├── .gitignore
│
└── bot/
    ├── handlers/
    │   ├── general.py          # /start, /help, /stats
    │   ├── moderation.py       # /warn, /ban, /mute, etc.
    │   └── ads.py              # /addad, /listads, /stopad, /broadcast
    │
    ├── database/
    │   └── queries.py          # All MongoDB operations
    │
    └── scheduler/
        └── ad_jobs.py          # Background ad delivery loop
```

---

## ⚙️ Requirements

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API ID & API Hash (from [my.telegram.org](https://my.telegram.org))
- MongoDB URI (free at [MongoDB Atlas](https://cloud.mongodb.com))

---

## 🚀 Setup Guide

### Step 1 — Get Your Credentials

| Credential | Where to Get |
|---|---|
| `API_ID` & `API_HASH` | [my.telegram.org](https://my.telegram.org) → App |
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) → /newbot |
| `OWNER_ID` | [@userinfobot](https://t.me/userinfobot) |
| `MONGO_URI` | [MongoDB Atlas](https://cloud.mongodb.com) → Free Cluster |

---

### Step 2 — Clone & Configure Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/telegram-group-ad-bot.git
cd telegram-group-ad-bot

# Install dependencies
pip install -r requirements.txt

# Copy env example and fill in your values
cp .env.example .env
nano .env
```

Fill in your `.env` file:

```env
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=123456:ABC...
OWNER_ID=987654321
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=groupadbot
MAX_WARNS=3
```

---

### Step 3 — Run Locally (Testing)

```bash
python main.py
```

You should see:
```
✅ Bot started as @YourBotName
📅 Ad scheduler started.
```

---

### Step 4 — Deploy to Render

1. Push your code to GitHub (make sure `.env` is in `.gitignore` ✅)

2. Go to [render.com](https://render.com) → **New** → **Blueprint**

3. Connect your GitHub repository

4. Render will detect `render.yaml` automatically

5. Go to **Environment** tab and add these variables:

   | Key | Value |
   |---|---|
   | `API_ID` | your api id |
   | `API_HASH` | your api hash |
   | `BOT_TOKEN` | your bot token |
   | `OWNER_ID` | your telegram user id |
   | `MONGO_URI` | your mongodb connection string |

6. Click **Deploy** ✅

> **Important:** The bot is deployed as a **Worker** (not a Web Service), so it stays always-on without the free-tier sleep issue.

---

## 📖 Commands Reference

### Group Admin Commands
*(Use inside a group where the bot is admin)*

| Command | Description |
|---|---|
| `/setwelcome <text>` | Set custom welcome message for the group |
| `/warn` | Warn a user (reply to their message) |
| `/warns` | Check a user's warning count (reply) |
| `/resetwarns` | Reset a user's warnings (reply) |
| `/ban` | Ban a user from the group (reply) |
| `/mute` | Mute a user (reply) |
| `/unmute` | Unmute a user (reply) |

### Owner Commands
*(Send to the bot in private/DM)*

| Command | Description |
|---|---|
| `/addad <hours> <text>` | Schedule an ad to all groups every N hours |
| `/listads` | Show all active scheduled ads |
| `/stopad <ad_id>` | Stop a scheduled ad by its ID |
| `/broadcast <text>` | Send an instant message to all groups |
| `/stats` | Show how many groups the bot is in |

---

## 💡 Usage Examples

**Set a welcome message:**
```
/setwelcome Welcome {mention}! Please read the rules 📌
```

**Schedule an ad every 6 hours:**
```
/addad 6 🚀 Join our premium signals channel! @yourchannel
```

**Send an instant broadcast:**
```
/broadcast 📢 We just hit 10,000 members! Thank you everyone 🎉
```

**Warn a user** (reply to their message):
```
/warn
```

---

## 🔧 Configuration Options

| Variable | Default | Description |
|---|---|---|
| `MAX_WARNS` | `3` | Warnings before auto-ban |
| `DB_NAME` | `groupadbot` | MongoDB database name |

---

## 💰 Monetization Ideas

Once your bot is in multiple groups:

1. **Charge businesses** to use `/addad` — e.g. $50–$200/month per ad slot
2. **Sell broadcast slots** — one-time messages to all your groups
3. **Charge group owners** for premium moderation features
4. **Package deals** — bundle moderation + ad exposure

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| [Python 3.10+](https://python.org) | Language |
| [Pyrogram](https://pyrogram.org) | Telegram MTProto bot framework |
| [TgCrypto](https://github.com/pyrogram/tgcrypto) | Speed boost for Pyrogram |
| [Motor](https://motor.readthedocs.io) | Async MongoDB driver |
| [MongoDB Atlas](https://cloud.mongodb.com) | Cloud database (free tier) |
| [Render](https://render.com) | Deployment platform |
| [GitHub](https://github.com) | Source code & CI/CD |

---

## 🤝 Adding the Bot to a Group

1. Add the bot to your Telegram group
2. Promote it as **Admin** with these permissions:
   - ✅ Delete messages
   - ✅ Ban users
   - ✅ Restrict members
   - ✅ Pin messages (optional)
3. The bot auto-registers the group in MongoDB on first member join

---

## ⚠️ Important Notes

- Never commit your `.env` file to GitHub
- MongoDB Atlas free tier (512MB) supports hundreds of groups
- Respect Telegram's rate limits — the scheduler has a built-in 0.5s delay between messages
- Always label sponsored content clearly to comply with Telegram's Terms of Service

---

## 📄 License

MIT License — free to use, modify, and distribute.
