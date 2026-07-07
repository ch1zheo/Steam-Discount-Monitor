# Конвертация валют для сравнения цен между регионами (RUB/UAH/KZT). 
# Используется бесплатный API open.er-api.com (без ключа). Курсы кэшируются
# на CACHE_TTL секунд, чтобы не дёргать API на каждый запуск проверки.

import time
from typing import Optional, Dict

import requests

_CACHE = {"rates": None, "ts": 0.0}
CACHE_TTL = 6 * 60 * 60  # обновлять курс раз в 6 часов

RATES_URL = "https://open.er-api.com/v6/latest/USD"

def get_rates_to_usd() -> Dict[str, float]:
    """Возвращает {валюта: курс_к_доллару}, например {'RUB': 90.5, ...}."""
    now = time.time()
    if _CACHE["rates"] and now - _CACHE["ts"] < CACHE_TTL:
        return _CACHE["rates"]

    resp = requests.get(RATES_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    rates = data.get("rates", {})
    _CACHE["rates"] = rates
    _CACHE["ts"] = now
    return rates

def to_usd(amount: Optional[float], currency: str) -> Optional[float]:
    """Переводит сумму в USD, чтобы сравнивать цены между регионами."""
    if amount is None:
        return None
    try:
        rates = get_rates_to_usd()
    except requests.RequestException as e:
        print(f"[currency] Не удалось получить курсы валют: {e}")
        return None
    rate = rates.get(currency)
    if not rate:
        return None
    return amount / rate
