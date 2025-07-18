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

    @dp.message()
    async def echo(message: types.Message):
        await message.reply(message.text)
        logger.info('Бот возвратил сообщение пользователя.')

    await dp.start_polling(bot)

    from private_chat import setup_private_handlers
    from group import setup_group_handlers
    from channel import setup_channel_handlers

    setup_private_handlers(dp)
    setup_group_handlers(dp)
    setup_channel_handlers(dp, bot)

if __name__ == "__main__":
    asyncio.run(main())