from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    buttons = [
        [InlineKeyboardButton(text="📱 iPhone", callback_data="show_iphones"), InlineKeyboardButton(text="💻 MacBook", callback_data="show_macbooks")],
        [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)