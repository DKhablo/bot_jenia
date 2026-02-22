# bot/utils/formatters.py
from typing import List, Tuple, Dict
from bot.config import config

def format_products_list(products: List[Tuple[str, str]], category: str) -> str:
    """Форматирование списка товаров для вывода"""
    count=1

    if not products:
        return f"❌ Нет данных по категории {category}"
    
    # Находим эмодзи для категории
    emoji = "📦"
    
    # Ищем в основных категориях
    for cat_key, category_data in config.CATEGORIES.items():
        if category_data.get("is_direct") and category_data["name"] == category:
            emoji = category_data["emoji"]
            break
        # Ищем в подкатегориях
        elif not category_data.get("is_direct") and "subcategories" in category_data:
            for sub_key, subcategory in category_data["subcategories"].items():
                if subcategory["name"] == category:
                    emoji = subcategory["emoji"]
                    break
    
    text = f"<b>{emoji} {category}</b>\n"
    text += "_" * 35 + "\n"
    text += f"<i>Вы можете скопировать нужную позицию простым нажатием на текст, а затем отправить её в личные сообщения</i> \n"
    text += "_" * 35 + "\n\n"

    for i, (model, price) in enumerate(products, 1):
        # Форматируем цену
        formatted_price = format_price(price)
        if len(model) > 10:
            if price != "0":
                text += f"<code><b>{count}.</b> {model}\n   💰 <b>{formatted_price}</b></code>\n\n"
                count += 1
        else:
            text += f"<b>__________  {model}  __________</b>\n"
            count = 1
    
    return text

def format_price(price: str) -> str:
    """Форматирование цены"""
    try:
        # Убираем все пробелы и символы валют
        price_clean = price.replace(' ', '').replace('₽', '').replace('$', '').strip()
        
        # Пробуем преобразовать в число
        if '.' in price_clean:
            price_float = float(price_clean)
            if price_float.is_integer():
                price_int = int(price_float)
                formatted = f"{price_int:,}".replace(',', ' ')
            else:
                formatted = f"{price_float:,.2f}".replace(',', ' ')
        else:
            price_int = int(price_clean)
            formatted = f"{price_int:,}".replace(',', ' ')
        
        return f"{formatted} ₽"
    except (ValueError, TypeError):
        return price

def format_stats(stats: Dict[str, int]) -> str:
    """Форматирование статистики"""
    if not stats:
        return "📊 Нет данных для статистики"
    
    text = "📊 <b>Статистика</b>\n"
    text += "═" * 20 + "\n\n"
    
    total_items = 0
    
    # Собираем все названия категорий для отображения
    category_names = {}
    
    # Основные категории
    for cat_key, category in config.CATEGORIES.items():
        if category.get("is_direct"):
            category_names[cat_key] = {
                "name": category["name"],
                "emoji": category["emoji"]
            }
        else:
            # Подкатегории
            for sub_key, subcategory in category["subcategories"].items():
                category_names[sub_key] = {
                    "name": subcategory["name"],
                    "emoji": subcategory["emoji"]
                }
    
    # Выводим статистику
    for key, count in stats.items():
        if key in category_names:
            text += f"{category_names[key]['emoji']} <b>{category_names[key]['name']}:</b> {count}\n"
            total_items += count
    
    text += "\n" + "─" * 20 + "\n"
    text += f"📦 <b>Всего товаров:</b> {total_items}"
    
    return text