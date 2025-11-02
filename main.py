import os
import asyncio
import feedparser

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from database import db
import pickle

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

bot = Bot(token=TOKEN)
dp = Dispatcher()


def load_last_entries():
    """Загрузка последних записей RSS из файла"""
    try:
        with open('last_entries.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return set()


def save_last_entries(entries):
    """Сохранение последних записей RSS в файл"""
    with open('last_entries.pkl', 'wb') as f:
        pickle.dump(entries, f)


async def fetch_news():
    """Фоновая задача для получения и отправки новостей RSS"""
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
                logger.info(f"Найдено {len(new_entries)} новых новостей")

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
                        logger.error(f"Ошибка отправки новости: {send_error}")

                    await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Ошибка в RSS парсере: {e}")

        await asyncio.sleep(300)


async def setup_handlers():
    """Настройка всех обработчиков"""
    try:

        from private_chat import setup_private_handlers
        from group import setup_group_handlers
        from channel import setup_channel_handlers

        setup_private_handlers(dp, ADMIN_IDS)
        setup_group_handlers(dp)
        setup_channel_handlers(dp, bot)

        logger.success("Все обработчики успешно настроены")
    except Exception as e:
        logger.error(f"Ошибка настройки обработчиков: {e}")
        raise


async def on_startup():
    """Действия при запуске бота"""
    logger.info("Бот запускается...")
    try:
        await db.init_db()
        logger.success("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise

    bot_info = await bot.get_me()
    logger.success(f"Бот @{bot_info.username} успешно запущен!")
    logger.info(f"ID бота: {bot_info.id}")
    logger.info(f"Имя бота: {bot_info.first_name}")

    if not TOKEN:
        logger.error("Токен бота не найден!")
        raise ValueError("Токен бота не установлен")

    if not CHANNEL_ID:
        logger.warning("CHANNEL_ID не установлен, RSS функционал может не работать")

    if not ADMIN_IDS:
        logger.warning("ADMIN_IDS не установлены, админские функции недоступны")
    else:
        logger.info(f"Загружено {len(ADMIN_IDS)} администраторов")


async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Бот останавливается...")
    await bot.session.close()
    logger.success("Бот успешно остановлен")


async def main():
    """Основная функция запуска бота"""

    logger.add(
        'bot.log',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}',
        rotation='10 MB',
        retention='30 days',
        compression='zip',
        level='INFO',
        backtrace=True,
        diagnose=True
    )

    logger.add(
        lambda msg: print(msg, flush=True),
        format='<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>',
        level='INFO',
        colorize=True
    )

    try:

        await on_startup()

        await setup_handlers()

        logger.info("Запуск поллинга и RSS задачи...")

        polling_task = asyncio.create_task(
            dp.start_polling(bot),
            name="PollingTask"
        )
        rss_task = asyncio.create_task(
            fetch_news(),
            name="RSSTask"
        )

        await asyncio.gather(polling_task, rss_task)

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:

        await on_shutdown()


@dp.message(Command('bot_stats'))
async def bot_stats_command(message: types.Message):
    """Статистика бота для админов"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Эта команда доступна только администраторам")
        return

    try:

        stats = await db.get_total_stats()

        import psutil
        import platform
        from datetime import datetime

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        stats_text = (
            "🤖 <b>Статистика бота:</b>\n\n"
            f"📊 <b>Пользователи:</b>\n"
            f"• Всего пользователей: {stats['total_users']}\n"
            f"• Всего сообщений: {stats['total_messages']}\n"
            f"• Обращений в поддержку: {stats['total_feedback']}\n\n"
            f"🖥 <b>Система:</b>\n"
            f"• OS: {platform.system()} {platform.release()}\n"
            f"• CPU: {psutil.cpu_percent()}%\n"
            f"• RAM: {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)\n"
            f"• Disk: {disk.percent}% ({disk.used//1024//1024//1024}GB/{disk.total//1024//1024//1024}GB)\n\n"
            f"⏰ <b>Время:</b>\n"
            f"• Сервер: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• Админов: {len(ADMIN_IDS)}\n"
            f"• RSS: 🔄 Активен\n"
        )

        await message.answer(stats_text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await message.answer("❌ Ошибка получения статистики")


@dp.message(Command('db_backup'))
async def db_backup_command(message: types.Message):
    """Создание резервной копии базы данных"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Эта команда доступна только администраторам")
        return

    try:
        import shutil
        from datetime import datetime

        backup_name = f"backup_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('bot.db', backup_name)

        await message.answer(f"✅ Резервная копия создана: `{backup_name}`", parse_mode="Markdown")
        logger.info(f"Создана резервная копия БД: {backup_name}")

    except Exception as e:
        logger.error(f"Ошибка создания резервной копии: {e}")
        await message.answer("❌ Ошибка создания резервной копии")


@dp.message(Command('user_info'))
async def user_info_command(message: types.Message):
    """Информация о пользователе"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Эта команда доступна только администраторам")
        return

    try:

        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /user_info <user_id>")
            return

        user_id = int(args[1])
        user_stats = await db.get_user_stats(user_id)

        if not user_stats:
            await message.answer(f"❌ Пользователь с ID {user_id} не найден в базе данных")
            return

        (user_id, username, first_name, last_name,
         messages_count, warnings_count, first_seen, last_seen) = user_stats

        user_info_text = (
            f"👤 <b>Информация о пользователе:</b>\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name or 'Не указано'} {last_name or ''}\n"
            f"📛 Username: @{username or 'Не указан'}\n"
            f"📨 Сообщений: {messages_count}\n"
            f"⚠️ Предупреждений: {warnings_count}\n"
            f"📅 Первый визит: {first_seen}\n"
            f"🕒 Последний визит: {last_seen}\n"
        )

        await message.answer(user_info_text, parse_mode="HTML")

    except ValueError:
        await message.answer("❌ Неверный формат ID пользователя")
    except Exception as e:
        logger.error(f"Ошибка получения информации о пользователе: {e}")
        await message.answer("❌ Ошибка получения информации о пользователе")

if __name__ == "__main__":

    os.makedirs('logs', exist_ok=True)

    logger.info("Запуск приложения...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}")
    finally:
        logger.info("Приложение завершило работу")
