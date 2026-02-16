# bot/config/settings.py
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional, Any

env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

class Config:
    """Класс конфигурации"""
    
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Администраторы
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    
    # Google Sheets
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
    
    # Настройки кэша
    CACHE_UPDATE_INTERVAL = int(os.getenv('CACHE_UPDATE_INTERVAL', 300))
    
    # Иерархическая структура категорий
    CATEGORIES: Dict[str, Dict[str, Any]] = {
        "iphone": {
            "name": "📱 iPhone",
            "emoji": "📱",
            "callback": "menu_iphone",
            "subcategories": {
                "iphone_17_pro_max": {
                    "name": "iPhone 17 Pro Max",
                    "sheet_name": "айфон 17 про макс",
                    "emoji": "📱",
                    "callback": "show_iphone_17_pro_max"
                },
                "iphone_17_pro": {
                    "name": "iPhone 17 Pro",
                    "sheet_name": "айфон 17 про",
                    "emoji": "📱",
                    "callback": "show_iphone_17_pro"
                },
                "iphone_17": {
                    "name": "iPhone 17",
                    "sheet_name": "айфон 17",
                    "emoji": "📱",
                    "callback": "show_iphone_17"
                },
                "iphone_air": {
                    "name": "iPhone Air",
                    "sheet_name": "айфон эйр",
                    "emoji": "📱",
                    "callback": "show_iphone_air"
                },
                "iphone_16_pro_max": {
                    "name": "iPhone 16 Pro Max",
                    "sheet_name": "айфон 16 про макс",
                    "emoji": "📱",
                    "callback": "show_iphone_16_pro_max"
                },
                "iphone_16_pro": {
                    "name": "iPhone 16 Pro",
                    "sheet_name": "айфон 16 про",
                    "emoji": "📱",
                    "callback": "show_iphone_16_pro"
                },
                "iphone_16_plus": {
                    "name": "iPhone 16 Plus",
                    "sheet_name": "айфон 16 плюс",
                    "emoji": "📱",
                    "callback": "show_iphone_16_plus"
                },
                "iphone_16": {
                    "name": "iPhone 16",
                    "sheet_name": "айфон 16",
                    "emoji": "📱",
                    "callback": "show_iphone_16"
                }
            }
        },
        "macbook": {
            "name": "💻 MacBook",
            "emoji": "💻",
            "callback": "menu_macbook",
            "subcategories": {
                "macbook_air": {
                    "name": "MacBook Air",
                    "sheet_name": "макбук эйр",
                    "emoji": "💻",
                    "callback": "show_macbook_air"
                },
                "macbook_pro": {
                    "name": "MacBook Pro",
                    "sheet_name": "макбук про",
                    "emoji": "💻",
                    "callback": "show_macbook_pro"
                }
            }
        },
        "ipad": {
            "name": "📱 iPad",
            "emoji": "📱",
            "callback": "menu_ipad",
            "subcategories": {
                "ipad_air": {
                    "name": "iPad Air",
                    "sheet_name": "айпад эйр",
                    "emoji": "📱",
                    "callback": "show_ipad_air"
                },
                "ipad_pro": {
                    "name": "iPad Pro",
                    "sheet_name": "айпад про",
                    "emoji": "📱",
                    "callback": "show_ipad_pro"
                }
            }
        },
        "watch": {
            "name": "⌚️ Watch",
            "emoji": "⌚️",
            "callback": "menu_watch",
            "subcategories": {
                "watch_ultra": {
                    "name": "Apple Watch Ultra",
                    "sheet_name": "эпл вотч ультра",
                    "emoji": "⌚️",
                    "callback": "show_watch_ultra"
                },
                "watch_11": {
                    "name": "Apple Watch 11",
                    "sheet_name": "эпл вотч 11",
                    "emoji": "⌚️",
                    "callback": "show_watch_11"
                }
            }
        },
        "airpods": {
            "name": "🎧 AirPods",
            "emoji": "🎧",
            "callback": "menu_airpods",
            "sheet_name": "эйрподсы",
            "is_direct": True
        },
        "samsung": {
            "name": "📱 Samsung",
            "emoji": "📱",
            "callback": "menu_samsung",
            "sheet_name": "самсунг",
            "is_direct": True
        },
        "playstation": {
            "name": "🎮 PlayStation",
            "emoji": "🎮",
            "callback": "menu_playstation",
            "sheet_name": "плейстейшн",
            "is_direct": True
        }
    }
    
    def get_all_sheet_names(self) -> List[str]:
        """Получить все названия листов"""
        sheets = []
        for category in self.CATEGORIES.values():
            if category.get("is_direct"):
                sheets.append(category["sheet_name"])
            else:
                for sub in category["subcategories"].values():
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
        if not os.path.exists(cls.SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Файл с ключами не найден: {cls.SERVICE_ACCOUNT_FILE}")

config = Config()