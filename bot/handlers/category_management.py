# bot/handlers/category_management.py
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from bot.config.settings import config
from bot.keyboards.admin_keyboards import (
    get_categories_keyboard, get_category_edit_keyboard,
    get_subcategories_keyboard, get_subcategory_edit_keyboard,
    get_confirmation_keyboard, get_back_keyboard,
    get_admin_main_keyboard, get_reorder_categories_keyboard
)

logger = logging.getLogger(__name__)

router = Router()

class CategoryManagementStates(StatesGroup):
    """Состояния для управления категориями"""
    waiting_for_category_name = State()
    waiting_for_category_emoji = State()
    waiting_for_category_callback = State()
    waiting_for_edit_value = State()
    waiting_for_subcategory_name = State()
    waiting_for_subcategory_emoji = State()
    waiting_for_subcategory_sheet = State()
    waiting_for_subcategory_callback = State()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def safe_get_category(category_id: str) -> tuple:
    """Безопасное получение категории с обработкой ошибок"""
    if not category_id or category_id == "None":
        return None, None

    category = config.CATEGORIES.get(category_id)
    return category_id, category

# ==================== ОБРАБОТЧИКИ НАВИГАЦИИ ====================

@router.callback_query(F.data.startswith("edit_cat_menu:"))
async def back_to_category_menu(callback: CallbackQuery):
    """Возврат к меню редактирования категории"""
    try:
        # Разбираем callback data формата "edit_cat_menu:category_id"
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("❌ Неверный формат данных")
            return

        category_id = parts[1]

        # Получаем категорию
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        # Определяем позицию категории
        sorted_cats = config.get_sorted_categories()
        position = 0
        for i, (cat_id, _) in enumerate(sorted_cats):
            if cat_id == category_id:
                position = i + 1
                break

        has_up = position > 1
        has_down = position < len(sorted_cats)

        # Показываем меню категории
        info_text = (
            f"✏️ **Редактирование категории**\n\n"
            f"**ID:** `{category_id}`\n"
            f"**Название:** {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"**Позиция:** {position} из {len(sorted_cats)}\n"
            f"**Callback:** `{cat_data.get('callback', 'не указан')}`\n"
        )

        if cat_data.get("is_direct"):
            info_text += f"**Sheet:** `{cat_data.get('sheet_name', 'не указан')}`\n"
        else:
            info_text += f"**Подкатегорий:** {len(cat_data.get('subcategories', {}))}\n"

        await callback.message.edit_text(
            info_text,
            reply_markup=get_category_edit_keyboard(category_id, has_up, has_down),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}",
            reply_markup=get_admin_main_keyboard()
        )
        await callback.answer()

# ==================== СПИСОК КАТЕГОРИЙ ====================

