# services/google_sheets.py
import logging
from typing import List, Tuple, Dict, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

from bot.config import config

logger = logging.getLogger(__name__)

class GoogleSheetsReader:
    """Класс для работы с Google Sheets"""
    
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = None
        self.connect()
    
    def connect(self) -> None:
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
            self.service = None
    
    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> List[Tuple[str, str]]:
        """Получение данных с указанного листа"""
        if not self.service:
            logger.error("❌ Сервис Google Sheets не инициализирован")
            return []
        
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
    
    def get_all_sheets_data(self, spreadsheet_id: str) -> Dict[str, List[Tuple[str, str]]]:
        """Получение данных со всех листов"""
        result = {}
        for key, sheet_config in config.SHEETS_CONFIG.items():
            sheet_name = sheet_config["sheet_name"]
            result[key] = self.get_sheet_data(spreadsheet_id, sheet_name)
        return result
    
    def get_sheet_info(self, spreadsheet_id: str) -> List[str]:
        """Получить список всех листов в таблице"""
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            sheets = result.get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка листов: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self.service is not None

# Инициализация Google Sheets
try:
    sheets_reader = GoogleSheetsReader(config.SERVICE_ACCOUNT_FILE)
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Google Sheets: {e}")
    sheets_reader = None