# main.py - главный скрипт (асинхронная версия: aiogram + aiohttp).

import sys
import asyncio

import aiohttp
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

import config
from currency import to_usd
from steam_api import fetch_discounted_games
from telegram_notifier import send_message
from storage import load_state, save_state, set_discount, remove_discount, should_notify

async def collect_all_regions(session: aiohttp.ClientSession) -> dict:
    """Возвращает {appid: {region_code: game_info}} по всем регионам.
    Регионы опрашиваются ПАРАЛЛЕЛЬНО - раньше (RU -> UA -> KZ последовательно)
    общее время было суммой времён всех регионов, теперь - временем самого медленного."""
    regions_items = list(config.REGIONS.items())
    tasks = [
        fetch_discounted_games(
            session,
            cc=cc,
            lang=meta["lang"],
            page_size=config.PAGE_SIZE,
            max_pages=config.MAX_PAGES_PER_REGION,
        )
        for cc, meta in regions_items
    ]

    print(f"[main] Проверяю регионы ({', '.join(cc for cc, _ in regions_items)}) параллельно...")
    # return_exceptions=True - чтобы ошибка в одном регионе не обрушила остальные
    results = await asyncio.gather(*tasks, return_exceptions=True)

    by_appid = {}
    for (cc, meta), games in zip(regions_items, results):
        if isinstance(games, Exception):
            print(f"[main] Регион {cc}: ошибка при сборе данных: {games}")
            continue
        for g in games:
            g["currency"] = meta["currency"]
            by_appid.setdefault(g["appid"], {})[cc] = g
        print(f"[main] Регион {cc}: найдено {len(games)} игр со скидкой")

    return by_appid

async def build_notifications(by_appid: dict, state: dict, session: aiohttp.ClientSession) -> list:
    """Формирует уведомления только для НОВЫХ или ИЗМЕНИВШИХСЯ скидок."""
    messages = []

    for appid, regions_data in by_appid.items():
        appid_key = str(appid)
        name = regions_data[next(iter(regions_data))]["name"]

        # Собираем текущие скидки по регионам
        current_regions = {}
        for cc, g in regions_data.items():
            if g["discount_percent"] >= config.MIN_DISCOUNT_PERCENT:
                current_regions[cc] = g["discount_percent"]

        # Проверяем, какие скидки появились или изменились
        new_regions = {}
        for cc, discount in current_regions.items():
            if should_notify(state, appid_key, cc, discount):
                new_regions[cc] = discount

        # Формируем сообщение для новых / изменившихся скидок
        if new_regions:
            region_info = []
            for cc in ("ru", "ua", "kz"):
                if cc in regions_data:
                    g = regions_data[cc]

                    if g["discount_percent"] >= config.MIN_DISCOUNT_PERCENT:
                        region_info.append(
                            f" 💵 {cc.upper()}: -{g['discount_percent']}% -> "
                            f"{g['final_price']} {g['currency']} "
                            f"(Было {g['original_price']} {g['currency']})"
                        )
                    else:
                        if cc == "ru":
                            region_info.append(" • RU: Недоступно")
                        else:
                            region_info.append(f" • {cc.upper()}: Неизвестно")
                else:
                    if cc == "ru":
                        region_info.append(" • RU: Недоступна")
                    else:
                        region_info.append(f" • {cc.upper()}: Неизвестно")

            msg = f"<b> • {name}</b>\n" + "\n".join(region_info)

            # Проверяем арбитраж (если он есть)
            arbitrage_text = await check_arbitrage(regions_data, state, appid_key, session)
            if arbitrage_text:
                msg += f"\n\n{arbitrage_text}"

            messages.append(msg)

        # Обновляем state (сохраняем все текущие скидки)
        for cc, discount in current_regions.items():
            set_discount(state, appid_key, cc, discount, name)

        # Удаляем скидки, которых больше нет
        saved_regions = state.get(appid_key, {}).get("regions", {})
        for cc in list(saved_regions.keys()):
            if cc not in current_regions:
                remove_discount(state, appid_key, cc)

    return messages

async def check_arbitrage(regions_data: dict, state: dict, appid_key: str,
                           session: aiohttp.ClientSession) -> str | None:
    """Проверяет арбитраж и возвращает текст уведомления."""
    # Курсы валют для всех регионов игры запрашиваются параллельно
    ccs = list(regions_data.keys())
    usd_values = await asyncio.gather(*[
        to_usd(session, regions_data[cc]["final_price"], regions_data[cc]["currency"])
        for cc in ccs
    ])
    prices_usd = {cc: usd for cc, usd in zip(ccs, usd_values) if usd is not None}

    if len(prices_usd) < 2:
        return None

    cheapest_cc = min(prices_usd, key=prices_usd.get)
    priciest_cc = max(prices_usd, key=prices_usd.get)
    cheap_price = prices_usd[cheapest_cc]
    expensive_price = prices_usd[priciest_cc]

    if cheap_price <= 0:
        return None

    diff_percent = (expensive_price - cheap_price) / cheap_price * 100
    if diff_percent < config.MIN_ARBITRAGE_PERCENT:
        return None

    prev_arbitrage = state.get(appid_key, {}).get("arbitrage_percent")
    if prev_arbitrage is not None and abs(prev_arbitrage - diff_percent) <= 3:
        return None

    entry = state.setdefault(appid_key, {})
    entry.setdefault("regions", {})
    state[appid_key]["arbitrage_percent"] = diff_percent

    return (
        f"<b>💰 Арбитраж:</b>"
        f"\n📉 Дешевле всего в {cheapest_cc.upper()}"
        f"(~${cheap_price:.2f}), "
        f"\n📈 дороже в {priciest_cc.upper()}"
        f"(~${expensive_price:.2f})"
        f"\n⚖️ Разница: {diff_percent:.0f}%"
    )

async def run_once(session: aiohttp.ClientSession, bot: Bot):
    state = load_state()
    by_appid = await collect_all_regions(session)
    messages = await build_notifications(by_appid, state, session)

    if not messages:
        print("[main] Новых скидок не найдено.")
    else:
        print(f"[main] Найдено {len(messages)} уведомлений, отправляю в Telegram...")
        for msg in messages:
            await send_message(bot, config.TELEGRAM_CHAT_ID, msg)
            # Telegram ограничивает ~1 сообщение/сек в один и тот же чат - задержка обязательна,
            # иначе часть сообщений будет отклонена с ошибкой "Too Many Requests"
            await asyncio.sleep(1)

    save_state(state)

async def main():
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[main] ОШИБКА: не заданы TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID в .env")
        sys.exit(1)

    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    # Одна aiohttp-сессия на весь процесс: переиспользует TCP-соединения (keep-alive),
    # что заметно быстрее, чем создавать новую сессию на каждый запрос
    async with aiohttp.ClientSession() as session:
        try:
            while True:
                try:
                    await run_once(session, bot)
                except Exception as e:
                    print(f"[main] Непредвиденная ошибка: {e}")
                print(f"[main] Жду {config.CHECK_INTERVAL_SECONDS} сек. до следующей проверки...")
                await asyncio.sleep(config.CHECK_INTERVAL_SECONDS)
        finally:
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())