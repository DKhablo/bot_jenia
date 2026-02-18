import logging
from typing import Dict, List, Tuple
from .database import Database
from services import sheets_reader
from bot.config import config

logger = logging.getLogger(__name__)

class DataCache:
    """Класс для работы с данными (теперь через БД)"""
    
    def __init__(self):
        self.db = Database()
    
    def get_category(self, key: str) -> List[Tuple[str, str]]:
        """Получить данные категории из БД"""
        return self.db.get_products(key)
    
    async def update_all(self) -> None:
        """Обновление всех данных (вызывается по кнопке)"""
        if not sheets_reader or not sheets_reader.is_connected():
            logger.error("❌ Google Sheets не доступен")
            return
        
        logger.info("🔄 Начало обновления всех категорий...")
        
        # Обновляем прямые категории
        for cat_key, category in config.CATEGORIES.items():
            if category.get("is_direct"):
                sheet_name = category["sheet_name"]
                data = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, sheet_name)
                self.db.save_products(cat_key, category["name"], data)
                logger.info(f"✅ {category['name']}: {len(data)} товаров")
        
        # Обновляем подкатегории
        for category in config.CATEGORIES.values():
            if not category.get("is_direct") and "subcategories" in category:
                for sub_key, subcategory in category["subcategories"].items():
                    sheet_name = subcategory["sheet_name"]
                    data = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, sheet_name)
                    self.db.save_products(sub_key, subcategory["name"], data)
                    logger.info(f"✅ {subcategory['name']}: {len(data)} товаров")
        
        logger.info("✅ Обновление всех категорий завершено")
    
    def get_stats(self) -> Dict[str, int]:
        """Получить статистику из БД"""
        return self.db.get_stats()
    
    # Удаляем методы auto_update - они больше не нужны!

cache = DataCache()