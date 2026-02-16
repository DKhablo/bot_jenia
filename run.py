#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настраиваем логирование до всего остального
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем после настройки логирования
from bot.config import config
from bot.handlers.commands import register_commands
from bot.handlers.callbacks import register_callbacks
from data import cache
from services import sheets_reader

# Глобальные переменные
bot = None
dp = None

async def shutdown(signal, loop):
    """Graceful shutdown"""
    logger.info(f"Получен сигнал {signal.name}...")
    if bot:
        await cache.stop_auto_update()
        await bot.session.close()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    logger.info(f"Отменено {len(tasks)} задач")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    global bot, dp
    
    logger.info("=" * 50)
    logger.info("🚀 Бот запускается...")
    
    # Проверка конфигурации
    try:
        config.validate()
        logger.info("✅ Конфигурация загружена")
    except Exception as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.types import BotCommand
    
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
        return
    
    # Проверка Google Sheets
    if sheets_reader and sheets_reader.is_connected():
        logger.info("✅ Google Sheets API подключен")
        try:
            await cache.update()
            logger.info(f"📊 Загружено: iPhone ({len(cache.iphones)}), MacBook ({len(cache.macbooks)})")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки: {e}")
    else:
        logger.error("❌ Google Sheets API не подключен")
        # Продолжаем работу с пустым кэшем
    
    # Регистрация обработчиков
    register_commands(dp)
    register_callbacks(dp)
    
    # Обработчик неизвестных сообщений
    @dp.message()
    async def handle_unknown(message):
        logger.info(f"Получено сообщение: {message.text}")
        await message.answer(
            "❌ Неизвестная команда. Используйте /start или /menu"
        )
    
    # Настройка команд
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="test", description="Проверка работы"),
    ]
    await bot.set_my_commands(commands)
    
    # Запуск автообновления кэша
    if sheets_reader and sheets_reader.is_connected():
        await cache.start_auto_update()
    
    # Запуск бота
    logger.info("🔄 Бот начинает polling...")
    try:
        await dp.start_polling(bot)
    finally:
        if sheets_reader and sheets_reader.is_connected():
            await cache.stop_auto_update()
        await bot.session.close()
    
    logger.info("=" * 50)

if __name__ == "__main__":
    # Создаем новый event loop для macOS
    if sys.platform == 'darwin':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Настраиваем обработку сигналов
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(s, loop))
            )
        
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()
    else:
        # Для других ОС
        asyncio.run(main())