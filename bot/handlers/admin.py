# bot/handlers/admin.py
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.config.settings import config
from bot.keyboards.admin_keyboards import get_admin_main_keyboard

logger = logging.getLogger(__name__)

router = Router()

class AdminStates(StatesGroup):
    """Состояния для администратора"""
    main_menu = State()

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Обработчик команды /admin"""
    user_id = message.from_user.id
    logger.info(f"Команда /admin от пользователя {user_id}")

    # Проверка на администратора
    if not config.is_admin(user_id):
        await message.answer("⛔ У вас нет прав администратора.")
        return

    # Приветственное сообщение для админа
    welcome_text = (
        "🔧 **Панель администратора**\n\n"
        "Выберите действие:"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.main_menu)

@router.callback_query(F.data == "admin_back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню администратора"""
    await state.clear()
    await callback.message.edit_text(
        "🔧 **Панель администратора**\n\nВыберите действие:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_exit")
async def admin_exit(callback: CallbackQuery, state: FSMContext):
    """Выход из панели администратора"""
    await callback.message.edit_text(
        "👋 Вы вышли из панели администратора."
    )
    await callback.answer()
    await state.clear()