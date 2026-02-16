# bot/utils/formatters.py
from typing import List, Tuple, Dict
from bot.config import config

def format_products_list(products: List[Tuple[str, str]], category: str) -> str:
    """Форматирование списка товаров для вывода"""
    if not products:
        return f"❌ Нет данных по категории {category}"
    
    # Находим эмодзи для категории
    emoji = "📦"
    for sheet_config in config.SHEETS_CONFIG.values():
        if sheet_config['display_name'] == category:
            emoji = sheet_config['emoji']
            break
    
    text = f"<b>{emoji} {category}</b>\n\n"
    for i, (model, price) in enumerate(products, 1):
        # Форматируем цену (добавляем пробелы для тысяч)
        try:
            # Убираем все пробелы из строки цены и пробуем преобразовать в int
            price_clean = price.replace(' ', '').replace('₽', '').strip()
            price_int = int(float(price_clean)) if '.' in price_clean else int(price_clean)
            formatted_price = f"{price_int:,}".replace(',', ' ')
        except (ValueError, TypeError):
            formatted_price = price
        
        text += f"{i}. {model} — <b>{formatted_price} ₽</b>\n"
    
    # Добавляем информацию о количестве
    text += f"\nВсего: {len(products)} товаров"
    
    return text

def format_stats(stats: Dict[str, int]) -> str:
    """Форматирование статистики"""
    if not stats:
        return "📊 Нет данных для статистики"
    
    text = "📊 <b>Статистика</b>\n\n"
    total_items = 0
    
    for key, count in stats.items():
        sheet_config = config.get_sheet_config(key)
        if sheet_config:
            text += f"{sheet_config['emoji']} {sheet_config['display_name']}: {count}\n"
            total_items += count
    
    text += f"\n<b>Всего товаров: {total_items}</b>"
    
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
            else:
                return f"{price_float:,.2f}".replace(',', ' ')
        else:
            price_int = int(price_clean)
            return f"{price_int:,}".replace(',', ' ')
    except (ValueError, TypeError):
        return price
    return price