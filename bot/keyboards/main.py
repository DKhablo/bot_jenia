from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import config

def get_main_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    """Главное меню"""
    buttons = []
    row = []
    
    for i, (key, category) in enumerate(config.CATEGORIES.items(), 1):
        button = InlineKeyboardButton(
            text=category["name"],
            callback_data=category["callback"]
        )
        row.append(button)
        
        if i % 2 == 0:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Кнопка обновления только для админов
    if user_id and config.is_admin(user_id):
        buttons.append([InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subcategory_keyboard(category_key: str, user_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура подкатегорий"""
    buttons = []
    category = config.CATEGORIES.get(category_key)
    
    if not category or category.get("is_direct"):
        return get_main_keyboard(user_id)
    
    row = []
    subcategories = list(category["subcategories"].items())
    
    for i, (sub_key, subcategory) in enumerate(subcategories, 1):
        button = InlineKeyboardButton(
            text=f"{subcategory['emoji']} {subcategory['name']}",
            callback_data=subcategory["callback"]
        )
        row.append(button)
        
        if i % 2 == 0:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Кнопки навигации
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_categories")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой в главное меню"""
    buttons = [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    buttons = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_subcategories")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)