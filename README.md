# Steam-Discount-Monitor

Steam Discount Monitor - это код для Telegram бота, который при запуске парсит цены Steam'а и выводит информацию об арбитраже и скидках.
Steam Discount Monitor is code for a Telegram bot that, when launched, scrapes Steam prices and provides information on arbitrage opportunities and discounts.

# Russian:

Бот мониторит скидки в Steam по трём регионам (RU/UA/KZ) и присылает
уведомления в Telegram:

1. Обычные скидки - если скидка на игру больше `MIN_DISCOUNT_PERCENT`(Регулируется).
2. Арбитраж - если одна и та же игра стоит заметно дешевле в одном
   регионе, чем в другом (сравнение в USD по текущему курсу).

/ Установка библиотек

pip install -r requirements.txt

/ Настройка Telegram

1. Напишите @BotFather в Telegram -> `/newbot` -> следуйте инструкциям -> получите токен.
2 Узнайте свой `chat_id`:
   - напишите что-нибудь своему новому боту,
   - откройте `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`,
   - найдите `"chat":{"id": ...}` в ответе.
3. Скопируйте `.env.example` в `.env` и впишите значения:

TELEGRAM_BOT_TOKEN="ТОКЕН БОТА"
TELEGRAM_CHAT_ID="ЧАТ АЙДИ ПОЛЬЗОВАТЕЛЯ"

/ Запуск

python main.py

Скрипт работает в бесконечном цикле и проверяет цены каждые
`CHECK_INTERVAL_SECONDS` (по умолчанию раз в 2 часа). Для постоянной
работы разверните на сервере/VPS через `systemd` или `screen`/`tmux`,
либо через `pm2`/`supervisor`. Эта версия без встроенного прокси так что используйте VPN.

/ Настройка порогов

Всё в `config.py`:

- `REGIONS` - какие регионы мониторить и в какой валюте у них цены.
- `MIN_DISCOUNT_PERCENT` - от какой скидки присылать уведомление.
- `MIN_ARBITRAGE_PERCENT` - от какой разницы цен между регионами присылать уведомление.
- `MAX_PAGES_PER_REGION` / `PAGE_SIZE` - сколько игр максимум просматривать за проход.
- `CHECK_INTERVAL_SECONDS` - как часто проверять.

/ Как это устроено

- `steam_api.py` - забирает список игр со скидкой из поиска Steam Store
  (неофициальный эндпоинт, но отдаёт полный список, а не только "витрину").
- `currency.py` - конвертирует цены в USD для честного сравнения регионов.
- `storage.py` - хранит `state.json`, чтобы не слать повторные уведомления.
- `telegram_notifier.py` - отправка сообщений через Bot API.
- `main.py` - связывает всё вместе и крутит бесконечный цикл проверки.

/ Важно

- Это неофициальный способ получения данных (парсинг публичной страницы
  поиска Steam), у Valve нет официального API для списка всех скидок.
  Если Steam изменит вёрстку сайта, парсинг может сломаться - если это произойдет сообщите об этом создателю.
- Не ставьте `CHECK_INTERVAL_SECONDS` слишком маленьким и не убирайте
  задержки между запросами - иначе Steam может временно заблокировать IP.

# English:

The bot monitors discounts in Steam across three regions (RU/UA/KZ) and sends notifications to Telegram:

1. Regular discounts - if the discount on a game is greater than `MIN_DISCOUNT_PERCENT` (adjustable).
2. Arbitrage - if the same game is noticeably cheaper in one region than in another (compared in USD at the current exchange rate).

/ Installing libraries

pip install -r requirements.txt

/ Telegram setup

1. Write to @BotFather in Telegram -> `/newbot` -> follow the instructions -> get the token.
2. Find out your `chat_id`:
   - write something to your new bot,
   - open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`,
   - find `"chat":{"id": ...}` in the response.
3. Copy `.env.example` to `.env` and fill in the values:

TELEGRAM_BOT_TOKEN="BOT TOKEN"
TELEGRAM_CHAT_ID="USER CHAT ID"

/ Running

python main.py

The script runs in an infinite loop and checks prices every `CHECK_INTERVAL_SECONDS` (default: 2 hours). For permanent operation, deploy on a VPS via `systemd` or `screen`/`tmux`, or via `pm2`/`supervisor`. This version does not have a built-in proxy, so use a VPN.

/ Configuring thresholds

Everything is in `config.py`:

- `REGIONS` - which regions to monitor and in what currency their prices are.
- `MIN_DISCOUNT_PERCENT` - from which discount to send a notification.
- `MIN_ARBITRAGE_PERCENT` - from which price difference between regions to send a notification.
- `MAX_PAGES_PER_REGION` / `PAGE_SIZE` - how many games maximum to view per pass.
- `CHECK_INTERVAL_SECONDS` - how often to check.

/ How it works

- `steam_api.py` - fetches the list of discounted games from the Steam Store search (unofficial endpoint, but returns the full list, not just the "showcase").
- `currency.py` - converts prices to USD for fair comparison between regions.
- `storage.py` - stores `state.json` to avoid duplicate notifications.
- `telegram_notifier.py` - sends messages via the Bot API.
- `main.py` - ties everything together and runs the infinite check loop.

/ Important

- This is an unofficial way of obtaining data (parsing the public Steam search page), Valve does not have an official API for the list of all discounts. If Steam changes the page layout, the parser may break - if this happens, report it to the creator.
- Do not set `CHECK_INTERVAL_SECONDS` too low and do not remove delays between requests - otherwise Steam may temporarily block your IP.
