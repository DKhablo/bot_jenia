import os
import sys
import logging
from typing import Dict, List, Tuple
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

from dotenv import load_dotenv

load_dotenv()

# Google Sheets импорты
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Проверяем существование файла с ключами
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    logger.error(f"❌ Файл с ключами не найден: {SERVICE_ACCOUNT_FILE}")
    sys.exit(1)

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Класс для работы с Google Sheets
class GoogleSheetsReader:
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = None
        self.connect()
    
    def connect(self):
        """Подключение к Google Sheets API"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Подключение к Google Sheets API успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
    
    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> List[Tuple[str, str]]:
        """Получение данных с указанного листа"""
        try:
            range_name = f"{sheet_name}!A:B"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            
            if not rows:
                logger.warning(f"⚠️ Лист {sheet_name} пуст")
                return []
            
            products = []
            for row in rows[1:]:  # пропускаем заголовок
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    products.append((row[0].strip(), row[1].strip()))
            
            logger.info(f"📊 Загружено {len(products)} записей из листа {sheet_name}")
            return products
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных из листа {sheet_name}: {e}")
            return []

# Инициализация Google Sheets
try:
    sheets_reader = GoogleSheetsReader(SERVICE_ACCOUNT_FILE)
    logger.info("✅ Google Sheets инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Google Sheets: {e}")
    sheets_reader = None

# Кэш для данных
data_cache: Dict[str, List[Tuple[str, str]]] = {
    "iphones": [],
    "macbooks": []
}
CACHE_UPDATE_INTERVAL = 300  # 5 минут

async def update_cache():
    """Обновление кэша данных"""
    global data_cache
    if sheets_reader is None:
        logger.error("❌ Google Sheets не инициализирован, кэш не обновляется")
        return
        
    while True:
        try:
            iphones = sheets_reader.get_sheet_data(SPREADSHEET_ID, "айфоны")
            macbooks = sheets_reader.get_sheet_data(SPREADSHEET_ID, "макбуки")
            
            data_cache["iphones"] = iphones
            data_cache["macbooks"] = macbooks
            
            logger.info(f"✅ Кэш обновлен: iPhone ({len(iphones)}), MacBook ({len(macbooks)})")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления кэша: {e}")
        
        await asyncio.sleep(CACHE_UPDATE_INTERVAL)

# Клавиатуры
def get_main_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📱 iPhone", callback_data="show_iphones")],
        [InlineKeyboardButton(text="💻 MacBook", callback_data="show_macbooks")],
        [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def format_products_list(products: List[Tuple[str, str]], category: str) -> str:
    if not products:
        return f"❌ Нет данных по категории {category}"
    
    text = f"<b>📋 {category}</b>\n\n"
    for i, (model, price) in enumerate(products, 1):
        text += f"{i}. {model} — <b>{price} ₽</b>\n"
    
    return text

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Я бот для просмотра товаров из Google Sheets.\n"
        "Выберите категорию:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Возврат в главное меню"""
    await message.answer(
        "📋 Главное меню:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("test"))
async def cmd_test(message: types.Message):
    """Тестовая команда"""
    await message.answer("✅ Бот работает!")

@dp.callback_query(F.data == "show_iphones")
async def show_iphones(callback: CallbackQuery):
    """Показать список iPhone"""
    await callback.answer()
    products = data_cache.get("iphones", [])
    text = format_products_list(products, "iPhone")
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "show_macbooks")
async def show_macbooks(callback: CallbackQuery):
    """Показать список MacBook"""
    await callback.answer()
    products = data_cache.get("macbooks", [])
    text = format_products_list(products, "MacBook")
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "refresh_data")
async def refresh_data(callback: CallbackQuery):
    """Принудительное обновление данных"""
    await callback.answer("🔄 Обновление данных...")
    
    if sheets_reader:
        iphones = sheets_reader.get_sheet_data(SPREADSHEET_ID, "айфоны")
        macbooks = sheets_reader.get_sheet_data(SPREADSHEET_ID, "макбуки")
        
        data_cache["iphones"] = iphones
        data_cache["macbooks"] = macbooks
        
        await callback.message.edit_text(
            f"✅ Данные обновлены!\n\n"
            f"iPhone: {len(iphones)} моделей\n"
            f"MacBook: {len(macbooks)} моделей",
            reply_markup=get_main_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка подключения к Google Sheets",
            reply_markup=get_main_keyboard()
        )

@dp.message()
async def handle_unknown(message: types.Message):
    """Обработка неизвестных сообщений"""
    logger.info(f"Получено сообщение: {message.text}")
    await message.answer(
        "❌ Неизвестная команда. Используйте /start или /menu"
    )

async def on_startup():
    """Действия при запуске бота"""
    logger.info("=" * 50)
    logger.info("🚀 Бот запускается...")
    
    # Проверяем подключение к Telegram
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот @{me.username} успешно подключен к Telegram")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram: {e}")
        return False

async def main():
    """Главная функция"""
    # Выполняем действия при запуске
    if not await on_startup():
        logger.error("❌ Ошибка при запуске, бот остановлен")
        return
    
    # Запускаем фоновое обновление кэша
    asyncio.create_task(update_cache())
    
    # Первоначальная загрузка данных
    if sheets_reader:
        # Загружаем данные синхронно при запуске
        try:
            iphones = sheets_reader.get_sheet_data(SPREADSHEET_ID, "айфоны")
            macbooks = sheets_reader.get_sheet_data(SPREADSHEET_ID, "макбуки")
            data_cache["iphones"] = iphones
            data_cache["macbooks"] = macbooks
            logger.info(f"📊 Начальная загрузка: iPhone ({len(iphones)}), MacBook ({len(macbooks)})")
        except Exception as e:
            logger.error(f"❌ Ошибка начальной загрузки: {e}")
    
    # Запускаем бота
    logger.info("🔄 Бот начинает polling...")
    await dp.start_polling(bot)

# Эта функция будет вызвана из run.py
if __name__ == "__main__":
    # Для прямого запуска
    asyncio.run(main())