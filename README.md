# ⚽ SPORTS_BOT Project: Революция в спортивных новостях и сообществах

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Многофункциональный Telegram бот с автоматическими спортивными новостями, системой модерации, мини-играми и аналитикой.

## 🌟 Особенности

### 🤖 Основные возможности
- **📰 Автоматические новости** - RSS парсинг с Sports.ru
- **👥 Модерация чатов** - Фильтр запрещенных слов и управление
- **🎮 Мини-игры** - "Угадай число" в личных и групповых чатах
- **📊 Аналитика** - Подробная статистика пользователей и бота
- **📝 Обратная связь** - Система сбора отзывов и поддержки

### 🛡 Администраторские функции
- Панель управления с метриками
- Массовые рассылки
- Резервное копирование БД
- Мониторинг системных ресурсов

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.8 или новее
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)

### Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/yourusername/sports-bot.git
cd sports-bot
Создайте виртуальное окружение

bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
Установите зависимости

bash
pip install -r requirements.txt
Настройте конфигурацию

bash
cp .env.example .env
# Отредактируйте .env файл
Запустите бота

bash
python main.py
⚙️ Конфигурация
Переменные окружения
Создайте файл .env со следующими параметрами:

env
TOKEN=your_telegram_bot_token_here
CHANNEL_ID=@your_channel_username
ADMIN_IDS=123456789,987654321
Переменная	Описание	Обязательная
TOKEN	Токен бота от BotFather	✅
CHANNEL_ID	ID канала для новостей	✅
ADMIN_IDS	ID администраторов	❌
📁 Структура проекта
text
sports-bot/
├── main.py                 # Точка входа
├── database.py            # Работа с БД
├── private_chat.py        # Личные сообщения
├── group.py               # Групповые чаты
├── channel.py             # Каналы и RSS
├── keyboards.py           # Клавиатуры
├── requirements.txt       # Зависимости
└── README.md             # Документация
🎮 Команды
Для пользователей
Команда	Описание
/start	Начать работу
/help	Справка по командам
/support	Поддержка
/guess <число>	Игра "Угадай число"
Для администраторов
Команда	Описание
/bot_stats	Статистика бота
/users	Список пользователей
/broadcast	Рассылка сообщений
🔧 Разработка
Установка для разработки
bash
git clone https://github.com/yourusername/sports-bot.git
cd sports-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt