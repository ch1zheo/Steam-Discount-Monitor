# Конвертация валют для сравнения цен между регионами (RUB/UAH/KZT).
# Используется бесплатный API open.er-api.com (без ключа). Курсы кэшируются
# на CACHE_TTL секунд, чтобы не дёргать API на каждую проверку.
# Все запросы асинхронные (aiohttp), используют общую сессию из main.py -
# отдельную сессию на каждый запрос создавать нельзя, это сильно замедляет работу.

import time
import asyncio
from typing import Optional, Dict

import aiohttp

_CACHE = {"rates": None, "ts": 0.0}
_cache_lock = asyncio.Lock()  # защищает от гонки, если несколько задач одновременно просят курс
CACHE_TTL = 6 * 60 * 60  # обновлять курс раз в 6 часов

RATES_URL = "https://open.er-api.com/v6/latest/USD"

async def get_rates_to_usd(session: aiohttp.ClientSession) -> Dict[str, float]:
    """Возвращает {валюта: курс_к_доллару}, например {'RUB': 90.5, ...}."""
    now = time.time()
    if _CACHE["rates"] and now - _CACHE["ts"] < CACHE_TTL:
        return _CACHE["rates"]

    async with _cache_lock:
        # Повторная проверка внутри лока: пока мы ждали лок, курс мог уже обновить другой таск
        now = time.time()
        if _CACHE["rates"] and now - _CACHE["ts"] < CACHE_TTL:
            return _CACHE["rates"]

        async with session.get(RATES_URL, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

        rates = data.get("rates", {})
        _CACHE["rates"] = rates
        _CACHE["ts"] = now
        return rates

async def to_usd(session: aiohttp.ClientSession, amount: Optional[float], currency: str) -> Optional[float]:
    """Переводит сумму в USD, чтобы сравнивать цены между регионами."""
    if amount is None:
        return None
    try:
        rates = await get_rates_to_usd(session)
    except aiohttp.ClientError as e:
        print(f"[currency] Не удалось получить курсы валют: {e}")
        return None
    rate = rates.get(currency)
    if not rate:
        return None
    return amount / rate