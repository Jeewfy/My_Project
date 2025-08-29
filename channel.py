import asyncio
import feedparser
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from loguru import logger
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def send_news_task(bot: Bot):
    last_entries = set()
    
    while True:
        try:
            
            feed = feedparser.parse("https://www.sports.ru/rss/all_news.xml")
            
            new_entries = []
            for entry in feed.entries:
                if entry.link not in last_entries:
                    new_entries.append(entry)
                    last_entries.add(entry.link)
            
            # Отправляем новые записи
            for entry in reversed(new_entries):
                message = f"📰 {entry.title}\n\n{entry.description}\n\n🔗 Читать далее: {entry.link}"
                await bot.send_message(CHANNEL_ID, message)
                logger.success(f"Новость отправлена: {entry.title}")
                await asyncio.sleep(2) 
                
        except Exception as e:
            logger.error(f"Канал: ошибка {e}")

        await asyncio.sleep(300) 

def setup_channel_handlers(dp: Dispatcher, bot: Bot):
    

    @dp.message(Command('channel_stats'), F.chat.type == "channel")
    async def channel_stats(message: types.Message):
        await message.answer("Бот канала работает!")
        logger.info("Канал: проверка работы")