import asyncio
import logging
from threading import Thread
from flask import Flask
from pyrogram import Client, idle
from config import Config
from database import Database
from handlers import register_all_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "Bot is alive!", 200

def run_web():
    web_app.run(host=Config.HOST, port=Config.PORT)

class PremiumGroupManager:
    def __init__(self):
        self.app = Client(
            "premium_manager",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="handlers")
        )
        self.db = Database()
    
    async def start(self):
        logger.info("🚀 Starting Premium Group Manager Bot...")
        Thread(target=run_web, daemon=True).start()
        
        await self.app.start()
        bot_info = await self.app.get_me()
        logger.info(f"✅ Bot started as @{bot_info.username}")
        
        register_all_handlers(self.app, self.db)
        asyncio.create_task(self.auto_delete_task())
        
        await idle()
        await self.app.stop()

    async def auto_delete_task(self):
        while True:
            try:
                groups = await self.db.get_all_groups()
                for group in groups:
                    if group.get('settings', {}).get('auto_delete'):
                        await self.delete_chat_messages(group['chat_id'])
                await asyncio.sleep(600)
            except Exception as e:
                logger.error(f"Auto-delete error: {e}")
                await asyncio.sleep(60)

    async def delete_chat_messages(self, chat_id):
        try:
            async for message in self.app.get_chat_history(chat_id, limit=100):
                await message.delete()
        except:
            pass

if __name__ == "__main__":
    # Explicitly create the event loop for newer Python versions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = PremiumGroupManager()
    try:
        loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
