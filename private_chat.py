import asyncio
import os
import aiosqlite
from aiogram import Dispatcher, types, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

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

from database import db

CHANNEL_ID = os.getenv('CHANNEL_ID')


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


class GameState(StatesGroup):
    waiting_for_guess = State()
    playing_number_game = State()


class SettingsState(StatesGroup):
    waiting_for_language = State()
    waiting_for_notifications = State()


class SupportState(StatesGroup):
    waiting_for_support_message = State()


class AdminState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_broadcast_message = State()


def setup_private_handlers(dp: Dispatcher, admin_ids: list):

    @dp.startup()
    async def on_startup():
        """Инициализация базы данных при запуске"""
        logger.info("Обработчики личных сообщений загружены")

    @dp.message(Command('start'))
    async def start_command(message: types.Message):
        user = message.from_user
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }

        await db.add_or_update_user(user_data)

        await db.log_user_action(user.id, 'start_command', 'Пользователь начал чат')

        welcome_text = (
            f"👋 <b>Привет, {user.first_name}!</b>\n\n"
            "🤖 Я - спортивный бот, твой помощник в мире спорта!\n\n"
            "✨ <b>Что я умею:</b>\n"
            "• 📊 Показывать статистику\n"
            "• 📝 Принимать обратную связь\n"
            "• 🎮 Играть в мини-игры\n"
            "• 📢 Делиться спортивными новостями\n"
            "• ⚽ Модерировать групповые чаты\n\n"
            "🎯 <b>Давайте начнем!</b> Выберите действие в меню ниже 👇"
        )

        await message.answer(welcome_text, parse_mode="HTML")
        await asyncio.sleep(0.5)
        await message.answer(
            "🛠 <b>Главное меню</b>\n"
            "Выберите нужный раздел:",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

        logger.info(f'Пользователь {user.id} начал чат')

    @dp.message(F.text == "📊 Статистика")
    async def stats_button(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'stats_button_click')

        if user_id in admin_ids:
            try:

                stats = await db.get_total_stats()
                user_stats = await db.get_user_stats(user_id)

                admin_stats_text = (
                    f"📊 <b>Статистика бота (Админ):</b>\n\n"
                    f"👥 Всего пользователей: {stats['total_users']}\n"
                    f"💬 Всего сообщений: {stats['total_messages']}\n"
                    f"📝 Обращений в поддержку: {stats['total_feedback']}\n"
                    f"🕒 Время: {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"<b>Ваша статистика:</b>\n"
                    f"📨 Ваших сообщений: {user_stats[4] if user_stats else 0}\n"
                    f"📅 С нами с: {user_stats[6].split()[0] if user_stats else 'Недавно'}"
                )

                await message.answer(admin_stats_text, parse_mode="HTML")

            except Exception as e:
                logger.error(f"Ошибка получения статистики: {e}")
                await message.answer("❌ Ошибка получения статистики")
        else:

            user_stats = await db.get_user_stats(user_id)
            user_stats_text = (
                f"📊 <b>Ваша статистика:</b>\n\n"
                f"👤 Имя: {message.from_user.first_name}\n"
                f"📨 Отправлено сообщений: {user_stats[4] if user_stats else 1}\n"
                f"📅 С нами с: {user_stats[6].split()[0] if user_stats else 'Сегодня'}\n"
                f"🕒 Последняя активность: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"💡 <i>Больше статистики доступно администраторам</i>"
            )
            await message.answer(user_stats_text, parse_mode="HTML")

    @dp.message(F.text == "📝 Обратная связь")
    async def feedback_button(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'feedback_button_click')

        await message.answer(
            "📝 <b>Обратная связь</b>\n\n"
            "Напишите ваше предложение, пожелание или сообщите о проблеме:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

        await message.answer(
            "📞 <b>Быстрые опции:</b>",
            parse_mode="HTML",
            reply_markup=get_feedback_inline_keyboard()
        )
        await state.set_state(FeedbackState.waiting_for_feedback)

    @dp.message(FeedbackState.waiting_for_feedback)
    async def process_feedback(message: types.Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id

        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Главное меню:", reply_markup=get_main_keyboard())
            return

        feedback_text = message.text
        user = message.from_user

        await db.add_feedback(user_id, feedback_text)
        await db.log_user_action(user_id, 'feedback_sent', f"Длина: {len(feedback_text)}")

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

    @dp.message(Command('support'))
    async def support_command(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'support_command')

        await message.answer(
            "🆘 <b>Поддержка</b>\n\n"
            "Опишите вашу проблему или вопрос, и мы обязательно поможем:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(SupportState.waiting_for_support_message)

    @dp.message(SupportState.waiting_for_support_message)
    async def process_support_message(message: types.Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id

        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Главное меню:", reply_markup=get_main_keyboard())
            return

        support_text = message.text
        user = message.from_user

        await db.add_feedback(user_id, f"SUPPORT: {support_text}")
        await db.log_user_action(user_id, 'support_sent', f"Длина: {len(support_text)}")

        for admin_id in admin_ids:
            try:
                await bot.send_message(
                    admin_id,
                    f"🆘 Новое обращение в поддержку от @{user.username or user.first_name} (ID: {user.id}):\n\n{support_text}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки обращения админу {admin_id}: {e}")

        await message.answer(
            "✅ Ваше обращение принято! Мы ответим в ближайшее время.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

    @dp.message(Command('users'))
    async def show_users(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        if user_id not in admin_ids:
            await message.answer("❌ Эта команда доступна только администраторам")
            return

        try:
            users = await db.get_all_users()
            if not users:
                await message.answer("📭 В базе данных пока нет пользователей")
                return

            users_text = "👥 <b>Список пользователей:</b>\n\n"
            for i, user in enumerate(users[:10], 1):
                user_id, username, first_name, last_name, messages_count, first_seen, last_seen = user
                name = f"{first_name or ''} {last_name or ''}".strip() or "Без имени"
                username_str = f"(@{username})" if username else ""

                users_text += (
                    f"{i}. {name} {username_str}\n"
                    f"   ID: {user_id} | Сообщений: {messages_count}\n"
                    f"   Первый визит: {first_seen.split()[0]}\n"
                    f"   Последний: {last_seen.split()[0]}\n\n"
                )

            if len(users) > 10:
                users_text += f"<i>... и еще {len(users) - 10} пользователей</i>"

            await message.answer(users_text, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Ошибка получения списка пользователей: {e}")
            await message.answer("❌ Ошибка получения списка пользователей")

    @dp.message(F.text == "❓ Помощь")
    async def help_button(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'help_button_click')

        help_text = (
            "🤖 <b>Команды и возможности бота:</b>\n\n"
            "📊 <b>Статистика</b> - просмотр статистики\n"
            "📝 <b>Обратная связь</b> - отправить предложение\n"
            "🎮 <b>Игры</b> - мини-игры для развлечения\n"
            "📢 <b>Канал</b> - информация о спортивном канале\n\n"
            "⚽ <b>В группах:</b>\n"
            "• Автоматическая модерация чата\n"
            "• Игра в угадай число\n"
            "• Фильтр запрещенных слов\n\n"
            "📢 <b>В канале:</b>\n"
            "• Автоматические спортивные новости\n"
            "• Ежедневные обновления\n\n"
            "💡 <b>Новые команды:</b>\n"
            "• /support - связь с поддержкой\n"
            "• /broadcast - рассылка (админы)\n\n"
            "🎯 <b>Начните с главного меню!</b>"
        )
        await message.answer(help_text, parse_mode="HTML")

    @dp.message(F.text == "📢 Канал")
    async def channel_info(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'channel_info_click')

        channel_info_text = (
            "📢 <b>Наш спортивный канал:</b>\n\n"
            "⚽ Самые свежие спортивные новости\n"
            "🏆 Обзоры матчей и трансляции\n"
            "🎯 Эксклюзивные интервью\n"
            "📊 Статистика и аналитика\n\n"
            "🔥 Подпишитесь, чтобы быть в курсе всех событий!"
        )
        await message.answer(
            channel_info_text,
            parse_mode="HTML",
            reply_markup=get_channel_inline_keyboard()
        )

    @dp.message(F.text == "🎮 Игры")
    async def games_menu(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'games_menu_click')

        await message.answer(
            "🎮 <b>Игровая зона!</b>\n\n"
            "Выберите игру:\n"
            "🎯 Угадай число - классическая игра на удачу\n"
            "🎲 Случайное число - мгновенный генератор чисел\n\n"
            "Давайте повеселимся! 🎉",
            parse_mode="HTML",
            reply_markup=get_games_keyboard()
        )

    @dp.message(F.text == "🎯 Угадай число")
    async def start_number_game(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'start_number_game')

        import random
        secret_number = random.randint(1, 100)
        attempts = 0

        await state.update_data(
            secret_number=secret_number,
            attempts=attempts,
            max_attempts=10
        )

        await message.answer(
            f"🎯 <b>Угадай число от 1 до 100!</b>\n\n"
            f"У тебя есть 10 попыток.\n"
            f"Просто напиши число в чат!\n\n"
            f"💡 <i>Используй '🔙 Назад' чтобы выйти из игры</i>",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

        await state.set_state(GameState.playing_number_game)

    @dp.message(GameState.playing_number_game)
    async def process_game_guess(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Игра завершена!", reply_markup=get_main_keyboard())
            await db.log_user_action(user_id, 'game_exited')
            return

        try:
            guess = int(message.text)
            user_data = await state.get_data()
            secret_number = user_data['secret_number']
            attempts = user_data['attempts'] + 1
            max_attempts = user_data['max_attempts']

            await state.update_data(attempts=attempts)

            if guess < 1 or guess > 100:
                await message.answer("📏 Число должно быть от 1 до 100!")
                return

            if guess < secret_number:
                await message.answer(f"🔺 Число БОЛЬШЕ чем {guess}\n"
                                   f"Попытка: {attempts}/{max_attempts}")
            elif guess > secret_number:
                await message.answer(f"🔻 Число МЕНЬШЕ чем {guess}\n"
                                   f"Попытка: {attempts}/{max_attempts}")
            else:

                await message.answer(
                    f"🎉 <b>ПОБЕДА!</b> 🎉\n\n"
                    f"✅ Ты угадал число {secret_number}!\n"
                    f"🎯 Попыток использовано: {attempts}\n\n"
                    f"Хочешь сыграть еще? Нажми '🎮 Игры'",
                    parse_mode="HTML",
                    reply_markup=get_main_keyboard()
                )
                await db.log_user_action(user_id, 'game_won', f"Число: {secret_number}, Попыток: {attempts}")
                await state.clear()
                return

            if attempts >= max_attempts:
                await message.answer(
                    f"💔 <b>Игра окончена!</b>\n\n"
                    f"❌ Ты исчерпал все попытки.\n"
                    f"🔢 Загаданное число было: {secret_number}\n\n"
                    f"Попробуй еще раз! 🎯",
                    parse_mode="HTML",
                    reply_markup=get_main_keyboard()
                )
                await db.log_user_action(user_id, 'game_lost', f"Число: {secret_number}")
                await state.clear()

        except ValueError:
            await message.answer("❌ Пожалуйста, введи число от 1 до 100!")

    @dp.message(F.text == "🎲 Случайное число")
    async def random_number(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'random_number_click')

        import random
        number = random.randint(1, 1000)
        await message.answer(
            f"🎲 <b>Случайное число:</b>\n\n"
            f"Ваше число: <b>{number}</b>\n\n"
            f"Может быть, это ваше счастливое число? 😊",
            parse_mode="HTML"
        )

    @dp.message(F.text == "⚙️ Настройки")
    async def settings_button(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'settings_button_click')

        await message.answer(
            "⚙️ <b>Настройки</b>\n\n"
            "Выберите опцию для настройки:",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )

    @dp.message(F.text == "🔔 Уведомления")
    async def notifications_settings(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'notifications_settings_click')

        await message.answer(
            "🔔 <b>Настройки уведомлений</b>\n\n"
            "Выберите статус уведомлений:",
            parse_mode="HTML",
            reply_markup=get_notifications_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_notifications)

    @dp.message(F.text == "🌐 Язык")
    async def language_settings(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'language_settings_click')

        await message.answer(
            "🌐 <b>Выбор языка</b>\n\n"
            "Выберите язык интерфейса:",
            parse_mode="HTML",
            reply_markup=get_language_keyboard()
        )
        await state.set_state(SettingsState.waiting_for_language)

    @dp.message(F.text == "🔙 Назад")
    async def back_button(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'back_button_click')

        current_state = await state.get_state()
        if current_state:
            await state.clear()
            await message.answer("✅ Действие отменено", reply_markup=get_main_keyboard())
        else:
            await message.answer(
                "🏠 <b>Главное меню</b>\n"
                "Выберите нужный раздел:",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )

    @dp.message(Command('guess'))
    async def guess_command(message: types.Message):
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'guess_command_used')

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

    @dp.message(
        F.chat.type == "private",
        ~F.text.in_([
            "📊 Статистика", "📝 Обратная связь", "❓ Помощь",
            "📢 Канал", "🎮 Игры", "⚙️ Настройки", "🔙 Назад",
            "🔔 Уведомления", "🌐 Язык", "🎯 Угадай число", "🎲 Случайное число"
        ])
    )
    async def private_message_stats(message: types.Message):
        user = message.from_user
        user_id = user.id

        user_data = {
            'id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        await db.add_or_update_user(user_data)

        await db.log_user_action(user_id, 'message_sent', f"Тип: {message.content_type}")

        await message.answer(
            "Выберите действие на клавиатуре ниже 👇",
            reply_markup=get_main_keyboard()
        )

    @dp.message(Command('broadcast'))
    async def broadcast_command(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        if user_id not in admin_ids:
            await message.answer("❌ Эта команда доступна только администраторам")
            return

        await message.answer(
            "📢 <b>Рассылка сообщений</b>\n\n"
            "Введите сообщение для рассылки всем пользователям:",
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(AdminState.waiting_for_broadcast_message)

    @dp.message(AdminState.waiting_for_broadcast_message)
    async def process_broadcast(message: types.Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id

        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Рассылка отменена", reply_markup=get_main_keyboard())
            return

        broadcast_text = message.text
        users = await db.get_all_users()

        success_count = 0
        fail_count = 0

        await message.answer(f"🔄 Начинаю рассылку для {len(users)} пользователей...")

        for user in users:
            try:
                await bot.send_message(
                    user[0],  # user_id
                    f"📢 <b>Важное сообщение от администрации:</b>\n\n{broadcast_text}",
                    parse_mode="HTML"
                )
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                fail_count += 1
                logger.error(f"Ошибка отправки пользователю {user[0]}: {e}")

        await message.answer(
            f"✅ Рассылка завершена!\n\n"
            f"✅ Успешно: {success_count}\n"
            f"❌ Не удалось: {fail_count}",
            reply_markup=get_main_keyboard()
        )
        await db.log_user_action(user_id, 'broadcast_sent', f"Успешно: {success_count}, Ошибок: {fail_count}")
        await state.clear()

    @dp.callback_query(F.data == "check_subscription")
    async def check_subscription_callback(callback: types.CallbackQuery, bot: Bot):
        await db.log_user_action(callback.from_user.id, 'check_subscription_callback')

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
        await db.log_user_action(callback.from_user.id, 'notifications_callback')

        action = callback.data.split("_")[1]
        if action == "on":
            await callback.answer("✅ Уведомления включены!", show_alert=False)
        else:
            await callback.answer("❌ Уведомления выключены!", show_alert=False)

    @dp.callback_query(F.data.startswith("lang_"))
    async def language_callback(callback: types.CallbackQuery):
        await db.log_user_action(callback.from_user.id, 'language_callback')

        lang = callback.data.split("_")[1]
        languages = {"ru": "Русский", "en": "English", "es": "Español"}
        await callback.answer(f"🌐 Язык изменен на {languages.get(lang, lang)}!", show_alert=False)

    @dp.message(Command('debug_db'))
    async def debug_db_command(message: types.Message):
        """Команда для отладки базы данных"""
        user_id = message.from_user.id

        user_data = {
            'id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
        await db.add_or_update_user(user_data)

        if user_id not in admin_ids:
            await message.answer("❌ Эта команда доступна только администраторам")
            return

        try:

            async with aiosqlite.connect('bot.db') as db_conn:
                cursor = await db_conn.execute("PRAGMA table_info(user_stats)")
                columns = await cursor.fetchall()

                debug_text = "📋 <b>Структура таблицы user_stats:</b>\n\n"
                for col in columns:
                    debug_text += f"• {col[1]} ({col[2]})\n"

                cursor = await db_conn.execute("SELECT * FROM user_stats LIMIT 5")
                users = await cursor.fetchall()

                debug_text += "\n👥 <b>Первые 5 пользователей:</b>\n\n"
                for user in users:
                    debug_text += f"ID: {user[0]}, Сообщений: {user[4]}, Имя: {user[2] or 'Нет'}\n"

                cursor = await db_conn.execute("SELECT COUNT(*) FROM user_stats")
                total_users = (await cursor.fetchone())[0]

                cursor = await db_conn.execute("SELECT SUM(messages_count) FROM user_stats")
                total_messages = (await cursor.fetchone())[0] or 0

                debug_text += f"\n📊 <b>Общая статистика:</b>\n"
                debug_text += f"• Всего пользователей: {total_users}\n"
                debug_text += f"• Всего сообщений: {total_messages}\n"

                await message.answer(debug_text, parse_mode="HTML")

        except Exception as e:
            await message.answer(f"❌ Ошибка отладки: {e}")
            logger.error(f"Ошибка отладки БД: {e}")
