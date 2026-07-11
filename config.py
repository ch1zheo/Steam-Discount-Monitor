# Конфигурация Steam Discount Monitor.

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Регионы для мониторинга и арбитража цен
REGIONS = {
    "ru": {"currency": "RUB", "lang": "russian"},
    "ua": {"currency": "UAH", "lang": "ukrainian"},
    "kz": {"currency": "KZT", "lang": "russian"},
}

# Уведомлять только если скидка на игру больше этого значения (%)
MIN_DISCOUNT_PERCENT = 1

# Уведомлять об арбитраже, если разница цены между самым дешёвым
# и самым дорогим регионом (в USD) больше этого значения (%)
MIN_ARBITRAGE_PERCENT = 1

# Сколько страниц (по PAGE_SIZE игр) максимум проверять за проход по региону
MAX_PAGES_PER_REGION = 5
PAGE_SIZE = 100

# Интервал между проверками, секунды
CHECK_INTERVAL_SECONDS = 7200

# Файл, где хранится история уведомлений (чтобы не дублировать)
STATE_FILE = "state.json"