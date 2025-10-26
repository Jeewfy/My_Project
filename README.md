# ⚽ SPORTS_BOT - Многофункциональный Telegram бот для спортивных новостей

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://docs.aiogram.dev/)

Многофункциональный Telegram бот с автоматическими спортивными новостями, системой модерации чатов, мини-играми и аналитикой.

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.8 или новее
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)

### Установка и запуск


# Клонирование репозитория
git clone https://github.com/yourusername/sports-bot.git
cd sports-bot

# Создание виртуального окружения
python -m venv venv

# Активация окружения
# Windows:
.\venv\Scripts\activate
# Linux/MacOS:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка конфигурации
cp .env.example .env

# Запуск бота
python main.py
## ⚙️ Конфигурация

Создайте файл `.env` в корне проекта:

TOKEN=your_telegram_bot_token_here
CHANNEL_ID=@your_channel_username
ADMIN_IDS=123456789,987654321

| Переменная | Описание | Обязательная |
|------------|-----------|--------------|
| `TOKEN` | Токен бота от BotFather | ✅ |
| `CHANNEL_ID` | ID канала для новостей | ✅ |
| `ADMIN_IDS` | ID администраторов через запятую | ❌ |

## 🏗️ Структура проекта
sports-bot/
├── main.py              # Основной файл запуска
├── database.py          # Модели и работа с SQLite
├── private_chat.py      # Обработчики личных сообщений
├── group.py            # Функции для групповых чатов
├── channel.py          # Работа с каналами и RSS
├── keyboards.py        # Генерация клавиатур
└── requirements.txt    # Зависимости Python


## 🎮 Основные возможности

### 📰 Автоматические новости
- RSS парсинг с Sports.ru
- Автопубликация в канал каждые 5 минут
- Умная фильтрация контента

### 🛡️ Модерация чатов
- Фильтр запрещенных слов
- Автоматическое удаление сообщений
- Система предупреждений

### 🎯 Мини-игры
- "Угадай число" в личных и групповых чатах
- Система рекордов и статистики

### 📊 Аналитика
- Статистика пользователей
- Мониторинг активности
- Админ-панель с метриками

## 👨‍💻 Команды

### Для пользователей
- `/start` - Начать работу
- `/help` - Справка по командам  
- `/support` - Обратная связь
- `/guess <число>` - Игра "Угадай число"

### Для администраторов
- `/bot_stats` - Статистика бота
- `/users` - Список пользователей
- `/broadcast` - Рассылка сообщений
- `/db_backup` - Резервная копия БД

## 🔧 Разработка


# Установка для разработки
git clone https://github.com/yourusername/sports-bot.git
cd sports-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt