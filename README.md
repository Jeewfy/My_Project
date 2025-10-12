Документация к Sports Bot
📋 Оглавление
Общее описание

Архитектура проекта

Установка и запуск

Конфигурация

Функциональность

База данных

FSM состояния

Команды

Логирование

🚀 Общее описание
Sports Bot - многофункциональный Telegram бот для спортивной тематики с функциями:

📢 Автоматическая публикация спортивных новостей в канал

💬 Умные диалоги с пользователями (FSM)

🎮 Мини-игры для развлечения

⚽ Модерация групповых чатов

📊 Статистика и аналитика

👥 Управление пользователями

🏗️ Архитектура проекта
text
sports_bot/
├── main.py              # Главный файл запуска
├── database.py          # Работа с базой данных
├── private_chat.py      # Обработчики личных сообщений
├── group.py            # Обработчики групповых чатов
├── channel.py          # Обработчики канала
├── keyboards.py        # Клавиатуры и кнопки
├── requirements.txt    # Зависимости
├── .env               # Конфигурация
├── bot.db            # База данных SQLite
├── last_entries.pkl  # Кэш RSS новостей
└── bot.log           # Логи приложения
⚙️ Установка и запуск
1. Предварительные требования
Python 3.8+

Telegram бот токен

Telegram канал (для RSS новостей)

2. Установка зависимостей
bash
# Клонирование репозитория (если есть)
git clone <repository-url>
cd sports_bot

# Установка зависимостей
pip install -r requirements.txt
3. Настройка конфигурации
Создайте файл .env в корне проекта:

env
TOKEN=your_telegram_bot_token_here
CHANNEL_ID=@your_channel_username
ADMIN_IDS=123456789,987654321
4. Запуск бота
bash
# Основной запуск
python main.py

# Запуск в фоне (Linux/Mac)
nohup python main.py &

# Запуск с виртуальным окружением
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
🔧 Конфигурация
Переменные окружения (.env)
Переменная	Описание	Пример
TOKEN	Токен бота от @BotFather	123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHANNEL_ID	ID канала для новостей	@sports_news
ADMIN_IDS	ID администраторов через запятую	123456789,987654321
Получение Telegram ID
python
# Временный скрипт для получения ID
import asyncio
from aiogram import Bot

async def get_id():
    bot = Bot(token="YOUR_TOKEN")
    me = await bot.get_me()
    print(f"Bot ID: {me.id}")
    # Напишите боту сообщение и проверьте логи

asyncio.run(get_id())
🎯 Функциональность
📍 Личные сообщения
Главное меню с интерактивными кнопками

Статистика пользователей и бота

Обратная связь с админами

Мини-игры (угадай число, случайное число)

Настройки языка и уведомлений

👥 Групповые чаты
Автомодерация - фильтр запрещенных слов

Игры - угадай число для группы

Статус игр - отслеживание активных игр

📢 Канал
RSS новости - автоматическая публикация

Ежедневные обновления - спортивные события

🗃️ База данных
Структура таблиц
sql
-- Пользователи и статистика
CREATE TABLE user_stats (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    messages_count INTEGER DEFAULT 0,
    warnings_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Обратная связь
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
);

-- Действия пользователей
CREATE TABLE user_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
);
Команды для работы с БД
bash
# Просмотр БД через SQLite
sqlite3 bot.db

.tables                    # Показать таблицы
.schema user_stats         # Структура таблицы
SELECT * FROM user_stats;  # Данные пользователей
🔄 FSM состояния
Определенные состояния
python
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
Пример использования FSM
python
@dp.message(F.text == "🎯 Угадай число")
async def start_number_game(message: types.Message, state: FSMContext):
    # Установка состояния
    await state.set_state(GameState.playing_number_game)
    await state.update_data(secret_number=42, attempts=0)

@dp.message(GameState.playing_number_game)
async def process_guess(message: types.Message, state: FSMContext):
    # Обработка только в состоянии игры
    data = await state.get_data()
    # ... логика игры
