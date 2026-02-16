# bot/keyboards/main.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import config

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с динамическими кнопками"""
    buttons = []
    
    # Создаем кнопки для всех категорий из конфига
    row = []
    for i, (key, sheet_config) in enumerate(config.SHEETS_CONFIG.items(), 1):
        button_text = f"{sheet_config['emoji']} {sheet_config['display_name']}"
        row.append(
            InlineKeyboardButton(
                text=button_text, 
                callback_data=sheet_config['callback']
            )
        )
        
        # По 2 кнопки в ряд
        if i % 2 == 0:
            buttons.append(row)
            row = []
    
    # Добавляем последний ряд, если остались кнопки
    if row:
        buttons.append(row)
    
    # Добавляем кнопку обновления в конце
    buttons.append([InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Удаляем get_category_keyboard и get_pagination_keyboard