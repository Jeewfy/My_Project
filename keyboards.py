from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Обратная связь")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="📢 Канал")],
            [KeyboardButton(text="🎮 Игры"), KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def get_games_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Угадай число"), KeyboardButton(text="🎲 Случайное число")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )


def get_channel_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")]
        ]
    )


def get_feedback_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📞 Связаться с поддержкой", url="https://t.me/username")],
            [InlineKeyboardButton(text="⭐ Оценить бота", callback_data="rate_bot")]
        ]
    )


def get_settings_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔔 Уведомления"), KeyboardButton(text="🌐 Язык")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def get_notifications_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Включить уведомления", callback_data="notifications_on")],
            [InlineKeyboardButton(text="❌ Выключить уведомления", callback_data="notifications_off")]
        ]
    )


def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")]
        ]
    )


CHANNEL_ID = os.getenv('CHANNEL_ID')