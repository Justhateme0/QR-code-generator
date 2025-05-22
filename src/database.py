import sqlite3
from typing import Optional
from src.config import DATABASE_URL

class Database:
    def __init__(self):
        self.db_path = DATABASE_URL.replace('sqlite:///', '')
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'ru',
                    qr_style TEXT DEFAULT 'classic'
                )
            ''')
            conn.commit()

    def get_user_language(self, user_id: int) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 'ru'

    def set_user_language(self, user_id: int, language: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, language) 
                VALUES (?, ?)
                ON CONFLICT(user_id) 
                DO UPDATE SET language = ?
            ''', (user_id, language, language))
            conn.commit()

    def get_user_style(self, user_id: int) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT qr_style FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 'classic'

    def set_user_style(self, user_id: int, style: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, qr_style) 
                VALUES (?, ?)
                ON CONFLICT(user_id) 
                DO UPDATE SET qr_style = ?
            ''', (user_id, style, style))
            conn.commit() 