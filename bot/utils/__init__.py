# bot/utils/__init__.py
from .formatters import format_products_list, format_stats

__all__ = [
    'format_products_list',
    'format_stats',
    'paginate_items',
    'format_paginated_text',
    'split_into_pages'
]