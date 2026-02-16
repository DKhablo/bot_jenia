# data/cache.py
import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any

from services import sheets_reader
from bot.config import config

logger = logging.getLogger(__name__)

class DataCache:
    """Класс для кэширования данных"""
    
    def __init__(self):
        # Динамически создаем кэш на основе конфигурации
        self._cache: Dict[str, List[Tuple[str, str]]] = {}
        self._last_update: Dict[str, float] = {}
        self._update_task: Optional[asyncio.Task] = None
        
        # Инициализируем кэш для всех листов
        for key in config.SHEETS_CONFIG.keys():
            self._cache[key] = []
    
    def __getattr__(self, name: str) -> List[Tuple[str, str]]:
        """Динамический доступ к свойствам (cache.iphones, cache.ipads, etc)"""
        if name in self._cache:
            return self._cache[name]
        raise AttributeError(f"'DataCache' object has no attribute '{name}'")
    
    def get_all_categories(self) -> Dict[str, List[Tuple[str, str]]]:
        """Получить все категории"""
        return self._cache.copy()
    
    def get_category(self, key: str) -> List[Tuple[str, str]]:
        """Получить данные конкретной категории"""
        return self._cache.get(key, [])
    
    async def update_category(self, key: str) -> None:
        """Обновить данные конкретной категории"""
        if not sheets_reader or not sheets_reader.is_connected():
            logger.error("❌ Google Sheets не доступен")
            return
        
        sheet_config = config.get_sheet_config(key)
        if not sheet_config:
            logger.error(f"❌ Нет конфигурации для ключа: {key}")
            return
        
        try:
            sheet_name = sheet_config["sheet_name"]
            data = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, sheet_name)
            self._cache[key] = data
            logger.info(f"✅ Обновлен кэш для {key}: {len(data)} записей")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления кэша для {key}: {e}")
    
    async def update_all(self) -> None:
        """Обновить все категории"""
        if not sheets_reader or not sheets_reader.is_connected():
            logger.error("❌ Google Sheets не доступен")
            return
        
        logger.info("🔄 Начало обновления всех категорий...")
        for key in config.SHEETS_CONFIG.keys():
            await self.update_category(key)
            await asyncio.sleep(1)  # Небольшая задержка между запросами
        logger.info("✅ Обновление всех категорий завершено")
    
    async def update(self) -> None:
        """Для обратной совместимости - обновляет все"""
        await self.update_all()
    
    async def start_auto_update(self) -> None:
        """Запуск автоматического обновления кэша"""
        if self._update_task:
            return
        
        async def updater():
            while True:
                await self.update_all()
                await asyncio.sleep(config.CACHE_UPDATE_INTERVAL)
        
        self._update_task = asyncio.create_task(updater())
        logger.info(f"🔄 Автообновление кэша запущено (интервал: {config.CACHE_UPDATE_INTERVAL}с)")
    
    async def stop_auto_update(self) -> None:
        """Остановка автоматического обновления кэша"""
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
            logger.info("⏹ Автообновление кэша остановлено")
    
    def get_stats(self) -> Dict[str, int]:
        """Получить статистику кэша"""
        return {key: len(data) for key, data in self._cache.items()}

cache = DataCache()