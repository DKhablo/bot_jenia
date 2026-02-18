import asyncio
from typing import Optional, List
from aiogram.types import Message
import time

class ProgressBar:
    """Класс для управления анимированным прогресс-баром"""
    
    def __init__(self, total: int, message: Message, emoji: str = "🔄", width: int = 20):
        self.total = total
        self.message = message
        self.emoji = emoji
        self.width = width
        self.current = 0
        self.start_time = time.time()
        self.last_text = ""  # Храним последний текст
        self.last_percent = -1  # Храним последний процент
        
        # Анимационные фреймы
        self.frames = ["◴", "◷", "◶", "◵"]
        self.frame_index = 0
    
    def _get_animation_char(self) -> str:
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        return self.frames[self.frame_index]
    
    def _format_time(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f}с"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}м {secs:.0f}с"
    
    async def update(self, current: int, details: str = "", emoji: str = "📌"):
        """Обновить прогресс-бар с проверкой на изменения"""
        self.current = current
        percent = (self.current * 100) // self.total
        
        # Расчет времени
        elapsed = time.time() - self.start_time
        if self.current > 0:
            estimated = (elapsed / self.current) * (self.total - self.current)
        else:
            estimated = 0
        
        # Создаем прогресс-бар
        filled = (percent * self.width) // 100
        bar = "█" * filled + "░" * (self.width - filled)
        
        # Получаем анимацию
        anim = self._get_animation_char()
        
        # Формируем текст
        message_text = (
            f"{self.emoji} {anim} <b>Обновление данных</b>\n"
            f"┃{bar}┃ {percent}%\n"
            f"📊 <b>Прогресс:</b> {self.current}/{self.total}\n"
        )

        message_text += (
            f"⏱ <b>Прошло:</b> {self._format_time(elapsed)}\n"
            f"⏳ <b>Осталось:</b> {self._format_time(estimated)}"
        )
        
        # ВАЖНО: Обновляем только если текст изменился
        if message_text != self.last_text:
            try:
                await self.message.edit_text(message_text)
                self.last_text = message_text
            except Exception as e:
                # Если ошибка "message not modified" - игнорируем
                if "message is not modified" not in str(e).lower():
                    raise e
        else:
            # Если текст не изменился, просто логируем
            print(f"ℹ️ Пропуск обновления - текст не изменился ({percent}%)")
    
    async def finish(self, summary: str = ""):
        """Завершить прогресс"""
        elapsed = time.time() - self.start_time
        
        message_text = (
            f"✅ <b>Обновление завершено!</b>\n"
            f"✨ <b>Все категории обновлены</b>\n"
            f"⏱ <b>Время:</b> {self._format_time(elapsed)}\n"
        )
        
        if summary:
            message_text += f"\n📊 {summary}"
        
        try:
            await self.message.edit_text(message_text)
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                raise e
        
        await asyncio.sleep(2)
    
    async def error(self, error_text: str):
        """Показать ошибку"""
        try:
            await self.message.edit_text(
                f"❌ <b>Ошибка при обновлении</b>\n"
                f"⚠️ {error_text}\n\n"
                f"🔄 Попробуйте позже"
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                raise e