# bot/handlers/commands.py
import logging
from aiogram import types
from aiogram.filters import Command

from bot.keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Я бот для просмотра товаров из Google Sheets.\n"
        "Выберите категорию:",
        reply_markup=get_main_keyboard()
    )

async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    await message.answer(
        "📋 Главное меню:",
        reply_markup=get_main_keyboard()
    )

async def cmd_test(message: types.Message):
    """Тестовая команда"""
    await message.answer("✅ Бот работает!")

# Регистрация обработчиков
def register_commands(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_test, Command("test"))