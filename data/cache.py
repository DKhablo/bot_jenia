# data/cache.py
import asyncio
import logging
from typing import Dict, List, Tuple, Optional

from services import sheets_reader
from bot.config import config

logger = logging.getLogger(__name__)

class DataCache:
    """Класс для кэширования данных"""
    
    def __init__(self):
        self._cache: Dict[str, List[Tuple[str, str]]] = {}
        self._update_task: Optional[asyncio.Task] = None
        
        # Инициализируем кэш для всех категорий
        self._init_cache()
    
    def _init_cache(self):
        """Инициализация структуры кэша"""
        # Для прямых категорий
        for cat_key, category in config.CATEGORIES.items():
            if category.get("is_direct"):
                self._cache[cat_key] = []
        
        # Для подкатегорий
        for category in config.CATEGORIES.values():
            if not category.get("is_direct") and "subcategories" in category:
                for sub_key in category["subcategories"].keys():
                    self._cache[sub_key] = []
    
    def get_category(self, key: str) -> List[Tuple[str, str]]:
        """Получить данные категории"""
        return self._cache.get(key, [])
    
    async def update_all(self) -> None:
        """Обновление всех данных"""
        if not sheets_reader or not sheets_reader.is_connected():
            logger.error("❌ Google Sheets не доступен")
            return
        
        logger.info("🔄 Начало обновления всех категорий...")
        
        # Обновляем прямые категории
        for cat_key, category in config.CATEGORIES.items():
            if category.get("is_direct"):
                sheet_name = category["sheet_name"]
                data = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, sheet_name)
                self._cache[cat_key] = data
                logger.info(f"✅ {category['name']}: {len(data)} товаров")
                await asyncio.sleep(0.5)
        
        # Обновляем подкатегории
        for category in config.CATEGORIES.values():
            if not category.get("is_direct") and "subcategories" in category:
                for sub_key, subcategory in category["subcategories"].items():
                    sheet_name = subcategory["sheet_name"]
                    data = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, sheet_name)
                    self._cache[sub_key] = data
                    logger.info(f"✅ {subcategory['name']}: {len(data)} товаров")
                    await asyncio.sleep(0.5)
        
        logger.info("✅ Обновление всех категорий завершено")
    
    def get_stats(self) -> Dict[str, int]:
        """Получить статистику"""
        stats = {}
        
        # Прямые категории
        for cat_key, category in config.CATEGORIES.items():
            if category.get("is_direct"):
                stats[cat_key] = len(self._cache.get(cat_key, []))
        
        # Подкатегории
        for category in config.CATEGORIES.values():
            if not category.get("is_direct") and "subcategories" in category:
                for sub_key in category["subcategories"].keys():
                    stats[sub_key] = len(self._cache.get(sub_key, []))
        
        return stats
    
    async def start_auto_update(self) -> None:
        """Запуск автообновления"""
        if self._update_task:
            return
        
        async def updater():
            while True:
                await asyncio.sleep(config.CACHE_UPDATE_INTERVAL)
                await self.update_all()
        
        self._update_task = asyncio.create_task(updater())
        logger.info(f"🔄 Автообновление запущено (интервал: {config.CACHE_UPDATE_INTERVAL}с)")
    
    async def stop_auto_update(self) -> None:
        """Остановка автообновления"""
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
            logger.info("⏹ Автообновление остановлено")

cache = DataCache()