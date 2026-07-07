# Отправка уведомлений в Telegram через Bot API.

import requests
import time

API_URL = "https://api.telegram.org/bot{token}/sendMessage"

def send_message(token: str, chat_id: str, text: str) -> bool:
    """Отправляет сообщение в Telegram. Возвращает True при успехе."""
    url = API_URL.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[telegram] Ошибка отправки сообщения: {e}")
        return False