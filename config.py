import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

REGIONS = {
    "ru": {"currency": "RUB", "lang": "russian"},
    "ua": {"currency": "UAH", "lang": "ukrainian"},
    "kz": {"currency": "KZT", "lang": "russian"},
}

MIN_DISCOUNT_PERCENT = 1

MIN_ARBITRAGE_PERCENT = 1

MAX_PAGES_PER_REGION = 5
PAGE_SIZE = 100

CHECK_INTERVAL_SECONDS = 7200

STATE_FILE = "state.json"