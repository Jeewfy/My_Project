import aiosqlite
import asyncio
from datetime import datetime
from loguru import logger

class Database:
    def __init__(self, db_path='bot.db'):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Удаляем старые таблицы если они есть (для чистоты)
            await db.execute('DROP TABLE IF EXISTS user_stats')
            await db.execute('DROP TABLE IF EXISTS feedback')
            await db.execute('DROP TABLE IF EXISTS user_actions')
            
            # Таблица для статистики пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    messages_count INTEGER DEFAULT 0,
                    warnings_count INTEGER DEFAULT 0,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для обратной связи
            await db.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                )
            ''')
            
            # Таблица для действий пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                )
            ''')
            
            await db.commit()
        logger.info("База данных инициализирована")

    async def add_or_update_user(self, user: dict):
        """Добавление или обновление пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Сначала проверяем существующего пользователя
            cursor = await db.execute(
                'SELECT messages_count FROM user_stats WHERE user_id = ?',
                (user['id'],)
            )
            existing_user = await cursor.fetchone()
            
            if existing_user:
                # Обновляем существующего пользователя
                current_count = existing_user[0]
                await db.execute('''
                    UPDATE user_stats 
                    SET username = ?, first_name = ?, last_name = ?, 
                        messages_count = ?, last_seen = ?
                    WHERE user_id = ?
                ''', (
                    user.get('username'),
                    user.get('first_name'),
                    user.get('last_name'),
                    current_count + 1,
                    datetime.now(),
                    user['id']
                ))
            else:
                # Добавляем нового пользователя
                await db.execute('''
                    INSERT INTO user_stats 
                    (user_id, username, first_name, last_name, messages_count, last_seen)
                    VALUES (?, ?, ?, ?, 1, ?)
                ''', (
                    user['id'],
                    user.get('username'),
                    user.get('first_name'),
                    user.get('last_name'),
                    datetime.now()
                ))
            
            await db.commit()

    async def increment_messages_count(self, user_id: int):
        """Увеличение счетчика сообщений пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE user_stats 
                SET messages_count = messages_count + 1, last_seen = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            await db.commit()

    async def add_feedback(self, user_id: int, message: str):
        """Добавление обратной связи"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO feedback (user_id, message) 
                VALUES (?, ?)
            ''', (user_id, message))
            await db.commit()

    async def log_user_action(self, user_id: int, action_type: str, details: str = None):
        """Логирование действий пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO user_actions (user_id, action_type, details) 
                VALUES (?, ?, ?)
            ''', (user_id, action_type, details))
            await db.commit()

    async def get_user_stats(self, user_id: int):
        """Получение статистики пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT * FROM user_stats WHERE user_id = ?
            ''', (user_id,))
            user_data = await cursor.fetchone()
            return user_data

    async def get_all_users(self):
        """Получение списка всех пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT user_id, username, first_name, last_name, messages_count, first_seen, last_seen
                FROM user_stats 
                ORDER BY last_seen DESC
            ''')
            users = await cursor.fetchall()
            return users

    async def get_total_stats(self):
        """Получение общей статистики"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM user_stats')
            total_users = (await cursor.fetchone())[0]
            
            cursor = await db.execute('SELECT SUM(messages_count) FROM user_stats')
            total_messages = (await cursor.fetchone())[0] or 0
            
            cursor = await db.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'total_messages': total_messages,
                'total_feedback': total_feedback
            }

# Глобальный экземпляр базы данных
db = Database()