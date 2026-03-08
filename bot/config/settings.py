# bot/config/settings.py
from dotenv import load_dotenv
import os
import json
from typing import Dict, List, Any
from pathlib import Path

# Находим корневую директорию проекта
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / '.env'

# Загружаем переменные окружения
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Файл .env загружен из: {env_path}")
else:
    print(f"⚠️ Файл .env не найден по пути: {env_path}")

class Config:
    """Класс конфигурации"""

    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # Администраторы
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]

    # Google Sheets
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

    # Настройки кэша
    CACHE_UPDATE_INTERVAL = int(os.getenv('CACHE_UPDATE_INTERVAL', 300))

    # Пути к файлам
    BASE_DIR = Path(__file__).parent.parent.parent
    CATEGORIES_FILE = BASE_DIR / 'categories.json'
    CATEGORIES_BACKUP_FILE = BASE_DIR / 'categories_backup.json'

    # Категории (будут загружены из файла)
    CATEGORIES: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        """Инициализация конфигурации"""
        self.load_categories()

    def load_categories(self) -> None:
        """Загрузить категории из JSON файла"""
        try:
            if self.CATEGORIES_FILE.exists():
                with open(self.CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                    self.CATEGORIES = json.load(f)
                print(f"✅ Категории загружены из: {self.CATEGORIES_FILE}")
            else:
                print(f"⚠️ Файл категорий не найден: {self.CATEGORIES_FILE}")
                self.CATEGORIES = {}
        except Exception as e:
            print(f"❌ Ошибка загрузки категорий: {e}")
            self.CATEGORIES = {}

    def save_categories(self) -> bool:
        """Сохранить категории в JSON файл"""
        try:
            # Сортируем категории по order перед сохранением
            sorted_categories = dict(sorted(
                self.CATEGORIES.items(),
                key=lambda x: x[1].get('order', 999)
            ))

            # Сохраняем в основной файл
            with open(self.CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(sorted_categories, f, ensure_ascii=False, indent=2)

            # Создаем резервную копию
            with open(self.CATEGORIES_BACKUP_FILE, 'w', encoding='utf-8') as f:
                json.dump(sorted_categories, f, ensure_ascii=False, indent=2)

            print(f"✅ Категории сохранены в: {self.CATEGORIES_FILE}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения категорий: {e}")
            return False

    def get_sorted_categories(self) -> List[tuple]:
        """Получить отсортированный список категорий"""
        return sorted(
            self.CATEGORIES.items(),
            key=lambda x: x[1].get('order', 999)
        )

    def get_sorted_subcategories(self, category_id: str) -> List[tuple]:
        """Получить отсортированный список подкатегорий"""
        category = self.CATEGORIES.get(category_id, {})
        subcategories = category.get('subcategories', {})
        return sorted(
            subcategories.items(),
            key=lambda x: x[1].get('order', 999)
        )

    def move_category(self, category_id: str, direction: str) -> bool:
        """Изменить порядок категории (up/down)"""
        sorted_cats = self.get_sorted_categories()

        # Находим индекс категории
        index = None
        for i, (cat_id, _) in enumerate(sorted_cats):
            if cat_id == category_id:
                index = i
                break

        if index is None:
            return False

        # Определяем новый индекс
        if direction == 'up' and index > 0:
            new_index = index - 1
        elif direction == 'down' and index < len(sorted_cats) - 1:
            new_index = index + 1
        else:
            return False

        # Меняем местами значения order
        current_order = self.CATEGORIES[category_id].get('order', index + 1)
        target_id, target_data = sorted_cats[new_index]
        target_order = target_data.get('order', new_index + 1)

        self.CATEGORIES[category_id]['order'] = target_order
        self.CATEGORIES[target_id]['order'] = current_order

        return True

    def move_subcategory(self, category_id: str, subcategory_id: str, direction: str) -> bool:
        """Изменить порядок подкатегории (up/down)"""
        category = self.CATEGORIES.get(category_id, {})
        subcategories = category.get('subcategories', {})

        sorted_subs = sorted(
            subcategories.items(),
            key=lambda x: x[1].get('order', 999)
        )

        # Находим индекс подкатегории
        index = None
        for i, (sub_id, _) in enumerate(sorted_subs):
            if sub_id == subcategory_id:
                index = i
                break

        if index is None:
            return False

        # Определяем новый индекс
        if direction == 'up' and index > 0:
            new_index = index - 1
        elif direction == 'down' and index < len(sorted_subs) - 1:
            new_index = index + 1
        else:
            return False

        # Меняем местами значения order
        current_order = subcategories[subcategory_id].get('order', index + 1)
        target_id, target_data = sorted_subs[new_index]
        target_order = target_data.get('order', new_index + 1)

        subcategories[subcategory_id]['order'] = target_order
        subcategories[target_id]['order'] = current_order

        return True

    def get_all_sheet_names(self) -> List[str]:
        """Получить все названия листов"""
        sheets = []
        for category in self.CATEGORIES.values():
            if category.get("is_direct"):
                if "sheet_name" in category:
                    sheets.append(category["sheet_name"])
            else:
                for sub in category.get("subcategories", {}).values():
                    if "sheet_name" in sub:
                        sheets.append(sub["sheet_name"])
        return sheets

    def is_admin(self, user_id: int) -> bool:
        """Проверка администратора"""
        return user_id in self.ADMIN_IDS

    @classmethod
    def validate(cls):
        """Проверка конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        if not cls.SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID не установлен")
        if cls.SERVICE_ACCOUNT_FILE and not os.path.exists(cls.SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Файл с ключами не найден: {cls.SERVICE_ACCOUNT_FILE}")

# Создаем экземпляр конфигурации
config = Config()