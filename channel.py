import asyncio
import requests
from bs4 import BeautifulSoup
from random import choice
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from loguru import logger
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def send_news_task(bot: Bot):
    while True:
        try:
            response = requests.get()
            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                news = soup.find_all('div', class_='text')
                news = choice(news).text.strip()
                await bot.send_message(CHANNEL_ID, f"Новость:\n{news}")
                logger.success("Новость отправлена")
            else:
                logger.warning("Канал: проблема с сайтом новостей")
        except Exception as e:
            logger.error(f"Канал: ошибка {e}")

        await asyncio.sleep(30)


def setup_channel_handlers(dp: Dispatcher, bot: Bot):
    asyncio.create_task(send_news_task(bot))

    @dp.message(Command('channel_stats'), F.chat.type == "channel")
    async def channel_stats(message: types.Message):
        await message.answer("Бот канала работает!")
        logger.info("Канал: проверка работы")