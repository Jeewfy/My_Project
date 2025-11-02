import random
import re
from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from loguru import logger

group_games = {}


BAD_WORDS = [
    'мат1', 'мат2', 'мат3', 'плохоеслово', 'оскорбление'

]


def setup_group_handlers(dp: Dispatcher):

    @dp.message(F.chat.type.in_({"group", "supergroup"}) & ~F.text.startswith('/'))
    async def filter_bad_words(message: types.Message):

        text = message.text.lower() if message.text else ""

        found_bad_words = []
        for word in BAD_WORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                found_bad_words.append(word)

        if found_bad_words:

            try:
                await message.delete()
                logger.info(f"Удалено сообщение с матом в чате {message.chat.id}: {found_bad_words}")
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение: {e}")

            warning_msg = (
                f"⚠️ {message.from_user.first_name}, пожалуйста, не используйте ненормативную лексику!\n"
                f"Обнаружены запрещенные слова: {', '.join(found_bad_words)}"
            )
            await message.answer(warning_msg)

    @dp.message(Command('start_game'),
                F.chat.type.in_({"group", "supergroup"}))
    async def start_game(message: types.Message):
        chat_id = message.chat.id
        secret_number = random.randint(1, 100)
        group_games[chat_id] = secret_number

        game_announcement = (
            f"🎮 <b>ИГРА НАЧАЛАСЬ!</b> 🎮\n\n"
            f"👤 Запустил: {message.from_user.first_name}\n"
            f"🔢 Я загадал число от 1 до 100\n\n"
            f"💡 Чтобы угадать, напишите:\n"
            f"<code>/guess ваше_число</code>\n\n"
            f"🎯 Например: <code>/guess 42</code>\n"
            f"🏆 Кто первый угадает - тот победил!"
        )

        await message.answer(game_announcement, parse_mode="HTML")
        logger.info(f"Группа: игра начата в {chat_id}, загадано число {secret_number}")

    @dp.message(Command('guess'), F.chat.type.in_({"group", "supergroup"}))
    async def make_guess(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in group_games:

            await message.answer(
                "🎯 Игра не активна! Хотите начать?\n"
                "Напишите: /start_game"
            )
            return

        try:
            guess = int(message.text.split()[1])
        except (IndexError, ValueError):
            await message.answer(
                "❌ Неправильный формат!\n"
                "Используйте: /guess число\n"
                "Например: /guess 42"
            )
            return

        if guess < 1 or guess > 100:
            await message.answer("📏 Число должно быть от 1 до 100!")
            return

        secret = group_games[chat_id]
        user_name = message.from_user.first_name

        if guess < secret:
            await message.answer(f"🔺 {user_name}, мое число БОЛЬШЕ чем {guess}!")
        elif guess > secret:
            await message.answer(f"🔻 {user_name}, мое число МЕНЬШЕ чем {guess}!")
        else:
            victory_message = (
                f"🎉 <b>ПОБЕДА!</b> 🎉\n\n"
                f"🏆 {user_name} угадал число!\n"
                f"✅ Загаданное число: {secret}\n\n"
                f"🎮 Хотите сыграть еще?\n"
                f"Напишите: /start_game"
            )
            await message.answer(victory_message, parse_mode="HTML")
            del group_games[chat_id]
            logger.info(f"Группа: игра завершена в {chat_id}, победитель {user_name}")

    @dp.message(Command('game_status'), F.chat.type.in_({"group", "supergroup"}))
    async def game_status(message: types.Message):
        chat_id = message.chat.id
        if chat_id in group_games:
            await message.answer(
                "🎮 Игра активна!\n"
                "🔢 Число загадано, угадывайте!\n\n"
                "💡 Используйте: /guess число"
            )
        else:
            await message.answer(
                "🤷 Игра не активна\n"
                "🎯 Чтобы начать: /start_game"
            )

    @dp.message(Command('badwords'), F.chat.type.in_({"group", "supergroup"}))
    async def show_bad_words(message: types.Message):
        await message.answer(
            f"📋 Список запрещенных слов:\n" +
            "\n".join([f"• {word}" for word in BAD_WORDS]) +
            "\n\n❌ Использование этих слов приведет к удалению сообщения!"
        )