⌨️ Команды
Пользовательские команды
Команда	Описание	Доступ
/start	Начало работы с ботом	Все
/help	Справка по командам	Все
/support	Связь с поддержкой	Все
/guess <число>	Угадать число	Все
/game_status	Статус игры в группе	Группы
Админские команды
Команда	Описание	Доступ
/users	Список пользователей	Админы
/broadcast	Рассылка сообщений	Админы
/bot_stats	Статистика бота	Админы
/debug_db	Отладка базы данных	Админы
/user_info <id>	Инфо о пользователе	Админы
/restart_rss	Перезапуск RSS	Админы
/db_backup	Резервная копия БД	Админы
📊 Логирование
Уровни логирования
INFO - основная информация

SUCCESS - успешные операции

WARNING - предупреждения

ERROR - ошибки

CRITICAL - критические ошибки

Просмотр логов
bash
# Реальный мониторинг
tail -f bot.log

# Поиск ошибок
grep "ERROR" bot.log

# Статистика логов
grep -c "INFO" bot.log
Пример логов
text
2025-01-15 10:30:45 | INFO | Бот запускается...
2025-01-15 10:30:46 | SUCCESS | Бот @sports_bot успешно запущен!
2025-01-15 10:31:02 | INFO | Пользователь 123456789 начал чат
2025-01-15 10:31:05 | INFO | Новость отправлена: Футбольные новости
🛠️ Разработка и отладка
Добавление новых функций
Добавьте обработчик в соответствующий файл

При необходимости создайте FSM состояние

Обновите клавиатуры в keyboards.py

Протестируйте функциональность

Отладка проблем
python
# Временная команда для отладки
@dp.message(Command('debug'))
async def debug_command(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Debug info:\nUser ID: {user_id}\nState: {await state.get_state()}")
Мониторинг производительности
bash
# Использование памяти
ps aux | grep python

# Логи в реальном времени
tail -f bot.log | grep -E "(ERROR|CRITICAL)"

# Проверка базы данных
sqlite3 bot.db "SELECT COUNT(*) FROM user_stats;"
🔄 RSS функционал
Настройка RSS
python
# В main.py - настройка источника новостей
RSS_FEED_URL = "https://www.sports.ru/rss/all_news.xml"
CHECK_INTERVAL = 300  # 5 минут
Добавление новых RSS источников
python
# В функции fetch_news() в main.py
feeds = [
    "https://www.sports.ru/rss/all_news.xml",
    "https://example.com/another-feed.xml"
]
📱 Клавиатуры и интерфейс
Основные клавиатуры
get_main_keyboard() - главное меню

get_games_keyboard() - игры

get_settings_keyboard() - настройки

get_back_keyboard() - кнопка назад

Инлайн клавиатуры
get_channel_inline_keyboard() - подписка на канал

get_feedback_inline_keyboard() - обратная связь

get_notifications_keyboard() - уведомления

get_language_keyboard() - выбор языка

🚀 Деплой
На VPS (Ubuntu)
bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip python3-venv -y

# Копирование проекта
scp -r sports_bot/ user@server:/home/user/

# Настройка сервиса
sudo nano /etc/systemd/system/sports-bot.service
systemd сервис
ini
[Unit]
Description=Sports Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sports_bot
Environment=PATH=/home/ubuntu/sports_bot/venv/bin
ExecStart=/home/ubuntu/sports_bot/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
bash
sudo systemctl daemon-reload
sudo systemctl enable sports-bot
sudo systemctl start sports-bot
sudo systemctl status sports-bot
📞 Поддержка
Полезные команды для админов
bash
# Перезапуск бота
sudo systemctl restart sports-bot

# Просмотр логов
sudo journalctl -u sports-bot -f

# Проверка состояния
sudo systemctl status sports-bot

# Резервное копирование БД
cp bot.db backup_$(date +%Y%m%d_%H%M%S).db
Мониторинг ресурсов
bash
# Память и CPU
htop

# Дисковое пространство
df -h

# Сетевые соединения
netstat -tulpn
