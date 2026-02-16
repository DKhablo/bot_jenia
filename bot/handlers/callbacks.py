# bot/handlers/callbacks.py
import logging
from aiogram.types import CallbackQuery
from aiogram import F

from bot.keyboards import get_main_keyboard
from bot.utils import format_products_list
from data import cache
from services import sheets_reader
from bot.config import config  # ИЗМЕНЕНО: было 'from config import config'

logger = logging.getLogger(__name__)

async def show_iphones(callback: CallbackQuery):
    """Показать список iPhone"""
    await callback.answer()
    products = cache.iphones
    text = format_products_list(products, "iPhone")
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())

async def show_macbooks(callback: CallbackQuery):
    """Показать список MacBook"""
    await callback.answer()
    products = cache.macbooks
    text = format_products_list(products, "MacBook")
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())

async def refresh_data(callback: CallbackQuery):
    """Принудительное обновление данных"""
    await callback.answer("🔄 Обновление данных...")
    
    if sheets_reader and sheets_reader.is_connected():
        await cache.update()
        await callback.message.edit_text(
            f"✅ Данные обновлены!\n\n"
            f"iPhone: {len(cache.iphones)} моделей\n"
            f"MacBook: {len(cache.macbooks)} моделей",
            reply_markup=get_main_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка подключения к Google Sheets",
            reply_markup=get_main_keyboard()
        )

# Регистрация обработчиков
def register_callbacks(dp):
    dp.callback_query.register(show_iphones, F.data == "show_iphones")
    dp.callback_query.register(show_macbooks, F.data == "show_macbooks")
    dp.callback_query.register(refresh_data, F.data == "refresh_data")