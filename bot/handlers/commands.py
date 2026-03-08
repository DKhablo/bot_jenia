# bot/handlers/commands.py
import logging
from aiogram import types
from aiogram.filters import Command

from bot.keyboards import get_main_keyboard  # Это теперь работает
from data import cache
from bot.utils import format_stats
from bot.config import config

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

    is_admin = config.is_admin(message.from_user.id)

    await message.answer(
        f"👋 Добро пожаловать{', администратор' if is_admin else ''}!\n\n"
        "Выберите категорию:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

async def cmd_menu(message: types.Message):
    """Показать меню"""
    await message.answer(
        "📋 Главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

async def cmd_stats(message: types.Message):
    """Статистика"""
    stats = cache.get_stats()
    text = format_stats(stats)
    is_admin = config.is_admin(message.from_user.id)
    if is_admin:
        await message.answer(text, reply_markup=get_main_keyboard(message.from_user.id))
    else:
        await message.answer(
            f"❌ Вы не администратор\nID: {message.from_user.id}",
            reply_markup=get_main_keyboard(message.from_user.id)
        )

def register_commands(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(cmd_stats, Command("stats"))