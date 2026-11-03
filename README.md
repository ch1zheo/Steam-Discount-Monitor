# Steam Discount Monitor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.2.1-informational.svg)](CHANGELOG.md)
[![Telegram: aiogram 3](https://img.shields.io/badge/Telegram-aiogram%203-2CA5E0.svg)](https://docs.aiogram.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<details>
<summary>🇬🇧 English</summary>

A bot that tracks Steam discounts in several regions at once (RU / UA / KZ), finds new or changed discounts, and looks for **arbitrage** — cases where the same game costs different amounts in different regions by more than a set threshold. Everything it finds is sent to Telegram.

## How it works

1. **Collecting data.** Every `CHECK_INTERVAL_SECONDS` seconds (2 hours by default) the bot queries the Steam Store search endpoint for the `ru`, `ua` and `kz` regions in parallel and collects discounted games page by page (up to `MAX_PAGES_PER_REGION` pages per region).

2. **Filtering.** Only discounts of at least `MIN_DISCOUNT_PERCENT` % are kept.

3. **Newness check.** Every discount is compared against `state.json`, a file that keeps the history of the latest notifications. If a discount for this game in this region has already been sent and has not changed, no duplicate notification is sent.

4. **Arbitrage detection.** For games that have a price in more than one region, prices are converted to USD (via open.er-api.com rates) and compared. If the difference between the cheapest and the most expensive region exceeds `MIN_ARBITRAGE_PERCENT` %, a separate "💰 Arbitrage" block is added to the notification.

5. **Sending to Telegram.** Ready messages are sent to the chat one by one with a 1-second pause between them (Telegram allows roughly one message per second per chat).

6. **Saving state.** After every pass `state.json` is rewritten, so the bot remembers what it has already sent and does not send duplicates on the next run.

7. The loop repeats forever until the process is stopped.

## Structure

```text
Steam Discount Monitor/
├── main.py                    # Entry point: main loop, building notifications, running the bot
├── steam_api.py               # Steam Store requests and search HTML parsing
├── currency.py                # Exchange rates and conversion to USD
├── telegram_notifier.py       # Telegram delivery via aiogram
├── storage.py                 # Reading/writing state.json (notification history)
├── config.py                  # Settings: regions, thresholds, intervals, .env
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template (copy to .env)
├── README.md                  # This file (English and Russian)
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guide
├── LICENSE                    # MIT license
├── .editorconfig              # Editor settings (UTF-8, 4 spaces, LF)
├── .gitattributes             # Line ending normalization
├── .gitignore                 # Files that must not be committed
├── .github/workflows/
│   └── ci.yml                 # Syntax and import check on every push
└── state.json                 # Created automatically after the first run
```

## Installation

The project needs **Python 3.10 or newer**.

Do not forget to activate the **virtual environment** in the project folder before running! (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Linux and macOS)

### Windows

1. Download and install Python from [python.org](https://www.python.org/downloads/) — make sure to tick **"Add python.exe to PATH"** during installation.

2. Open PowerShell or CMD in the project folder and create a virtual environment:

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root (see the `.env` setup section).

5. Start the bot:

   ```powershell
   python main.py
   ```

### Linux (Ubuntu, Debian based)

1. Install Python and pip if they are not there yet:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```

2. Go to the project folder and create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root (see the `.env` setup section).

5. Start the bot:

   ```bash
   python3 main.py
   ```

   - To keep the bot running after the terminal is closed, start it via `nohup`, `tmux`/`screen`, or set it up as a systemd service.

### macOS

1. Install Python (if missing) via [Homebrew](https://brew.sh/):

   ```bash
   brew install python
   ```

2. Go to the project folder and create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root (see the `.env` setup section).

5. Start the bot:

   ```bash
   python3 main.py
   ```

## `.env` setup

Create a `.env` file in the project root (based on `.env.example`) with the following variables:

```dotenv
TELEGRAM_BOT_TOKEN=BOT_TOKEN
TELEGRAM_CHAT_ID=CHAT_ID
```

- **`TELEGRAM_BOT_TOKEN`** — the token of your bot, get it from [@BotFather](https://t.me/BotFather) with the `/newbot` command.
- **`TELEGRAM_CHAT_ID`** — the numeric ID of a channel or chat. If the bot has already been added to the channel as an administrator, the ID can be found, for example, via `@userinfobot` or through the `getUpdates` method of the Telegram Bot API.

Without these two variables the bot will not start and will print an error to the console.

## Monitoring settings

All settings live in `config.py`:

- `REGIONS` — which Steam regions to monitor (RU, UA, KZ by default).
- `MIN_DISCOUNT_PERCENT` — the minimum discount percentage for the bot to react.
- `MIN_ARBITRAGE_PERCENT` — the minimum price difference between regions to trigger an arbitrage signal.
- `MAX_PAGES_PER_REGION` / `PAGE_SIZE` — how many pages and how many games per page to check for one region.
- `CHECK_INTERVAL_SECONDS` — how often to repeat the check (7200 seconds = 2 hours by default).

## Important note

Steam does not provide an official API for this functionality — the bot parses the public search page (`store.steampowered.com/search`). If Valve changes the page layout, parsing may stop finding games; in that case check and update the CSS selectors in `steam_api.py`, in the `_parse_results_html` function.

## Contributing

Found a bug or want to suggest a feature? Open an [issue](../../issues) or read [CONTRIBUTING.md](CONTRIBUTING.md). Version history is in [CHANGELOG.md](CHANGELOG.md).

### 📜 License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.

Author — Ch1zheo

</details>

<details>
<summary>🇷🇺 Русский</summary>

Бот, который следит за скидками в Steam сразу в нескольких регионах (RU / UA / KZ), находит новые или изменившиеся скидки, а также ищет **арбитраж** — случаи, когда одна и та же игра в разных регионах стоит по-разному больше заданного порога. Обо всех находках бот пишет в Telegram.

## Как это работает

1. **Сбор данных.** Каждые `CHECK_INTERVAL_SECONDS` секунд (по умолчанию — раз в 2 часа) бот параллельно опрашивает поисковый эндпоинт Steam Store для регионов `ru`, `ua`, `kz` и собирает список игр со скидкой (постранично, до `MAX_PAGES_PER_REGION` страниц на регион).

2. **Фильтрация.** Из всех найденных скидок оставляются только те, что не меньше `MIN_DISCOUNT_PERCENT` %.

3. **Проверка на новизну.** Каждая скидка сверяется с `state.json` — файлом, в котором хранится история последних отправленных уведомлений. Если скидка на эту игру в этом регионе уже была отправлена и не изменилась — повторное уведомление не отправляется.

4. **Поиск арбитража.** Для игр, у которых есть цена в нескольких регионах, цены переводятся в USD (через курсы open.er-api.com) и сравниваются. Если разница между самым дешёвым и самым дорогим регионом превышает `MIN_ARBITRAGE_PERCENT` % — добавляется отдельный блок «💰 Арбитраж» в уведомление.

5. **Отправка в Telegram.** Готовые сообщения отправляются в чат по одному, с паузой в 1 секунду между сообщениями (ограничение Telegram — не более ~1 сообщения в секунду в один и тот же чат).

6. **Сохранение состояния.** После каждого прохода `state.json` перезаписывается — так бот «запоминает», что уже отправлял, и не дублирует уведомления при следующем запуске.

7. Цикл повторяется бесконечно, пока процесс не остановлен.

## Структура

```text
Steam Discount Monitor/
├── main.py                    # Точка входа: главный цикл, сбор уведомлений, запуск бота
├── steam_api.py               # Запросы к Steam Store и парсинг HTML-результатов поиска
├── currency.py                # Получение курсов валют и конвертация цен в USD
├── telegram_notifier.py       # Отправка сообщений в Telegram через aiogram
├── storage.py                 # Чтение/запись state.json (история уведомлений)
├── config.py                  # Конфигурация: регионы, пороги, интервалы, .env
├── requirements.txt           # Список зависимостей Python
├── .env.example               # Образец переменных окружения (копируется в .env)
├── README.md                  # Этот файл (английский и русский)
├── CHANGELOG.md               # История версий
├── CONTRIBUTING.md            # Гайд для контрибьюторов
├── LICENSE                    # Лицензия MIT
├── .editorconfig              # Настройки редактора (UTF-8, 4 пробела, LF)
├── .gitattributes             # Нормализация переводов строк
├── .gitignore                 # Файлы, которые не попадают в репозиторий
├── .github/workflows/
│   └── ci.yml                 # Проверка синтаксиса и импортов на каждый push
└── state.json                 # Создаётся автоматически после первого прогона
```

## Установка

Проекту нужен **Python 3.10 или новее**.

Не забывайте перед запуском активировать **окружение** в папке с проектом! (`venv\Scripts\activate` для Windows, `source venv/bin/activate` для Linux и macOS)

### Windows

1. Скачайте и установите Python с [python.org](https://www.python.org/downloads/) — при установке обязательно поставьте галочку **"Add python.exe to PATH"**.

2. Откройте PowerShell или CMD в папке проекта и создайте виртуальное окружение:

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Установите зависимости:

   ```powershell
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта (см. раздел «Настройка `.env`»).

5. Запустите бота:

   ```powershell
   python main.py
   ```

### Linux (Ubuntu, Debian Based)

1. Установите Python и pip, если их ещё нет:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```

2. Перейдите в папку проекта и создайте виртуальное окружение:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта (см. раздел «Настройка `.env`»).

5. Запустите бота:

   ```bash
   python3 main.py
   ```

   - Чтобы бот продолжал работать после закрытия терминала, можно запустить его через `nohup`, `tmux`/`screen` или оформить как systemd-сервис.

### macOS

1. Установите Python (если его нет) через [Homebrew](https://brew.sh/):

   ```bash
   brew install python
   ```

2. Перейдите в папку проекта и создайте виртуальное окружение:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта (см. раздел «Настройка `.env`»).

5. Запустите бота:

   ```bash
   python3 main.py
   ```

## Настройка `.env`

Создайте в корне проекта файл `.env` (по образцу `.env.example`) со следующими переменными:

```dotenv
TELEGRAM_BOT_TOKEN=BOT_TOKEN
TELEGRAM_CHAT_ID=CHAT_ID
```

- **`TELEGRAM_BOT_TOKEN`** — токен вашего бота, получить у [@BotFather](https://t.me/BotFather) командой `/newbot`.
- **`TELEGRAM_CHAT_ID`** — числовой ID канала или чата. Если бот уже добавлен в канал как администратор, узнать ID можно, например, через `@userinfobot` или через метод `getUpdates` Telegram Bot API.

Без этих двух переменных бот не запустится и выведет ошибку в консоль.

## Настройка параметров мониторинга

Все параметры находятся в `config.py`:

- `REGIONS` — какие регионы Steam мониторить (по умолчанию RU, UA, KZ).
- `MIN_DISCOUNT_PERCENT` — минимальный процент скидки, чтобы бот на неё среагировал.
- `MIN_ARBITRAGE_PERCENT` — минимальная разница цен между регионами для сигнала об арбитраже.
- `MAX_PAGES_PER_REGION` / `PAGE_SIZE` — сколько страниц и игр на странице проверять за один регион.
- `CHECK_INTERVAL_SECONDS` — как часто повторять проверку (по умолчанию 7200 сек = 2 часа).

## Важное замечание

Steam не предоставляет официального API для этого функционала — используется парсинг публичной страницы поиска (`store.steampowered.com/search`). Если Valve изменит вёрстку страницы, парсинг может перестать находить игры — в этом случае нужно проверить и обновить CSS-селекторы в файле `steam_api.py`, в функции `_parse_results_html`.

## Участие в разработке

Нашли баг или есть идея? Откройте [issue](../../issues) или прочитайте [CONTRIBUTING.md](CONTRIBUTING.md). История версий — в [CHANGELOG.md](CHANGELOG.md).

### 📜 Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).

Автор — Ch1zheo

</details>
