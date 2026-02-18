#!/usr/bin/env python3
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from bot.config import config
from bot.handlers.commands import register_commands
from bot.handlers.callbacks import register_callbacks
from data import cache
from services import sheets_reader

import psutil
import os

# Добавьте в начало файла после импортов
def log_memory_usage():
    """Логирование использования памяти"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # В байтах
    rss = memory_info.rss  # Resident Set Size - память в RAM
    vms = memory_info.vms  # Virtual Memory Size - виртуальная память
    
    # Конвертируем в MB
    rss_mb = rss / 1024 / 1024
    vms_mb = vms / 1024 / 1024
    
    # Процент использования CPU
    cpu_percent = process.cpu_percent(interval=1)
    
    # Общая память системы
    system_memory = psutil.virtual_memory()
    
    logger.info("=" * 50)
    logger.info("📊 ИСПОЛЬЗОВАНИЕ РЕСУРСОВ:")
    logger.info(f"💾 RAM (RSS): {rss_mb:.2f} MB")
    logger.info(f"💿 Виртуальная память: {vms_mb:.2f} MB")
    logger.info(f"⚙️ CPU: {cpu_percent:.1f}%")
    logger.info(f"🖥️ Всего RAM в системе: {system_memory.total / 1024 / 1024:.0f} MB")
    logger.info(f"📈 Свободно RAM: {system_memory.available / 1024 / 1024:.0f} MB")
    logger.info("=" * 50)
    
    return rss_mb

# Добавьте периодический мониторинг
async def memory_monitor():
    """Мониторинг памяти каждые 60 секунд"""
    while True:
        await asyncio.sleep(60)
        memory_usage = log_memory_usage()
        
        # Предупреждение если памяти слишком много
        if memory_usage > 150:
            logger.warning(f"⚠️ ВЫСОКОЕ ИСПОЛЬЗОВАНИЕ ПАМЯТИ: {memory_usage:.2f} MB")
        
        # Критическое предупреждение
        if memory_usage > 300:
            logger.error(f"❌ КРИТИЧЕСКОЕ ИСПОЛЬЗОВАНИЕ ПАМЯТИ: {memory_usage:.2f} MB")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем глобальные переменные
bot = None
dp = None

async def main():
    global bot, dp
    
    logger.info("=" * 50)
    logger.info("🚀 Бот запускается...")
    
    # Проверка конфигурации
    try:
        config.validate()
        logger.info("✅ Конфигурация загружена")
        logger.info(f"👑 Администраторы: {config.ADMIN_IDS}")
    except Exception as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Инициализация бота
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Проверка подключения к Telegram
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот @{me.username} успешно подключен")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram: {e}")
        await bot.session.close()
        return
    
    # Проверка Google Sheets
    if sheets_reader and sheets_reader.is_connected():
        logger.info("✅ Google Sheets API подключен")
        try:
            await cache.update_all()
            logger.info("✅ Данные загружены")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
    else:
        logger.error("❌ Google Sheets API не подключен")
    
    # Регистрация обработчиков
    register_commands(dp)
    register_callbacks(dp)
    
    # Обработчик неизвестных сообщений
    @dp.message()
    async def handle_unknown(message):
        await message.answer("❌ Неизвестная команда. Используйте /start")
    
    # Настройка команд
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="stats", description="Статистика"),
        BotCommand(command="admin", description="Проверка администратора"),
    ]
    await bot.set_my_commands(commands)
    
    # Запуск бота
    logger.info("🔄 Бот начинает polling...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    # Для macOS
    if sys.platform == 'darwin':
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("👋 Бот остановлен")
    else:
        asyncio.run(main())