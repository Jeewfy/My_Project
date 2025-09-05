import os
import asyncio
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv, find_dotenv
from loguru import logger
import pickle

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load_last_entries():
    try:
        with open('last_entries.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return set()

def save_last_entries(entries):
    with open('last_entries.pkl', 'wb') as f:
        pickle.dump(entries, f)

async def fetch_news():
    last_entries = load_last_entries()
    
    while True:
        try:
            feed = feedparser.parse("https://www.sports.ru/rss/all_news.xml")
            new_entries = []
            
            for entry in feed.entries:
                if entry.link not in last_entries:
                    new_entries.append(entry)
                    last_entries.add(entry.link)
            
            if new_entries:
                save_last_entries(last_entries)
            
            for entry in reversed(new_entries):
                message = f"<b>{entry.title}</b>\n\n{entry.description}\n\n<a href='{entry.link}'>Читать далее</a>"
                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    )
                    logger.success(f"Новость отправлена: {entry.title}")
                except Exception as send_error:
                    logger.error(f"Ошибка отправки: {send_error}")
                
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Ошибка в RSS: {e}")
        
        await asyncio.sleep(300)

@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer('Здесь должно быть приветствие')
    logger.info('Бот ответил на команду "start".')

async def main():
    logger.add('file.log',
               format='{time:YYYY-MM-DD at HH-mm-ss} | {level} | {message}',
               rotation='3 days',
               backtrace=True,
               diagnose=True)

    logger.info('Бот запускается...')
    
    from private_chat import setup_private_handlers
    from group import setup_group_handlers
    from channel import setup_channel_handlers

    setup_private_handlers(dp, ADMIN_IDS)
    setup_group_handlers(dp)
    setup_channel_handlers(dp, bot)
    
    polling_task = asyncio.create_task(dp.start_polling(bot))
    rss_task = asyncio.create_task(fetch_news())
    
    await asyncio.gather(polling_task, rss_task)

if __name__ == "__main__":
    asyncio.run(main())
