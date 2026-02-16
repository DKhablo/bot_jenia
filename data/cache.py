# data/cache.py
import asyncio
import logging
from typing import Dict, List, Tuple, Optional

from services import sheets_reader
from bot.config import config  # ИЗМЕНЕНО

logger = logging.getLogger(__name__)

class DataCache:
    """Класс для кэширования данных"""
    
    def __init__(self):
        self._cache: Dict[str, List[Tuple[str, str]]] = {
            "iphones": [],
            "macbooks": []
        }
        self._update_task: Optional[asyncio.Task] = None
    
    @property
    def iphones(self) -> List[Tuple[str, str]]:
        """Получить список iPhone"""
        return self._cache.get("iphones", [])
    
    @property
    def macbooks(self) -> List[Tuple[str, str]]:
        """Получить список MacBook"""
        return self._cache.get("macbooks", [])
    
    async def update(self) -> None:
        """Обновление кэша"""
        if not sheets_reader or not sheets_reader.is_connected():
            logger.error("❌ Google Sheets не доступен")
            return
        
        try:
            iphones = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, config.SHEET_IPHONE)
            macbooks = sheets_reader.get_sheet_data(config.SPREADSHEET_ID, config.SHEET_MACBOOK)
            
            self._cache["iphones"] = iphones
            self._cache["macbooks"] = macbooks
            
            logger.info(f"✅ Кэш обновлен: iPhone ({len(iphones)}), MacBook ({len(macbooks)})")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления кэша: {e}")
    
    async def start_auto_update(self) -> None:
        """Запуск автоматического обновления кэша"""
        if self._update_task:
            return
        
        async def updater():
            while True:
                await self.update()
                await asyncio.sleep(config.CACHE_UPDATE_INTERVAL)
        
        self._update_task = asyncio.create_task(updater())
        logger.info(f"🔄 Автообновление кэша запущено (интервал: {config.CACHE_UPDATE_INTERVAL}с)")
    
    async def stop_auto_update(self) -> None:
        """Остановка автоматического обновления кэша"""
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
            logger.info("⏹ Автообновление кэша остановлено")

# Создаем глобальный экземпляр кэша
cache = DataCache()