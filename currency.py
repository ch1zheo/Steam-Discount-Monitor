import time
import asyncio
from typing import Optional, Dict

import aiohttp

_CACHE = {"rates": None, "ts": 0.0}
_cache_lock = asyncio.Lock()
CACHE_TTL = 6 * 60 * 60

RATES_URL = "https://open.er-api.com/v6/latest/USD"

async def get_rates_to_usd(session: aiohttp.ClientSession) -> Dict[str, float]:
    now = time.time()
    if _CACHE["rates"] and now - _CACHE["ts"] < CACHE_TTL:
        return _CACHE["rates"]

    async with _cache_lock:
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