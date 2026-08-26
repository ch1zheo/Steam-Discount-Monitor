import json
import os
import time
from typing import Optional, Union

STATE_FILE = "state.json"

def load_state(path: str = STATE_FILE) -> dict:
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            print(f"[storage] Ошибка: данные в {path} не являются словарём. Сбрасываю...")
            return {}

        cleaned = {}
        for key, value in data.items():
            try:
                str_key = str(key)
                if isinstance(value, dict):
                    inner = {}
                    for inner_key, inner_value in value.items():
                        inner[str(inner_key)] = inner_value
                    cleaned[str_key] = inner
                else:
                    cleaned[str_key] = value
            except Exception:
                continue

        return cleaned

    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        print(f"[storage] Ошибка загрузки {path}: {e}. Создаю новый файл...")
        return {}

def save_state(state: dict, path: str = STATE_FILE) -> None:
    cleaned = {}
    for key, value in state.items():
        try:
            str_key = str(key)
            if isinstance(value, dict):
                inner = {}
                for inner_key, inner_value in value.items():
                    inner[str(inner_key)] = inner_value
                cleaned[str_key] = inner
            else:
                cleaned[str_key] = value
        except Exception:
            continue

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

def get_discount(state: dict, appid: Union[int, str], region: str) -> Optional[int]:
    appid_key = str(appid)
    if appid_key not in state:
        return None
    regions = state[appid_key].get("regions")
    if not isinstance(regions, dict):
        return None
    return regions.get(region)

def set_discount(state: dict, appid: Union[int, str], region: str, discount: int, name: str = "") -> None:
    appid_key = str(appid)
    if appid_key not in state:
        state[appid_key] = {
            "name": name,
            "regions": {},
            "last_seen": int(time.time())
        }
    state[appid_key]["regions"][region] = discount
    state[appid_key]["last_seen"] = int(time.time())
    if name:
        state[appid_key]["name"] = name

def remove_discount(state: dict, appid: Union[int, str], region: str) -> None:
    appid_key = str(appid)
    if appid_key not in state:
        return
    regions = state[appid_key].get("regions")
    if not isinstance(regions, dict):
        return
    if region in regions:
        del regions[region]
    if not state[appid_key].get("regions"):
        del state[appid_key]

def should_notify(state: dict, appid: Union[int, str], region: str, discount: int) -> bool:
    appid_key = str(appid)
    if appid_key not in state:
        return True

    regions = state[appid_key].get("regions")
    if not isinstance(regions, dict):
        return True

    saved = regions.get(region)
    if saved is None:
        return True

    return saved != discount