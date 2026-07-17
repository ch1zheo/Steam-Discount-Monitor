# Получение данных о скидках Steam по разным регионам.

import re
import asyncio
from typing import List, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup

SEARCH_URL = "https://store.steampowered.com/search/results/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://store.steampowered.com/search/?specials=1",
}

async def fetch_discounted_games(session: aiohttp.ClientSession, cc: str, lang: str = "russian",
                                  page_size: int = 100, max_pages: int = 5,
                                  request_delay: float = 1.0) -> List[Dict]:
    """ Возвращает список игр со скидкой для региона cc (например 'ru', 'ua', 'kz').
    Каждый элемент:
    {
        "appid": int,
        "name": str,
        "discount_percent": int,
        "original_price": float | None,
        "final_price": float | None,
        "region": str,
    } """
    games = []
    seen_appids = set()

    for page in range(max_pages):
        start = page * page_size
        params = {
            "query": "",
            "start": start,
            "count": page_size,
            "dynamic_data": "",
            "sort_by": "_ASC",
            "specials": 1,
            "cc": cc,
            "l": lang,
            "infinite": 1,
        }
        try:
            async with session.get(
                SEARCH_URL, params=params, headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                resp.raise_for_status()
                # content_type=None - Steam иногда отдаёт JSON с "неправильным" Content-Type,
                # без этого aiohttp кинет ContentTypeError вместо парсинга
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
            print(f"[steam_api] Ошибка запроса region={cc}, start={start}: {e}")
            break

        html = data.get("results_html", "")
        if not html or "search_result_row" not in html:
            print(f"[steam_api] Регион {cc}: пустой ответ или нет результатов")
            break

        parsed = _parse_results_html(html, cc)
        new_items = [g for g in parsed if g["appid"] not in seen_appids]
        if not new_items:
            break

        for g in new_items:
            seen_appids.add(g["appid"])
        games.extend(new_items)

        if len(parsed) < page_size:
            break

        await asyncio.sleep(request_delay)

    return games

def _parse_results_html(html: str, cc: str) -> List[Dict]:
    """Парсит HTML-фрагмент результатов поиска Steam."""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("a.search_result_row")
    results = []

    for row in rows:
        appid_raw = row.get("data-ds-appid")
        if not appid_raw:
            continue

        appid_str = appid_raw.split(",")[0].strip()
        try:
            appid = int(appid_str)
        except ValueError:
            continue

        title_el = row.select_one(".title")
        if not title_el:
            continue
        name = title_el.get_text(strip=True)

        discount_el = row.select_one(".discount_pct")
        if not discount_el:
            discount_el = row.select_one(".search_discount span")
        discount_percent = 0
        if discount_el:
            match = re.search(r"-?(\d+)%", discount_el.get_text(strip=True))
            if match:
                discount_percent = int(match.group(1))

        price_el = row.select_one(".discount_final_price")
        orig_price_el = row.select_one(".discount_original_price")

        final_price = _price_to_float(price_el) if price_el else None
        original_price = _price_to_float(orig_price_el) if orig_price_el else None

        if final_price is None:
            price_el2 = row.select_one(".search_price")
            if price_el2:
                final_price = _price_to_float(price_el2)

        if final_price is None or discount_percent == 0:
            continue

        results.append({
            "appid": appid,
            "name": name,
            "discount_percent": discount_percent,
            "original_price": original_price,
            "final_price": final_price,
            "region": cc,
        })

    return results

def _price_to_float(price_el) -> Optional[float]:
    """Извлекает число из элемента с ценой."""
    if price_el is None:
        return None
    text = price_el.get_text(strip=True)
    cleaned = re.sub(r"[^\d,.\s]", "", text)
    cleaned = cleaned.replace(" ", "").replace(",", ".")
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = parts[0] + "." + "".join(parts[1:])
    try:
        return float(cleaned)
    except ValueError:
        return None
