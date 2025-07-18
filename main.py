import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from loguru import logger


load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')


async def main():
    logger.add('file.log',
               format='{time:YYYY-MM-DD at HH-mm-ss} | {level} | {message}',
               rotation='3 days',
               backtrace=True,
               diagnose=True)

    bot = Bot(token=TOKEN)
    logger.info('Бот создан.')
    dp = Dispatcher()
    logger.info('Диспетчер создан.')

    @dp.message(Command('start'))
    async def start_command(message: types.Message):
        await message.answer('Здесь должно быть приветствие')
        logger.info('Бот ответил на команду "start".')

    await dp.start_polling(bot)

    from private_chat import setup_private_handlers
    from group import setup_group_handlers
    from channel import setup_channel_handlers

    setup_private_handlers(dp)
    setup_group_handlers(dp)
    setup_channel_handlers(dp, bot)

if __name__ == "__main__":
    asyncio.run(main())


\async def fetch_news():
    \\last_entries = set()  # Храним последние записи, чтобы не дублировать
    \\while True:
        \\feed = feedparser.parse(RSS_URL)
       \ new_entries = []
        
        \for entry in feed.entries:
            \if entry.link not in last_entries:
           \     new_entries.append(entry)
            \    last_entries.add(entry.link)
        
        \# Отправляем новые записи в канал (в обратном порядке, чтобы сначала шли свежие)
        \for entry in reversed(new_entries):
           \ message = f"<b>{entry.title}</b>\n\n{entry.description}\n\n<a href='{entry.link}'>Читать далее</a>"
           \ await bot.send_message(
              \  chat_id=CHANNEL_ID,
               \ text=message,
               \ parse_mode="HTML",
                \disable_web_page_preview=False
            )
           \ await asyncio.sleep(2)  # Задержка между постами
        
        \await asyncio.sleep(300)  # Проверяем RSS каждые 5 минут

\async def main():
    \await asyncio.gather(
       \ dp.start_polling(bot),
        \fetch_news()
    \)

\if __name__ == "__main__":
    \asyncio.run(main())