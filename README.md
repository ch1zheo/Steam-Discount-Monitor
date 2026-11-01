# Steam Discount Monitor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/ch1zheo/Steam-Discount-Monitor/graphs/commit-activity)
[![GitHub release](https://img.shields.io/github/v/release/ch1zheo/Steam-Discount-Monitor)](https://github.com/ch1zheo/Steam-Discount-Monitor/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Бот, который следит за скидками в Steam сразу в нескольких регионах (RU / UA / KZ), находит новые или изменившиеся скидки, а также ищет **арбитраж** - случаи, когда одна и та же игра в разных регионах стоит по-разному больше заданного порога. Обо всех находках бот пишет в Telegram.

## Как это работает

1. **Сбор данных.** Каждые `CHECK_INTERVAL_SECONDS` секунд (по умолчанию - раз в 2 часа) бот параллельно опрашивает поисковый эндпоинт Steam Store для регионов `ru`, `ua`, `kz` и собирает список игр со скидкой (постранично, до `MAX_PAGES_PER_REGION` страниц на регион).

2. **Фильтрация.** Из всех найденных скидок оставляются только те, что не меньше `MIN_DISCOUNT_PERCENT` %.

3. **Проверка на новизну.** Каждая скидка сверяется с `state.json` - файлом, в котором хранится история последних отправленных уведомлений. Если скидка на эту игру в этом регионе уже была отправлена и не изменилась - повторное уведомление не отправляется.

4. **Поиск арбитража.** Для игр, у которых есть цена в нескольких регионах, цены переводятся в USD (через курсы open.er-api.com) и сравниваются. Если разница между самым дешёвым и самым дорогим регионом превышает `MIN_ARBITRAGE_PERCENT` % - добавляется отдельный блок «💰 Арбитраж» в уведомление.

5. **Отправка в Telegram.** Готовые сообщения отправляются в чат по одному, с паузой в 1 секунду между сообщениями (ограничение Telegram - не более ~1 сообщения в секунду в один и тот же чат).

6. **Сохранение состояния.** После каждого прохода `state.json` перезаписывается - так бот "запоминает", что уже отправлял, и не дублирует уведомления при следующем запуске.

7. Цикл повторяется бесконечно, пока процесс не остановлен.

## Структура

Steam Discount Monitor/

├── main.py                 # Точка входа: главный цикл, сбор уведомлений, запуск бота

├── steam_api.py             # Запросы к Steam Store и парсинг HTML-результатов поиска

├── currency.py               # Получение курсов валют и конвертация цен в USD

├── telegram_notifier.py       # Отправка сообщений в Telegram через aiogram

├── storage.py                 # Чтение/запись state.json (история уведомлений)

├── config.py                   # Конфигурация: регионы, пороги, интервалы, .env

├── requirements.txt             # Список зависимостей Python

├── .env                          # Файл с секретами

└── state.json                     # Создаётся автоматически после первого прогона

## Установка

Проекту нужен **Python 3.10 или новее**.

Не забывайте перед запуском активировать **окружение** в папке с проектом! (venv\Scripts\activate для Windows, source venv/bin/activate для Linux, macOS)

### Windows

1. Скачайте и установите Python с [python.org](https://www.python.org/downloads/) - при установке обязательно поставьте галочку **"Add python.exe to PATH"**.

2. Откройте PowerShell или CMD в папке проекта и создайте виртуальное окружение:

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Установите зависимости:

   ```powershell
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта (см. раздел # Настройка `.env`).

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

4. Создайте файл `.env` в корне проекта (см. раздел # Настройка `.env`).

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

4. Создайте файл `.env` в корне проекта (см. раздел # Настройка `.env`).

5. Запустите бота:

   ```bash
   python3 main.py
   ```

## Настройка `.env`

Создайте в корне проекта файл `.env` (по образцу `default.env.example`) со следующими переменными:

- TELEGRAM_BOT_TOKEN=BOT_TOKEN - это токен вашего бота

- TELEGRAM_CHAT_ID=CHAT_ID - это ваш айди, он будет слать уведомления только вам

- **`TELEGRAM_BOT_TOKEN`** - получить у [@BotFather](https://t.me/BotFather) командой `/newbot`.

- **`TELEGRAM_CHAT_ID`** - числовой ID канала или чата. Если бот уже добавлен в канал
  как администратор, узнать ID можно, например, через `@userinfobot` или через
  `getUpdates` метод Telegram Bot API.

Без этих двух переменных бот не запустится и выведет ошибку в консоль.

## Настройка параметров мониторинга

Все параметры находятся в `config.py`:

- `REGIONS` - какие регионы Steam мониторить (по умолчанию RU, UA, KZ).

- `MIN_DISCOUNT_PERCENT` - минимальный процент скидки, чтобы бот на неё среагировал.

- `MIN_ARBITRAGE_PERCENT` - минимальная разница цен между регионами для сигнала об арбитраже.

- `MAX_PAGES_PER_REGION` / `PAGE_SIZE` - сколько страниц и игр на странице проверять за один регион.

- `CHECK_INTERVAL_SECONDS` - как часто повторять проверку (по умолчанию 7200 сек = 2 часа).

## Важное замечание

Steam не предоставляет официального API для этого функционала - используется
парсинг публичной страницы поиска (`store.steampowered.com/search`). Если Valve
изменит вёрстку страницы, парсинг может перестать находить игры - в этом случае
нужно проверить и обновить CSS-селекторы в файле `steam_api.py`, в функции
`_parse_results_html`.

## Важная информация

Если вы нашли баг, обязательно сообщите о нём автору!

### Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).

Автор - Ch1zheo
