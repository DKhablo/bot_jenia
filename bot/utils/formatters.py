from typing import List, Tuple

def format_products_list(products: List[Tuple[str, str]], category: str) -> str:
    """Форматирование списка товаров для вывода"""
    if not products:
        return f"❌ Нет данных по категории {category}"
    
    text = f"<b>📋 {category}</b>\n\n"
    for i, (model, price) in enumerate(products, 1):
        text += f"{i}. {model} — <b>{price} ₽</b>\n"
    
    return text