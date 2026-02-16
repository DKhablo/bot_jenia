# bot/keyboards/__init__.py
from .main import (
    get_main_keyboard, 
    get_back_to_menu_keyboard,
    get_subcategory_keyboard,
    get_back_keyboard
)

__all__ = [
    'get_main_keyboard',
    'get_back_to_menu_keyboard',
    'get_subcategory_keyboard',
    'get_back_keyboard'
]