@router.callback_query(F.data == "admin_list_categories")
async def list_categories(callback: CallbackQuery):
    """Показать список всех категорий"""
    if not config.CATEGORIES:
        await callback.message.edit_text(
            "📋 **Список категорий пуст**",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    sorted_cats = config.get_sorted_categories()
    categories_text = "**📋 Список всех категорий:**\n\n"

    for cat_id, cat_data in sorted_cats:
        emoji = cat_data.get('emoji', '📁')
        name = cat_data['name']
        order = cat_data.get('order', '?')

        # Подсчет подкатегорий
        if cat_data.get("is_direct"):
            sub_count = "прямая категория"
        else:
            sub_count = f"подкатегорий: {len(cat_data.get('subcategories', {}))}"

        categories_text += f"{order}. {emoji} **{name}**\n"
        categories_text += f"└ ID: `{cat_id}` | {sub_count}\n\n"

    await callback.message.edit_text(
        categories_text,
        reply_markup=get_back_keyboard("admin_back_to_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

# ==================== ДОБАВЛЕНИЕ КАТЕГОРИИ ====================

@router.callback_query(F.data == "admin_add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления новой категории"""
    await callback.message.edit_text(
        "➕ **Добавление новой категории**\n\n"
        "Введите название категории (например, 'Apple iPhone'):",
        parse_mode="Markdown",
        reply_markup=get_back_keyboard("admin_back_to_main")
    )
    await state.set_state(CategoryManagementStates.waiting_for_category_name)
    await callback.answer()

@router.message(StateFilter(CategoryManagementStates.waiting_for_category_name))
async def process_category_name(message: Message, state: FSMContext):
    """Обработка названия новой категории"""
    category_name = message.text.strip()
    await state.update_data(category_name=category_name)

    await message.answer(
        "Теперь введите эмодзи для категории (например, 📱):",
        reply_markup=get_back_keyboard("admin_back_to_main")
    )
    await state.set_state(CategoryManagementStates.waiting_for_category_emoji)

@router.message(StateFilter(CategoryManagementStates.waiting_for_category_emoji))
async def process_category_emoji(message: Message, state: FSMContext):
    """Обработка эмодзи новой категории"""
    category_emoji = message.text.strip()
    await state.update_data(category_emoji=category_emoji)

    await message.answer(
        "Введите callback_data для категории (например, 'menu_iphone'):",
        reply_markup=get_back_keyboard("admin_back_to_main")
    )
    await state.set_state(CategoryManagementStates.waiting_for_category_callback)

@router.message(StateFilter(CategoryManagementStates.waiting_for_category_callback))
async def process_category_callback(message: Message, state: FSMContext):
    """Создание новой категории"""
    callback_data = message.text.strip()
    data = await state.get_data()

    # Генерируем ID для новой категории
    new_id = callback_data.replace("menu_", "").lower()

    # Проверяем, не существует ли уже такая категория
    if new_id in config.CATEGORIES:
        await message.answer(
            f"❌ Категория с ID `{new_id}` уже существует!\n"
            f"Попробуйте другой callback_data.",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard("admin_back_to_main")
        )
        await state.set_state(CategoryManagementStates.waiting_for_category_callback)
        return

    # Определяем порядковый номер для новой категории
    max_order = 0
    for cat_data in config.CATEGORIES.values():
        if cat_data.get('order', 0) > max_order:
            max_order = cat_data.get('order', 0)
    new_order = max_order + 1

    # Создаем новую категорию
    config.CATEGORIES[new_id] = {
        "name": data['category_name'],
        "emoji": data['category_emoji'],
        "callback": callback_data,
        "order": new_order,
        "subcategories": {}
    }

    # Сохраняем изменения
    config.save_categories()

    await message.answer(
        f"✅ **Категория успешно создана!**\n\n"
        f"ID: `{new_id}`\n"
        f"Название: {data['category_emoji']} {data['category_name']}\n"
        f"Callback: `{callback_data}`\n"
        f"Порядковый номер: {new_order}",
        parse_mode="Markdown",
        reply_markup=get_admin_main_keyboard()
    )

    await state.clear()

# ==================== РЕДАКТИРОВАНИЕ КАТЕГОРИИ ====================

@router.callback_query(F.data == "admin_edit_category")
async def edit_category_list(callback: CallbackQuery):
    """Показать список категорий для редактирования"""
    if not config.CATEGORIES:
        await callback.message.edit_text(
            "📋 **Нет категорий для редактирования**",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    sorted_cats = config.get_sorted_categories()

    await callback.message.edit_text(
        "✏️ **Выберите категорию для редактирования:**",
        reply_markup=get_categories_keyboard(sorted_cats, "edit"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_cat_"))
async def edit_category_menu(callback: CallbackQuery):
    """Меню редактирования конкретной категории"""
    logger.info(f"Открытие меню редактирования категории от {callback.from_user.id}: {callback.data}")
    category_id = callback.data.replace("edit_cat_", "")

    cat_id, cat_data = safe_get_category(category_id)
    if not cat_data:
        await callback.message.edit_text(
            "❌ Категория не найдена. Возврат к списку.",
            reply_markup=get_categories_keyboard(config.get_sorted_categories(), "edit"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    # Определяем позицию категории
    sorted_cats = config.get_sorted_categories()
    position = 0
    for i, (cat_id, _) in enumerate(sorted_cats):
        if cat_id == category_id:
            position = i + 1
            break

    has_up = position > 1
    has_down = position < len(sorted_cats)

    info_text = (
        f"✏️ **Редактирование категории**\n\n"
        f"**ID:** `{cat_id}`\n"
        f"**Название:** {cat_data.get('emoji', '')} {cat_data['name']}\n"
        f"**Позиция:** {position} из {len(sorted_cats)}\n"
        f"**Callback:** `{cat_data.get('callback', 'не указан')}`\n"
    )

    if cat_data.get("is_direct"):
        info_text += f"**Sheet:** `{cat_data.get('sheet_name', 'не указан')}`\n"
    else:
        info_text += f"**Подкатегорий:** {len(cat_data.get('subcategories', {}))}\n"

    await callback.message.edit_text(
        info_text,
        reply_markup=get_category_edit_keyboard(cat_id, has_up, has_down),
        parse_mode="Markdown"
    )
    await callback.answer()

# ==================== УДАЛЕНИЕ КАТЕГОРИИ ====================

@router.callback_query(F.data == "admin_delete_category")
async def delete_category_list(callback: CallbackQuery):
    """Показать список категорий для удаления"""
    if not config.CATEGORIES:
        await callback.message.edit_text(
            "📋 **Нет категорий для удаления**",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    sorted_cats = config.get_sorted_categories()

    await callback.message.edit_text(
        "❌ **Выберите категорию для удаления:**",
        reply_markup=get_categories_keyboard(sorted_cats, "delete"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category_confirm(callback: CallbackQuery):
    """Подтверждение удаления категории"""
    category_id = callback.data.replace("delete_cat_", "")

    cat_id, cat_data = safe_get_category(category_id)
    if not cat_data:
        await callback.message.edit_text(
            "❌ Категория не найдена. Возврат к списку.",
            reply_markup=get_categories_keyboard(config.get_sorted_categories(), "delete"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"⚠️ **Подтверждение удаления**\n\n"
        f"Вы действительно хотите удалить категорию:\n"
        f"{cat_data.get('emoji', '')} **{cat_data['name']}**?\n\n"
        f"Это действие нельзя отменить!",
        reply_markup=get_confirmation_keyboard("delete", "category", cat_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_category:"))
async def delete_category_execute(callback: CallbackQuery):
    """Выполнение удаления категории"""
    category_id = callback.data.split(":")[1]

    if category_id in config.CATEGORIES:
        del config.CATEGORIES[category_id]

        # Перенумеровываем порядок оставшихся категорий
        sorted_cats = config.get_sorted_categories()
        for i, (cat_id, cat_data) in enumerate(sorted_cats):
            cat_data['order'] = i + 1

        config.save_categories()

        await callback.message.edit_text(
            "✅ **Категория успешно удалена!**",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ Категория не найдена",
            reply_markup=get_admin_main_keyboard()
        )

    await callback.answer()

# ==================== УПРАВЛЕНИЕ ПОДКАТЕГОРИЯМИ ====================

@router.callback_query(F.data == "admin_view_subcategories")
async def view_subcategories_list(callback: CallbackQuery):
    """Показать категории для просмотра подкатегорий"""
    if not config.CATEGORIES:
        await callback.message.edit_text(
            "📋 **Нет категорий для просмотра**",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    sorted_cats = config.get_sorted_categories()

    await callback.message.edit_text(
        "📊 **Выберите категорию для просмотра подкатегорий:**",
        reply_markup=get_categories_keyboard(sorted_cats, "view_subs"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("view_subs_cat_"))
async def show_subcategories(callback: CallbackQuery):
    """Показать подкатегории выбранной категории"""
    category_id = callback.data.replace("view_subs_cat_", "")

    cat_id, cat_data = safe_get_category(category_id)
    if not cat_data:
        await callback.message.edit_text(
            "❌ Категория не найдена. Возврат к списку.",
            reply_markup=get_categories_keyboard(config.get_sorted_categories(), "view_subs"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    if cat_data.get("is_direct"):
        await callback.message.edit_text(
            f"ℹ️ Категория **{cat_data['name']}** является прямой и не имеет подкатегорий.",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        return

    subcategories = cat_data.get("subcategories", {})
    sorted_subs = config.get_sorted_subcategories(category_id)

    if not subcategories:
        await callback.message.edit_text(
            f"📊 **Подкатегории для {cat_data['name']}**\n\n"
            f"Нет подкатегорий.",
            reply_markup=get_back_keyboard(f"edit_cat_menu:{cat_id}"),
            parse_mode="Markdown"
        )
        return

    text = f"📊 **Подкатегории для {cat_data['name']}:**\n\n"

    for sub_id, sub_data in sorted_subs:
        order = sub_data.get('order', '?')
        text += f"{order}. {sub_data.get('emoji', '📄')} **{sub_data['name']}**\n"
        text += f"└ ID: `{sub_id}`\n"
        text += f"└ Sheet: `{sub_data.get('sheet_name', 'не указан')}`\n\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(f"edit_cat_menu:{cat_id}"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("manage_subcats:"))
async def manage_subcategories(callback: CallbackQuery):
    """Управление подкатегориями категории"""
    try:
        # Разбираем callback data формата "manage_subcats:category_id"
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("❌ Неверный формат данных")
            return

        category_id = parts[1]

        # Получаем категорию
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        # Если это прямая категория, преобразуем
        if cat_data.get("is_direct"):
            cat_data["subcategories"] = {}
            if "is_direct" in cat_data:
                del cat_data["is_direct"]
            if "sheet_name" in cat_data:
                del cat_data["sheet_name"]

        sorted_subs = config.get_sorted_subcategories(category_id)

        await callback.message.edit_text(
            f"📊 **Управление подкатегориями**\n"
            f"Категория: {cat_data['name']}\n\n"
            f"Всего подкатегорий: {len(sorted_subs)}",
            reply_markup=get_subcategories_keyboard(category_id, sorted_subs),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}",
            reply_markup=get_admin_main_keyboard()
        )
        await callback.answer()

@router.callback_query(F.data.startswith("edit_sub:"))
async def edit_subcategory(callback: CallbackQuery):
    """Редактирование подкатегории"""
    try:
        # Разбираем callback data формата "edit_sub:category_id:subcategory_id"
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        # Получаем категорию
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                f"❌ Категория с ID '{category_id}' не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        # Получаем подкатегорию
        subcategories = cat_data.get("subcategories", {})
        sub_data = subcategories.get(subcategory_id)

        if not sub_data:
            await callback.message.edit_text(
                f"❌ Подкатегория с ID '{subcategory_id}' не найдена в категории '{cat_data['name']}'.",
                reply_markup=get_subcategories_keyboard(category_id, config.get_sorted_subcategories(category_id)),
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        # Определяем позицию подкатегории
        sorted_subs = config.get_sorted_subcategories(category_id)
        position = 0
        for i, (sub_id, _) in enumerate(sorted_subs):
            if sub_id == subcategory_id:
                position = i + 1
                break

        has_up = position > 1
        has_down = position < len(sorted_subs)

        # Показываем информацию о подкатегории
        info_text = (
            f"✏️ **Редактирование подкатегории**\n\n"
            f"**Категория:** {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"**ID категории:** `{category_id}`\n"
            f"**ID подкатегории:** `{subcategory_id}`\n"
            f"**Название:** {sub_data.get('emoji', '📄')} {sub_data['name']}\n"
            f"**Позиция:** {position} из {len(sorted_subs)}\n"
            f"**Sheet:** `{sub_data.get('sheet_name', 'не указан')}`\n"
            f"**Callback:** `{sub_data.get('callback', 'не указан')}`\n"
        )

        await callback.message.edit_text(
            info_text,
            reply_markup=get_subcategory_edit_keyboard(category_id, subcategory_id, has_up, has_down),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_admin_main_keyboard()
        )
        await callback.answer()

# ==================== ИЗМЕНЕНИЕ ПОРЯДКА КАТЕГОРИЙ ====================

@router.callback_query(F.data == "admin_reorder_categories")
async def reorder_categories_list(callback: CallbackQuery):
    """Показать список категорий для изменения порядка"""
    if not config.CATEGORIES:
        await callback.message.edit_text(
            "📋 **Нет категорий для изменения порядка**",
            reply_markup=get_back_keyboard("admin_back_to_main"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    sorted_cats = config.get_sorted_categories()

    await callback.message.edit_text(
        "⬆️⬇️ **Изменение порядка категорий**\n\n"
        "Выберите категорию, порядок которой хотите изменить:",
        reply_markup=get_reorder_categories_keyboard(sorted_cats),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reorder_select:"))
async def reorder_category_selected(callback: CallbackQuery):
    """Показать меню изменения порядка для выбранной категории"""
    category_id = callback.data.split(":")[1]

    cat_data = config.CATEGORIES.get(category_id)
    if not cat_data:
        await callback.answer("❌ Категория не найдена")
        return

    sorted_cats = config.get_sorted_categories()

    # Определяем, можно ли переместить вверх/вниз
    index = None
    for i, (cat_id, _) in enumerate(sorted_cats):
        if cat_id == category_id:
            index = i
            break

    has_up = index > 0
    has_down = index < len(sorted_cats) - 1

    await callback.message.edit_text(
        f"⬆️⬇️ **Изменение порядка категории**\n\n"
        f"Категория: {cat_data.get('emoji', '')} {cat_data['name']}\n"
        f"Текущая позиция: {index + 1} из {len(sorted_cats)}\n\n"
        f"Выберите действие:",
        reply_markup=get_category_edit_keyboard(category_id, has_up, has_down),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("move_cat_up:"))
async def move_category_up(callback: CallbackQuery):
    """Переместить категорию вверх"""
    category_id = callback.data.split(":")[1]

    if config.move_category(category_id, 'up'):
        config.save_categories()
        await callback.answer("✅ Категория перемещена вверх")

        # Обновляем отображение
        cat_data = config.CATEGORIES.get(category_id)
        sorted_cats = config.get_sorted_categories()

        index = None
        for i, (cat_id, _) in enumerate(sorted_cats):
            if cat_id == category_id:
                index = i
                break

        has_up = index > 0
        has_down = index < len(sorted_cats) - 1

        await callback.message.edit_text(
            f"✅ **Категория перемещена вверх**\n\n"
            f"Категория: {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"Новая позиция: {index + 1} из {len(sorted_cats)}",
            reply_markup=get_category_edit_keyboard(category_id, has_up, has_down),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Нельзя переместить дальше")

@router.callback_query(F.data.startswith("move_cat_down:"))
async def move_category_down(callback: CallbackQuery):
    """Переместить категорию вниз"""
    category_id = callback.data.split(":")[1]

    if config.move_category(category_id, 'down'):
        config.save_categories()
        await callback.answer("✅ Категория перемещена вниз")

        # Обновляем отображение
        cat_data = config.CATEGORIES.get(category_id)
        sorted_cats = config.get_sorted_categories()

        index = None
        for i, (cat_id, _) in enumerate(sorted_cats):
            if cat_id == category_id:
                index = i
                break

        has_up = index > 0
        has_down = index < len(sorted_cats) - 1

        await callback.message.edit_text(
            f"✅ **Категория перемещена вниз**\n\n"
            f"Категория: {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"Новая позиция: {index + 1} из {len(sorted_cats)}",
            reply_markup=get_category_edit_keyboard(category_id, has_up, has_down),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Нельзя переместить дальше")

# ==================== ИЗМЕНЕНИЕ ПОРЯДКА ПОДКАТЕГОРИЙ ====================

@router.callback_query(F.data.startswith("move_sub_up:"))
async def move_subcategory_up(callback: CallbackQuery):
    """Переместить подкатегорию вверх"""
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("❌ Неверный формат данных")
        return

    category_id, subcategory_id = parts[1], parts[2]

    if config.move_subcategory(category_id, subcategory_id, 'up'):
        config.save_categories()
        await callback.answer("✅ Подкатегория перемещена вверх")

        # Обновляем отображение
        cat_data = config.CATEGORIES.get(category_id)
        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        sorted_subs = config.get_sorted_subcategories(category_id)

        index = None
        for i, (sub_id, _) in enumerate(sorted_subs):
            if sub_id == subcategory_id:
                index = i
                break

        has_up = index > 0
        has_down = index < len(sorted_subs) - 1

        info_text = (
            f"✏️ **Редактирование подкатегории**\n\n"
            f"**Категория:** {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"**ID категории:** `{category_id}`\n"
            f"**ID подкатегории:** `{subcategory_id}`\n"
            f"**Название:** {sub_data.get('emoji', '📄')} {sub_data['name']}\n"
            f"**Позиция:** {index + 1} из {len(sorted_subs)}\n"
            f"**Sheet:** `{sub_data.get('sheet_name', 'не указан')}`\n"
            f"**Callback:** `{sub_data.get('callback', 'не указан')}`\n"
        )

        await callback.message.edit_text(
            info_text,
            reply_markup=get_subcategory_edit_keyboard(category_id, subcategory_id, has_up, has_down),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Нельзя переместить дальше")

@router.callback_query(F.data.startswith("move_sub_down:"))
async def move_subcategory_down(callback: CallbackQuery):
    """Переместить подкатегорию вниз"""
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("❌ Неверный формат данных")
        return

    category_id, subcategory_id = parts[1], parts[2]

    if config.move_subcategory(category_id, subcategory_id, 'down'):
        config.save_categories()
        await callback.answer("✅ Подкатегория перемещена вниз")

        # Обновляем отображение
        cat_data = config.CATEGORIES.get(category_id)
        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        sorted_subs = config.get_sorted_subcategories(category_id)

        index = None
        for i, (sub_id, _) in enumerate(sorted_subs):
            if sub_id == subcategory_id:
                index = i
                break

        has_up = index > 0
        has_down = index < len(sorted_subs) - 1

        info_text = (
            f"✏️ **Редактирование подкатегории**\n\n"
            f"**Категория:** {cat_data.get('emoji', '')} {cat_data['name']}\n"
            f"**ID категории:** `{category_id}`\n"
            f"**ID подкатегории:** `{subcategory_id}`\n"
            f"**Название:** {sub_data.get('emoji', '📄')} {sub_data['name']}\n"
            f"**Позиция:** {index + 1} из {len(sorted_subs)}\n"
            f"**Sheet:** `{sub_data.get('sheet_name', 'не указан')}`\n"
            f"**Callback:** `{sub_data.get('callback', 'не указан')}`\n"
        )

        await callback.message.edit_text(
            info_text,
            reply_markup=get_subcategory_edit_keyboard(category_id, subcategory_id, has_up, has_down),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Нельзя переместить дальше")

# ==================== РЕДАКТИРОВАНИЕ ПОДКАТЕГОРИЙ ====================

@router.callback_query(F.data.startswith("edit_sub_name:"))
async def edit_subcategory_name_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения названия подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        # Проверяем существование категории и подкатегории
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        if not sub_data:
            await callback.answer("❌ Подкатегория не найдена")
            return

        # Сохраняем данные в состояние
        await state.update_data(
            edit_category_id=category_id,
            edit_subcategory_id=subcategory_id,
            edit_field="name"
        )

        await callback.message.edit_text(
            f"✏️ **Изменение названия подкатегории**\n\n"
            f"Текущее название: {sub_data.get('emoji', '')} {sub_data['name']}\n\n"
            f"Введите новое название:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_sub:{category_id}:{subcategory_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("edit_sub_emoji:"))
async def edit_subcategory_emoji_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения эмодзи подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        # Проверяем существование
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        if not sub_data:
            await callback.answer("❌ Подкатегория не найдена")
            return

        # Сохраняем данные в состояние
        await state.update_data(
            edit_category_id=category_id,
            edit_subcategory_id=subcategory_id,
            edit_field="emoji"
        )

        await callback.message.edit_text(
            f"😊 **Изменение эмодзи подкатегории**\n\n"
            f"Текущий эмодзи: {sub_data.get('emoji', 'не установлен')}\n"
            f"Название: {sub_data['name']}\n\n"
            f"Введите новый эмодзи (например, 📱):",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_sub:{category_id}:{subcategory_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("edit_sub_sheet:"))
async def edit_subcategory_sheet_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения sheet_name подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        # Проверяем существование
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        if not sub_data:
            await callback.answer("❌ Подкатегория не найдена")
            return

        # Сохраняем данные в состояние
        await state.update_data(
            edit_category_id=category_id,
            edit_subcategory_id=subcategory_id,
            edit_field="sheet_name"
        )

        await callback.message.edit_text(
            f"📄 **Изменение sheet_name подкатегории**\n\n"
            f"Текущий sheet_name: `{sub_data.get('sheet_name', 'не указан')}`\n"
            f"Подкатегория: {sub_data['name']}\n\n"
            f"Введите новое название листа в Google Sheets:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_sub:{category_id}:{subcategory_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("edit_sub_callback:"))
async def edit_subcategory_callback_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения callback подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        # Проверяем существование
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        if not sub_data:
            await callback.answer("❌ Подкатегория не найдена")
            return

        # Сохраняем данные в состояние
        await state.update_data(
            edit_category_id=category_id,
            edit_subcategory_id=subcategory_id,
            edit_field="callback"
        )

        await callback.message.edit_text(
            f"🔄 **Изменение callback подкатегории**\n\n"
            f"Текущий callback: `{sub_data.get('callback', 'не указан')}`\n"
            f"Подкатегория: {sub_data['name']}\n\n"
            f"Введите новый callback_data:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_sub:{category_id}:{subcategory_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.message(StateFilter(CategoryManagementStates.waiting_for_edit_value))
async def process_edit_value(message: Message, state: FSMContext):
    """Обработка измененного значения"""
    try:
        logger.info(f"Обработка изменения значения от пользователя {message.from_user.id}: {message.text}")
        data = await state.get_data()
        logger.info(f"Данные состояния: {data}")
        category_id = data.get('edit_category_id')
        subcategory_id = data.get('edit_subcategory_id')
        field = data.get('edit_field')
        new_value = message.text.strip()

        # Получаем категорию и подкатегорию
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await message.answer(
                "❌ Категория не найдена",
                reply_markup=get_admin_main_keyboard()
            )
            await state.clear()
            return

        subcategories = cat_data.get("subcategories", {})
        if subcategory_id is not None and subcategory_id not in subcategories:
            await message.answer(
                "❌ Подкатегория не найдена",
                reply_markup=get_subcategories_keyboard(category_id, config.get_sorted_subcategories(category_id))
            )
            await state.clear()
            return

        # Обновляем поле
        if subcategory_id is None:
            # Изменение категории
            old_value = cat_data.get(field, 'не указано')
            cat_data[field] = new_value
            reply_markup = get_category_edit_keyboard(category_id)
        else:
            # Изменение подкатегории
            old_value = subcategories[subcategory_id].get(field, 'не указано')
            subcategories[subcategory_id][field] = new_value
            reply_markup = get_subcategory_edit_keyboard(category_id, subcategory_id)

        # Сохраняем изменения
        config.save_categories()

        # Показываем результат
        field_names = {
            'name': 'Название',
            'emoji': 'Эмодзи',
            'sheet_name': 'Sheet name',
            'callback': 'Callback'
        }

        field_name = field_names.get(field, field)

        await message.answer(
            f"✅ **{field_name} успешно изменено!**\n\n"
            f"Было: {old_value}\n"
            f"Стало: {new_value}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        await state.clear()

    except Exception as e:
        await message.answer(
            f"❌ Ошибка: {str(e)}",
            reply_markup=get_admin_main_keyboard()
        )
        await state.clear()

# ==================== УДАЛЕНИЕ ПОДКАТЕГОРИЙ ====================

@router.callback_query(F.data.startswith("del_sub:"))
async def delete_subcategory_confirm(callback: CallbackQuery):
    """Подтверждение удаления подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, category_id, subcategory_id = parts

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        sub_data = cat_data.get("subcategories", {}).get(subcategory_id)
        if not sub_data:
            await callback.message.edit_text(
                "❌ Подкатегория не найдена",
                reply_markup=get_subcategories_keyboard(category_id, config.get_sorted_subcategories(category_id))
            )
            await callback.answer()
            return

        await callback.message.edit_text(
            f"⚠️ **Подтверждение удаления**\n\n"
            f"Вы действительно хотите удалить подкатегорию:\n"
            f"{sub_data.get('emoji', '📄')} **{sub_data['name']}**?\n\n"
            f"Это действие нельзя отменить!",
            reply_markup=get_confirmation_keyboard("delete", "subcategory", subcategory_id, category_id),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("confirm_delete_subcategory:"))
async def delete_subcategory_execute(callback: CallbackQuery):
    """Выполнение удаления подкатегории"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return

        action, subcategory_id, category_id = parts

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        if "subcategories" in cat_data and subcategory_id in cat_data["subcategories"]:
            del cat_data["subcategories"][subcategory_id]

            # Перенумеровываем порядок оставшихся подкатегорий
            sorted_subs = config.get_sorted_subcategories(category_id)
            for i, (sub_id, sub_data) in enumerate(sorted_subs):
                sub_data['order'] = i + 1

            config.save_categories()

            await callback.message.edit_text(
                "✅ **Подкатегория успешно удалена!**",
                reply_markup=get_subcategories_keyboard(category_id, config.get_sorted_subcategories(category_id)),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ Подкатегория не найдена",
                reply_markup=get_subcategories_keyboard(category_id, config.get_sorted_subcategories(category_id))
            )

        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("delete_all_subs:"))
async def delete_all_subcategories_confirm(callback: CallbackQuery):
    """Подтверждение удаления всех подкатегорий"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("❌ Неверный формат данных")
            return

        category_id = parts[1]

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        sub_count = len(cat_data.get("subcategories", {}))

        if sub_count == 0:
            await callback.answer("❌ Нет подкатегорий для удаления")
            return

        await callback.message.edit_text(
            f"⚠️ **Подтверждение удаления**\n\n"
            f"Вы действительно хотите удалить ВСЕ подкатегории ({sub_count} шт.)\n"
            f"из категории **{cat_data['name']}**?\n\n"
            f"Это действие нельзя отменить!",
            reply_markup=get_confirmation_keyboard("delete_all", "subcategories", category_id),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("confirm_delete_all_subcategories:"))
async def delete_all_subcategories_execute(callback: CallbackQuery):
    """Выполнение удаления всех подкатегорий"""
    try:
        category_id = callback.data.split(":")[1]

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        cat_data["subcategories"] = {}
        config.save_categories()

        await callback.message.edit_text(
            "✅ **Все подкатегории успешно удалены!**",
            reply_markup=get_subcategories_keyboard(category_id, []),
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

# ==================== ДОБАВЛЕНИЕ ПОДКАТЕГОРИИ ====================

@router.callback_query(F.data.startswith("add_sub:"))
async def add_subcategory_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления новой подкатегории"""
    try:
        # Разбираем callback data формата "add_sub:category_id"
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("❌ Неверный формат данных")
            return

        category_id = parts[1]

        # Получаем категорию
        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.message.edit_text(
                "❌ Категория не найдена. Возврат в главное меню.",
                reply_markup=get_admin_main_keyboard()
            )
            await callback.answer()
            return

        # Сохраняем ID категории
        await state.update_data(parent_category=category_id)

        await callback.message.edit_text(
            f"➕ **Добавление подкатегории**\n"
            f"Категория: {cat_data['name']}\n\n"
            f"Введите название подкатегории (например, 'iPhone 15 Pro Max'):",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"manage_subcats:{category_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_subcategory_name)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.message(StateFilter(CategoryManagementStates.waiting_for_subcategory_name))
async def process_subcategory_name(message: Message, state: FSMContext):
    """Обработка названия новой подкатегории"""
    sub_name = message.text.strip()
    data = await state.get_data()
    parent_category = data.get('parent_category')

    await state.update_data(sub_name=sub_name)

    await message.answer(
        "Теперь введите эмодзи для подкатегории (например, 📱):",
        reply_markup=get_back_keyboard(f"manage_subcats:{parent_category}")
    )
    await state.set_state(CategoryManagementStates.waiting_for_subcategory_emoji)

@router.message(StateFilter(CategoryManagementStates.waiting_for_subcategory_emoji))
async def process_subcategory_emoji(message: Message, state: FSMContext):
    """Обработка эмодзи новой подкатегории"""
    sub_emoji = message.text.strip()
    data = await state.get_data()
    parent_category = data.get('parent_category')

    await state.update_data(sub_emoji=sub_emoji)

    await message.answer(
        "Введите название листа в Google Sheets (например, 'айфон 15 про макс'):",
        reply_markup=get_back_keyboard(f"manage_subcats:{parent_category}")
    )
    await state.set_state(CategoryManagementStates.waiting_for_subcategory_sheet)

@router.message(StateFilter(CategoryManagementStates.waiting_for_subcategory_sheet))
async def process_subcategory_sheet(message: Message, state: FSMContext):
    """Обработка sheet_name новой подкатегории"""
    sheet_name = message.text.strip()
    data = await state.get_data()
    parent_category = data.get('parent_category')

    await state.update_data(sheet_name=sheet_name)

    await message.answer(
        "Введите callback_data для подкатегории (например, 'show_iphone_15_pro_max'):",
        reply_markup=get_back_keyboard(f"manage_subcats:{parent_category}")
    )
    await state.set_state(CategoryManagementStates.waiting_for_subcategory_callback)

@router.message(StateFilter(CategoryManagementStates.waiting_for_subcategory_callback))
async def process_subcategory_callback(message: Message, state: FSMContext):
    """Создание новой подкатегории"""
    callback_data = message.text.strip()
    data = await state.get_data()

    parent_category = data.get('parent_category')

    cat_data = config.CATEGORIES.get(parent_category)
    if not cat_data:
        await message.answer(
            "❌ Категория не найдена. Начните заново.",
            reply_markup=get_admin_main_keyboard()
        )
        await state.clear()
        return

    # Генерируем ID для новой подкатегории
    new_id = callback_data.replace("show_", "").lower()

    # Убеждаемся, что есть словарь подкатегорий
    if "subcategories" not in cat_data:
        cat_data["subcategories"] = {}

    # Проверяем, не существует ли уже такая подкатегория
    if new_id in cat_data["subcategories"]:
        await message.answer(
            f"❌ Подкатегория с ID `{new_id}` уже существует!\n"
            f"Попробуйте другой callback_data.",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"manage_subcats:{parent_category}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_subcategory_callback)
        return

    # Определяем порядковый номер для новой подкатегории
    max_order = 0
    for sub_data in cat_data["subcategories"].values():
        if sub_data.get('order', 0) > max_order:
            max_order = sub_data.get('order', 0)
    new_order = max_order + 1

    # Создаем новую подкатегорию
    cat_data["subcategories"][new_id] = {
        "name": data['sub_name'],
        "emoji": data['sub_emoji'],
        "sheet_name": data['sheet_name'],
        "callback": callback_data,
        "order": new_order
    }

    # Сохраняем изменения
    config.save_categories()

    await message.answer(
        f"✅ **Подкатегория успешно создана!**\n\n"
        f"ID: `{new_id}`\n"
        f"Название: {data['sub_emoji']} {data['sub_name']}\n"
        f"Sheet: `{data['sheet_name']}`\n"
        f"Callback: `{callback_data}`\n"
        f"Порядковый номер: {new_order}",
        parse_mode="Markdown",
        reply_markup=get_subcategories_keyboard(parent_category, config.get_sorted_subcategories(parent_category))
    )

    await state.clear()

# ==================== РЕДАКТИРОВАНИЕ КАТЕГОРИЙ ====================

@router.callback_query(F.data.startswith("edit_cat_name:"))
async def edit_category_name_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения названия категории"""
    try:
        logger.info(f"Начало изменения названия категории от {callback.from_user.id}: {callback.data}")
        category_id = callback.data.split(":")[1]

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        await state.update_data(
            edit_category_id=category_id,
            edit_field="name"
        )

        await callback.message.edit_text(
            f"✏️ **Изменение названия категории**\n\n"
            f"Текущее название: {cat_data.get('emoji', '')} {cat_data['name']}\n\n"
            f"Введите новое название:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_cat_menu:{category_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        logger.info(f"Состояние установлено для пользователя {callback.from_user.id}")
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("edit_cat_emoji:"))
async def edit_category_emoji_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения эмодзи категории"""
    try:
        category_id = callback.data.split(":")[1]

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        await state.update_data(
            edit_category_id=category_id,
            edit_field="emoji"
        )

        await callback.message.edit_text(
            f"😊 **Изменение эмодзи категории**\n\n"
            f"Текущий эмодзи: {cat_data.get('emoji', 'не установлен')}\n"
            f"Название: {cat_data['name']}\n\n"
            f"Введите новый эмодзи (например, 📱):",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_cat_menu:{category_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("edit_cat_callback:"))
async def edit_category_callback_start(callback: CallbackQuery, state: FSMContext):
    """Начало изменения callback категории"""
    try:
        category_id = callback.data.split(":")[1]

        cat_data = config.CATEGORIES.get(category_id)
        if not cat_data:
            await callback.answer("❌ Категория не найдена")
            return

        await state.update_data(
            edit_category_id=category_id,
            edit_field="callback"
        )

        await callback.message.edit_text(
            f"🔄 **Изменение callback категории**\n\n"
            f"Текущий callback: `{cat_data.get('callback', 'не указан')}`\n"
            f"Категория: {cat_data['name']}\n\n"
            f"Введите новый callback_data:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(f"edit_cat_menu:{category_id}")
        )
        await state.set_state(CategoryManagementStates.waiting_for_edit_value)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

# ==================== СОХРАНЕНИЕ И ЗАГРУЗКА ====================

@router.callback_query(F.data == "admin_save_changes")
async def save_changes(callback: CallbackQuery):
    """Сохранить изменения в файл"""
    try:
        config.save_categories()
        await callback.message.edit_text(
            "✅ **Изменения успешно сохранены в файл!**",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Ошибка при сохранении:**\n`{e}`",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()

@router.callback_query(F.data == "admin_load_changes")
async def load_changes(callback: CallbackQuery):
    """Загрузить изменения из файла"""
    try:
        config.load_categories()
        await callback.message.edit_text(
            "✅ **Категории успешно загружены из файла!**",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Ошибка при загрузке:**\n`{e}`",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()