# bot/handlers/callbacks.py
import logging
from aiogram.types import CallbackQuery
from aiogram import F

from bot.keyboards import (
    get_main_keyboard, 
    get_subcategory_keyboard, 
    get_back_keyboard,
    get_back_to_menu_keyboard
)
from bot.utils import format_products_list
from data import cache
from services import sheets_reader
from bot.config import config

logger = logging.getLogger(__name__)

# Хранилище последней выбранной категории
user_last_category = {}

async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    await callback.answer()
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )

async def show_category_menu(callback: CallbackQuery):
    """Показать меню категории"""
    await callback.answer()
    
    # Получаем callback data
    callback_data = callback.data
    
    # Находим категорию по callback data
    category_key = None
    category_data = None
    
    for key, category in config.CATEGORIES.items():
        if category["callback"] == callback_data:
            category_key = key
            category_data = category
            break
    
    if not category_data:
        await callback.message.edit_text(
            "❌ Категория не найдена",
            reply_markup=get_main_keyboard(callback.from_user.id)
        )
        return
    
    # Сохраняем последнюю категорию
    user_last_category[callback.from_user.id] = category_key
    
    # Если это прямая категория
    if category_data.get("is_direct"):
        products = cache.get_category(category_key)
        text = format_products_list(products, category_data["name"])
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_menu_keyboard()
        )
    else:
        # Показываем подкатегории
        await callback.message.edit_text(
            f"{category_data['name']}\n\nВыберите модель:",
            reply_markup=get_subcategory_keyboard(category_key, callback.from_user.id)
        )

async def show_product_category(callback: CallbackQuery):
    """Показать товары подкатегории"""
    await callback.answer()
    
    # Получаем callback data
    callback_data = callback.data
    
    # Ищем подкатегорию по callback data
    product_key = None
    product_data = None
    parent_category = None
    
    for cat_key, category in config.CATEGORIES.items():
        if not category.get("is_direct") and "subcategories" in category:
            for sub_key, subcategory in category["subcategories"].items():
                if subcategory["callback"] == callback_data:
                    product_key = sub_key
                    product_data = subcategory
                    parent_category = cat_key
                    break
        if product_data:
            break
    
    if not product_data:
        await callback.message.edit_text(
            "❌ Товар не найден",
            reply_markup=get_main_keyboard(callback.from_user.id)
        )
        return
    
    # Сохраняем последнюю категорию
    user_last_category[callback.from_user.id] = parent_category
    
    # Получаем данные
    products = cache.get_category(product_key)
    text = format_products_list(products, product_data["name"])
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard()
    )

async def back_to_categories(callback: CallbackQuery):
    """Вернуться к основным категориям"""
    await callback.answer()
    await show_main_menu(callback)

async def back_to_subcategories(callback: CallbackQuery):
    """Вернуться к подкатегориям"""
    await callback.answer()
    
    # Получаем последнюю категорию
    last_category = user_last_category.get(callback.from_user.id)
    
    if last_category and last_category in config.CATEGORIES:
        category = config.CATEGORIES[last_category]
        await callback.message.edit_text(
            f"{category['name']}\n\nВыберите модель:",
            reply_markup=get_subcategory_keyboard(last_category, callback.from_user.id)
        )
    else:
        await show_main_menu(callback)

async def refresh_data(callback: CallbackQuery):
    """Обновление данных (только для админов)"""
    if not config.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await callback.answer("🔄 Обновление...")
    
    if sheets_reader and sheets_reader.is_connected():
        await cache.update_all()
        await callback.message.edit_text(
            "✅ Данные обновлены!",
            reply_markup=get_main_keyboard(callback.from_user.id)
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка подключения",
            reply_markup=get_main_keyboard(callback.from_user.id)
        )

# Регистрация обработчиков
def register_callbacks(dp):
    # Главное меню
    dp.callback_query.register(show_main_menu, F.data == "main_menu")
    dp.callback_query.register(back_to_categories, F.data == "back_to_categories")
    dp.callback_query.register(back_to_subcategories, F.data == "back_to_subcategories")
    
    # Собираем все callback data для категорий и подкатегорий
    category_callbacks = []
    product_callbacks = []
    
    for category in config.CATEGORIES.values():
        category_callbacks.append(category["callback"])
        
        if not category.get("is_direct") and "subcategories" in category:
            for subcategory in category["subcategories"].values():
                product_callbacks.append(subcategory["callback"])
    
    # Регистрируем обработчики категорий
    for callback_data in category_callbacks:
        dp.callback_query.register(show_category_menu, F.data == callback_data)
    
    # Регистрируем обработчики товаров
    for callback_data in product_callbacks:
        dp.callback_query.register(show_product_category, F.data == callback_data)
    
    # Обновление данных
    dp.callback_query.register(refresh_data, F.data == "refresh_data")