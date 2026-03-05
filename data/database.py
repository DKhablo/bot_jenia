import sqlite3
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с SQLite"""

    def __init__(self, db_path='data/bot_database.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица для товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_key TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    price TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Индекс для быстрого поиска
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_category
                ON products(category_key)
            ''')

            # Таблица для метаданных (время последнего обновления)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

        logger.info("✅ База данных инициализирована")

    def save_products(self, category_key: str, category_name: str, products: List[Tuple[str, str]]):
        """Сохранить товары категории"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Удаляем старые записи
            cursor.execute('DELETE FROM products WHERE category_key = ?', (category_key,))

            # Добавляем новые
            for model, price in products:
                cursor.execute('''
                    INSERT INTO products (category_key, category_name, model, price)
                    VALUES (?, ?, ?, ?)
                ''', (category_key, category_name, model, price))

            # Обновляем время последнего обновления
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES (?, ?)
            ''', (f'last_update_{category_key}', datetime.now().isoformat()))

            conn.commit()

        logger.info(f"💾 Сохранено {len(products)} товаров в {category_key}")

    def get_products(self, category_key: str) -> List[Tuple[str, str]]:
        """Получить товары категории"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT model, price FROM products
                WHERE category_key = ?
                ORDER BY id
            ''', (category_key,))

            return cursor.fetchall()

    def get_all_products(self) -> Dict[str, List[Tuple[str, str]]]:
        """Получить все товары"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT category_key, model, price FROM products ORDER BY category_key, id')

            result = {}
            for category_key, model, price in cursor.fetchall():
                if category_key not in result:
                    result[category_key] = []
                result[category_key].append((model, price))

            return result

    def get_stats(self) -> Dict[str, int]:
        """Получить статистику"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category_key, category_name, COUNT(*)
                FROM products
                GROUP BY category_key, category_name
            ''')

            stats = {}
            for category_key, category_name, count in cursor.fetchall():
                stats[category_key] = count

            return stats

    def get_last_update(self, category_key: str) -> Optional[str]:
        """Время последнего обновления категории"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT value FROM metadata
                WHERE key = ?
            ''', (f'last_update_{category_key}',))

            result = cursor.fetchone()
            return result[0] if result else None

    def clear_all(self):
        """Очистить все данные (для отладки)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products')
            cursor.execute('DELETE FROM metadata')
            conn.commit()
        logger.info("🗑 База данных очищена")