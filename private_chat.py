from aiogram import Dispatcher, types, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
import aiosqlite
from datetime import datetime
import os


from keyboards import (
    get_main_keyboard,
    get_games_keyboard,
    get_back_keyboard,
    get_channel_inline_keyboard,
    get_feedback_inline_keyboard,
    get_settings_keyboard,
    get_notifications_keyboard,
    get_language_keyboard
)

CHANNEL_ID = os.getenv('CHANNEL_ID')

class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

class SettingsState(StatesGroup):
    waiting_for_settings = State()

def setup_private_handlers(dp: Dispatcher, admin_ids: list):
    
    @dp.startup()
    async def on_startup():
        async with aiosqlite.connect('bot.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS user_stats 
                             (user_id INTEGER PRIMARY KEY, messages INTEGER DEFAULT 0, 
                             warnings INTEGER DEFAULT 0)''')
            await db.commit()
        logger.info("База данных инициализирована")
    
    
    @dp.message(Command('start'))
    async def start_command(message: types.Message):
        welcome_text = (
            "🤖 <b>Добро пожаловать в спортивный бот!</b>\n\n"
            "Здесь вы можете:\n"
            "• 📊 Посмотреть статистику\n"
            "• 📝 Оставить обратную связь\n"
            "• 🎮 Поиграть в игры\n"
            "• 📢 Получить информацию о канале\n\n"
            "Выберите действие на клавиатуре ниже 👇"
        )
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard())
        logger.info(f'Пользователь {message.from_user.id} начал чат')

    
    @dp.message(F.text == "📊 Статистика")
    async def stats_button(message: types.Message):
        if message.from_user.id in admin_ids:
            try:
                async with aiosqlite.connect('bot.db') as db:
                    cursor = await db.execute('SELECT COUNT(*) FROM user_stats')
                    total_users = (await cursor.fetchone())[0]
                    
                    cursor = await db.execute('SELECT SUM(messages) FROM user_stats')
                    total_messages = (await cursor.fetchone())[0] or 0
                    
                await message.answer(
                    f"📊 <b>Статистика бота:</b>\n\n"
                    f"👥 Пользователей: {total_users}\n"
                    f"💬 Сообщений: {total_messages}\n"
                    f"🕒 Время: {datetime.now().strftime('%H:%M:%S')}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка получения статистики: {e}")
                await message.answer("❌ Ошибка получения статистики")
        else:
            await message.answer("📊 Статистика доступна только администраторам")

    @dp.message(F.text == "📝 Обратная связь")
    async def feedback_button(message: types.Message, state: FSMContext):
        await message.answer(
            "📝 Напишите ваше предложение или жалобу:",
            reply_markup=get_back_keyboard()
        )
        
        await message.answer(
            "Или воспользуйтесь быстрыми опциями:",
            reply_markup=get_feedback_inline_keyboard()
        )
        await state.set_state(FeedbackState.waiting_for_feedback)

    @dp.message(F.text == "❓ Помощь")
    async def help_button(message: types.Message):
        help_text = (
            "🤖 <b>Команды и возможности бота:</b>\n\n"
            "📊 <b>Статистика</b> - просмотр статистики (админы)\n"
            "📝 <b>Обратная связь</b> - отправить предложение\n"
            "🎮 <b>Игры</b> - мини-игры для развлечения\n"
            "📢 <b>Канал</b> - информация о спортивном канале\n\n"
            "⚽ <b>В группах:</b>\n"
            "• Автоматическая модерация чата\n"
            "• Игра в угадай число\n"
            "• Фильтр запрещенных слов\n\n"
            "📢 <b>В канале:</b>\n"
            "• Автоматические спортивные новости\n"
            "• Ежедневные обновления"
        )
        await message.answer(help_text, parse_mode="HTML")

    @dp.message(F.text == "📢 Канал")
    async def channel_info(message: types.Message):
        channel_info_text = (
            "📢 <b>Наш спортивный канал:</b>\n\n"
            "⚽ Самые свежие спортивные новости\n"
            "🏆 Обзоры матчей и трансляции\n"
            "🎯 Эксклюзивные интервью\n"
            "📊 Статистика и аналитика\n\n"
            "Подпишитесь, чтобы быть в курсе всех событий!"
        )
        await message.answer(
            channel_info_text, 
            parse_mode="HTML",
            reply_markup=get_channel_inline_keyboard()
        )

    @dp.message(F.text == "🎮 Игры")
    async def games_menu(message: types.Message):
        await message.answer(
            "🎮 <b>Выберите игру:</b>\n\n"
            "🎯 Угадай число - классическая игра\n"
            "🎲 Случайное число - генератор чисел",
            parse_mode="HTML",
            reply_markup=get_games_keyboard()
        )

    @dp.message(F.text == "🎯 Угадай число")
    async def guess_number_game(message: types.Message):
        import random
        number = random.randint(1, 100)
        await message.answer(
            f"🎯 Я загадал число от 1 до 100!\n"
            f"Попробуй угадать: /guess число\n\n"
            f"Например: <code>/guess 42</code>",
            parse_mode="HTML"
        )

    @dp.message(F.text == "🎲 Случайное число")
    async def random_number(message: types.Message):
        import random
        number = random.randint(1, 1000)
        await message.answer(f"🎲 Ваше случайное число: <b>{number}</b>", parse_mode="HTML")

    @dp.message(F.text == "⚙️ Настройки")
    async def settings_button(message: types.Message):
        await message.answer(
            "⚙️ <b>Настройки:</b>\n\n"
            "Выберите опцию:",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )

    @dp.message(F.text == "🔔 Уведомления")
    async def notifications_settings(message: types.Message):
        await message.answer(
            "🔔 <b>Настройки уведомлений:</b>\n\n"
            "Выберите статус уведомлений:",
            parse_mode="HTML",
            reply_markup=get_notifications_keyboard()
        )

    @dp.message(F.text == "🌐 Язык")
    async def language_settings(message: types.Message):
        await message.answer(
            "🌐 <b>Выбор языка:</b>\n\n"
            "Select language:",
            parse_mode="HTML",
            reply_markup=get_language_keyboard()
        )

    @dp.message(F.text == "🔙 Назад")
    async def back_button(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state:
            await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())

    
    @dp.message(FeedbackState.waiting_for_feedback)
    async def process_feedback(message: types.Message, state: FSMContext, bot: Bot):
        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Главное меню:", reply_markup=get_main_keyboard())
            return

        feedback_text = message.text
        user = message.from_user
        
        
        for admin_id in admin_ids:
            try:
                await bot.send_message(
                    admin_id,
                    f"📩 Новый фидбек от @{user.username or user.first_name} (ID: {user.id}):\n\n{feedback_text}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки фидбека админу {admin_id}: {e}")
        
        await message.answer(
            "✅ Спасибо за ваш отзыв! Мы его рассмотрим.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

    
    @dp.message(Command('guess'))
    async def guess_command(message: types.Message):
        try:
            guess = int(message.text.split()[1])
            import random
            secret = random.randint(1, 100)
            
            if guess == secret:
                await message.answer(f"🎉 Угадал! Это действительно {secret}!")
            else:
                await message.answer(f"❌ Не угадал! Я загадал {secret}. Попробуй еще!")
                
        except (IndexError, ValueError):
            await message.answer("Используйте: /guess число (от 1 до 100)")

    
    @dp.callback_query(F.data == "check_subscription")
    async def check_subscription_callback(callback: types.CallbackQuery, bot: Bot):
        try:
            user_id = callback.from_user.id
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            
            if member.status in ['member', 'administrator', 'creator']:
                await callback.answer("✅ Вы подписаны на канал!", show_alert=True)
            else:
                await callback.answer("❌ Вы не подписаны на канал!", show_alert=True)
                
        except Exception as e:
            await callback.answer("❌ Ошибка проверки подписки", show_alert=True)

    @dp.callback_query(F.data.startswith("notifications_"))
    async def notifications_callback(callback: types.CallbackQuery):
        action = callback.data.split("_")[1]
        if action == "on":
            await callback.answer("✅ Уведомления включены!", show_alert=False)
        else:
            await callback.answer("❌ Уведомления выключены!", show_alert=False)

    @dp.callback_query(F.data.startswith("lang_"))
    async def language_callback(callback: types.CallbackQuery):
        lang = callback.data.split("_")[1]
        languages = {"ru": "Русский", "en": "English", "es": "Español"}
        await callback.answer(f"🌐 Язык изменен на {languages.get(lang, lang)}!", show_alert=False)

    
    @dp.message(F.chat.type == "private")
    async def private_message_stats(message: types.Message):
        user_id = message.from_user.id
        
        
        try:
            async with aiosqlite.connect('bot.db') as db:
                await db.execute(
                    'INSERT OR IGNORE INTO user_stats (user_id, messages) VALUES (?, 1)',
                    (user_id,)
                )
                await db.execute(
                    'UPDATE user_stats SET messages = messages + 1 WHERE user_id = ?',
                    (user_id,)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
            
        
        
        if message.text not in ["📊 Статистика", "📝 Обратная связь", "❓ Помощь", 
                               "📢 Канал", "🎮 Игры", "⚙️ Настройки", "🔙 Назад",
                               "🔔 Уведомления", "🌐 Язык"]:
            await message.answer(
                "Выберите действие на клавиатуре ниже 👇",
                reply_markup=get_main_keyboard()
            )