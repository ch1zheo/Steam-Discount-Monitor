# Главный скрипт. 

# Логика:
# 1. Собираем текущие скидки по всем регионам (RU/UA/KZ).
# 2. Отбираем те, что >= MIN_DISCOUNT_PERCENT.
# 3. Группируем по appid и ищем арбитраж — разницу цены одной и той же
#   игры между регионами (в USD, чтобы валюты были сопоставимы).
# 4. Отправляем уведомления в Telegram по новым находкам, сверяясь
#   с state.json, чтобы не дублировать сообщения при каждом запуске.
# 5. Повторяем каждые CHECK_INTERVAL_SECONDS секунд.

import sys
import time
import config
from currency import to_usd
from steam_api import fetch_discounted_games
from telegram_notifier import send_message
from storage import load_state, save_state, get_discount, set_discount, remove_discount, should_notify

def collect_all_regions() -> dict:
    """Возвращает {appid: {region_code: game_info}} по всем регионам."""
    by_appid = {}
    for cc, meta in config.REGIONS.items():
        print(f"[main] Проверяю регион {cc}...")
        games = fetch_discounted_games(
            cc=cc,
            lang=meta["lang"],
            page_size=config.PAGE_SIZE,
            max_pages=config.MAX_PAGES_PER_REGION,
        )
        for g in games:
            g["currency"] = meta["currency"]
            by_appid.setdefault(g["appid"], {})[cc] = g
        print(f"[main] Регион {cc}: найдено {len(games)} игр со скидкой")
    return by_appid

def build_notifications(by_appid: dict, state: dict) -> list:
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
            arbitrage_text = check_arbitrage(regions_data, state, appid_key)
            if arbitrage_text:
                msg += f"\n\n{arbitrage_text}"

            messages.append(msg)

        # Обновляем state (сохраняем все текущие скидки)
        for cc, discount in current_regions.items():
            set_discount(state, appid_key, cc, discount, name)

        # Удаляем скидки, которых больше нет
        saved_regions = state.get(str(appid_key), {}).get("regions", {})
        for cc in list(saved_regions.keys()):
            if cc not in current_regions:
                remove_discount(state, appid_key, cc)

    return messages

def check_arbitrage(regions_data: dict, state: dict, appid_key: str) -> str | None:
    """Проверяет арбитраж и возвращает текст уведомления."""
    prices_usd = {}
    for cc, g in regions_data.items():
        usd = to_usd(g["final_price"], g["currency"])
        if usd is not None:
            prices_usd[cc] = usd

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

    name = regions_data[cheapest_cc]["name"]
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

def run_once():
    state = load_state()
    by_appid = collect_all_regions()
    messages = build_notifications(by_appid, state)

    if not messages:
        print("[main] Новых скидок не найдено.")
    else:
        print(f"[main] Найдено {len(messages)} уведомлений, отправляю в Telegram...")
        for msg in messages:
            # Отправка в бота
            send_message(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID, msg)
            time.sleep(1)

    save_state(state)

def main():
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[main] ОШИБКА: не заданы TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID в .env")
        sys.exit(1)

    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[main] Непредвиденная ошибка: {e}")
        print(f"[main] Жду {config.CHECK_INTERVAL_SECONDS} сек. до следующей проверки...")
        time.sleep(config.CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
