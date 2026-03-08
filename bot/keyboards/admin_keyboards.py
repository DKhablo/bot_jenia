# bot/keyboards/admin_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional, List

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура администратора"""
    builder = InlineKeyboardBuilder()

    buttons = [
        ("📋 Список категорий", "admin_list_categories"),
        ("➕ Добавить категорию", "admin_add_category"),
        ("✏️ Редактировать категорию", "admin_edit_category"),
        ("❌ Удалить категорию", "admin_delete_category"),
        ("📊 Просмотр подкатегорий", "admin_view_subcategories"),
        ("⬆️⬇️ Изменить порядок", "admin_reorder_categories"),
        ("💾 Сохранить изменения", "admin_save_changes"),
        ("🔄 Загрузить из файла", "admin_load_changes"),
        ("🔙 Выход", "admin_exit")
    ]

    for text, callback in buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))

    builder.adjust(2)
    return builder.as_markup()

def get_categories_keyboard(categories: List[tuple], action: str = "edit") -> InlineKeyboardMarkup:
    """Клавиатура со списком категорий (отсортированная)"""
    builder = InlineKeyboardBuilder()

    for cat_id, cat_data in categories:
        order = cat_data.get('order', '?')
        button_text = f"{order}. {cat_data.get('emoji', '📁')} {cat_data['name']}"
        callback = f"{action}_cat_{cat_id}"
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback))

    builder.add(InlineKeyboardButton(text="🔙 Назад в главное меню", callback_data="admin_back_to_main"))
    builder.adjust(1)
    return builder.as_markup()

def get_category_edit_keyboard(category_id: str, has_up: bool = True, has_down: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования категории с кнопками изменения порядка"""
    builder = InlineKeyboardBuilder()

    # Кнопки изменения порядка
    order_buttons = []
    if has_up:
        order_buttons.append(("⬆️ Вверх", f"move_cat_up:{category_id}"))
    if has_down:
        order_buttons.append(("⬇️ Вниз", f"move_cat_down:{category_id}"))

    for text, callback in order_buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))

    if order_buttons:
        builder.adjust(2)

    # Основные кнопки редактирования
    edit_buttons = [
        ("📝 Изменить название", f"edit_cat_name:{category_id}"),
        ("😊 Изменить эмодзи", f"edit_cat_emoji:{category_id}"),
        ("🔄 Изменить callback", f"edit_cat_callback:{category_id}"),
        ("📊 Управление подкатегориями", f"manage_subcats:{category_id}"),
        ("🔙 Назад к списку категорий", "admin_edit_category"),
        ("🏠 Главное меню", "admin_back_to_main")
    ]

    for text, callback in edit_buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))

    builder.adjust(1)
    return builder.as_markup()

def get_subcategories_keyboard(category_id: str, subcategories: List[tuple]) -> InlineKeyboardMarkup:
    """Клавиатура для управления подкатегориями (отсортированная)"""
    builder = InlineKeyboardBuilder()

    for sub_id, sub_data in subcategories:
        order = sub_data.get('order', '?')
        button_text = f"{order}. {sub_data.get('emoji', '📄')} {sub_data['name']}"
        callback = f"edit_sub:{category_id}:{sub_id}"
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback))

    # Кнопки управления
    if subcategories:
        builder.add(InlineKeyboardButton(
            text="❌ Удалить все подкатегории",
            callback_data=f"delete_all_subs:{category_id}"
        ))

    builder.add(InlineKeyboardButton(
        text="➕ Добавить подкатегорию",
        callback_data=f"add_sub:{category_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад к категории",
        callback_data=f"edit_cat_menu:{category_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🏠 Главное меню",
        callback_data="admin_back_to_main"
    ))

    builder.adjust(1)
    return builder.as_markup()

def get_subcategory_edit_keyboard(category_id: str, subcategory_id: str,
                                  has_up: bool = True, has_down: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования подкатегории с кнопками изменения порядка"""
    builder = InlineKeyboardBuilder()

    # Кнопки изменения порядка
    order_buttons = []
    if has_up:
        order_buttons.append(("⬆️ Вверх", f"move_sub_up:{category_id}:{subcategory_id}"))
    if has_down:
        order_buttons.append(("⬇️ Вниз", f"move_sub_down:{category_id}:{subcategory_id}"))

    for text, callback in order_buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))

    if order_buttons:
        builder.adjust(2)

    # Основные кнопки редактирования
    edit_buttons = [
        ("📝 Изменить название", f"edit_sub_name:{category_id}:{subcategory_id}"),
        ("😊 Изменить эмодзи", f"edit_sub_emoji:{category_id}:{subcategory_id}"),
        ("📄 Изменить sheet_name", f"edit_sub_sheet:{category_id}:{subcategory_id}"),
        ("🔄 Изменить callback", f"edit_sub_callback:{category_id}:{subcategory_id}"),
        ("❌ Удалить подкатегорию", f"del_sub:{category_id}:{subcategory_id}"),
        ("🔙 Назад к подкатегориям", f"manage_subcats:{category_id}"),
        ("🏠 Главное меню", "admin_back_to_main")
    ]

    for text, callback in edit_buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))

    builder.adjust(1)
    return builder.as_markup()

def get_reorder_categories_keyboard(categories: List[tuple]) -> InlineKeyboardMarkup:
    """Клавиатура для изменения порядка категорий"""
    builder = InlineKeyboardBuilder()

    for cat_id, cat_data in categories:
        order = cat_data.get('order', '?')
        button_text = f"{order}. {cat_data.get('emoji', '📁')} {cat_data['name']}"
        callback = f"reorder_select:{cat_id}"
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback))

    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back_to_main"))
    builder.adjust(1)
    return builder.as_markup()

def get_confirmation_keyboard(action: str, item_type: str, item_id: str,
                             parent_id: Optional[str] = None) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()

    if parent_id:
        confirm_data = f"confirm_{action}_{item_type}:{item_id}:{parent_id}"
        back_data = f"edit_cat_menu:{parent_id}" if item_type == "subcategory" else "admin_back_to_main"
    else:
        confirm_data = f"confirm_{action}_{item_type}:{item_id}"
        back_data = "admin_edit_category" if item_type == "category" else "admin_back_to_main"

    builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_data))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data=back_data))

    builder.adjust(2)
    return builder.as_markup()

def get_back_keyboard(callback: str = "admin_back_to_main") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=callback))
    return builder.as_markup()