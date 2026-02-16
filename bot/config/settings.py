# bot/config/settings.py
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из корневого .env
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
    
    # Названия листов
    SHEET_IPHONE = "айфоны"
    SHEET_MACBOOK = "макбуки"
    
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