# Отправка уведомлений в Telegram через aiogram (асинхронно).
# parse_mode="HTML" задаётся один раз при создании Bot в main.py (DefaultBotProperties),
# поэтому здесь его указывать не нужно.

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

async def send_message(bot: Bot, chat_id: str, text: str) -> bool:
    """Отправляет сообщение в Telegram. Возвращает True при успехе."""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
        )
        return True
    except TelegramAPIError as e:
        print(f"[telegram] Ошибка отправки сообщения: {e}")
        return False