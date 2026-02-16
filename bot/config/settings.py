# bot/config/settings.py
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional

env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

class Config:
    """Класс конфигурации"""
    
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Google Sheets
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
    
    # Настройки кэша
    CACHE_UPDATE_INTERVAL = int(os.getenv('CACHE_UPDATE_INTERVAL', 300))
    
    # Словарь с настройками листов
    SHEETS_CONFIG: Dict[str, Dict[str, str]] = {
        "iphones": {
            "sheet_name": "айфоны",
            "display_name": "iPhone",
            "emoji": "📱",
            "callback": "show_iphones"
        },
        "macbooks": {
            "sheet_name": "макбуки",
            "display_name": "MacBook",
            "emoji": "💻",
            "callback": "show_macbooks"
        },
        # Добавляйте новые листы здесь
        "ipads": {
            "sheet_name": "айпады",
            "display_name": "iPad",
            "emoji": "📱",
            "callback": "show_ipads"
        },
        "airpods": {
            "sheet_name": "эйрподсы",
            "display_name": "AirPods",
            "emoji": "🎧",
            "callback": "show_airpods"
        },
        "watch": {
            "sheet_name": "часы",
            "display_name": "Apple Watch",
            "emoji": "⌚️",
            "callback": "show_watch"
        }
    }
    
    @property
    def sheet_names(self) -> List[str]:
        """Получить список названий листов"""
        return [cfg["sheet_name"] for cfg in self.SHEETS_CONFIG.values()]
    
    @property
    def callbacks(self) -> List[str]:
        """Получить список callback данных"""
        return [cfg["callback"] for cfg in self.SHEETS_CONFIG.values()]
    
    def get_sheet_config(self, key: str) -> Optional[Dict[str, str]]:
        """Получить конфигурацию листа по ключу"""
        return self.SHEETS_CONFIG.get(key)
    
    @classmethod
    def validate(cls):
        """Проверка конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        if not cls.SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID не установлен")
        if not os.path.exists(cls.SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Файл с ключами не найден: {cls.SERVICE_ACCOUNT_FILE}")

# Создаем экземпляр конфига
config = Config()