# bot/handlers/callbacks.py
import logging
from aiogram.types import CallbackQuery
from aiogram import F

from bot.keyboards import get_main_keyboard
from bot.utils import format_products_list
from data import cache
from services import sheets_reader
from bot.config import config

logger = logging.getLogger(__name__)

async def show_category(callback: CallbackQuery, category_key: str):
    """Универсальная функция для показа категории"""
    await callback.answer()
    
    # Получаем данные из кэша
    products = cache.get_category(category_key)
    sheet_config = config.get_sheet_config(category_key)
    
    if not sheet_config:
        await callback.message.edit_text(
            "❌ Ошибка: категория не найдена",
            reply_markup=get_main_keyboard()
        )
        return
    
    display_name = sheet_config['display_name']
    text = format_products_list(products, display_name)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard()
    )

# Создаем отдельные функции-обработчики для каждой категории
def create_category_handler(category_key: str):
    """Создает обработчик для конкретной категории"""
    async def handler(callback: CallbackQuery):
        await show_category(callback, category_key)
    return handler

async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    await callback.answer()
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=get_main_keyboard()
    )

async def refresh_data(callback: CallbackQuery):
    """Принудительное обновление данных"""
    await callback.answer("🔄 Обновление данных...")
    
    if sheets_reader and sheets_reader.is_connected():
        await cache.update_all()
        stats = cache.get_stats()
        
        # Формируем сообщение со статистикой
        stats_text = "\n".join([f"{config.SHEETS_CONFIG[k]['display_name']}: {v}" for k, v in stats.items()])
        
        await callback.message.edit_text(
            f"✅ Данные обновлены!\n\n{stats_text}",
            reply_markup=get_main_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка подключения к Google Sheets",
            reply_markup=get_main_keyboard()
        )

# Регистрация обработчиков
def register_callbacks(dp):
    # Регистрируем обработчики для всех категорий
    for key, sheet_config in config.SHEETS_CONFIG.items():
        # Создаем уникальный обработчик для каждой категории
        handler = create_category_handler(key)
        handler.__name__ = f"show_{key}_handler"
        dp.callback_query.register(handler, F.data == sheet_config['callback'])
    
    # Остальные обработчики
    dp.callback_query.register(show_main_menu, F.data == "main_menu")
    dp.callback_query.register(refresh_data, F.data == "refresh_data")