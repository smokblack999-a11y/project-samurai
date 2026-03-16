import json
import os
from src.config import Config


def ensure_dirs():
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)


def ensure_storage_file():
    ensure_dirs()
    if not os.path.exists(Config.STORAGE_FILE):
        with open(Config.STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, ensure_ascii=False, indent=2)


def load_storage():
    ensure_storage_file()
    with open(Config.STORAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_storage(data):
    ensure_dirs()
    with open(Config.STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_items():
    data = load_storage()
    data.setdefault("items", [])
    return data["items"]


def next_item_id():
    items = get_items()
    if not items:
        return 1
    return max(item.get("id", 0) for item in items) + 1


def add_item(payload, created_at):
    data = load_storage()
    data.setdefault("items", [])

    item = {
        "id": next_item_id(),
        "payload": payload,
        "created_at": created_at,
    }

    data["items"].append(item)
    save_storage(data)
    return item


def get_item_by_id(item_id):
    for item in get_items():
        if item.get("id") == item_id:
            return item
    return None


def update_item(item_id, payload, updated_at):
    data = load_storage()
    data.setdefault("items", [])

    for item in data["items"]:
        if item.get("id") == item_id:
            item["payload"] = payload
            item["updated_at"] = updated_at
            save_storage(data)
            return item

    return None


def delete_item(item_id):
    data = load_storage()
    data.setdefault("items", [])

    for index, item in enumerate(data["items"]):
        if item.get("id") == item_id:
            deleted = data["items"].pop(index)
            save_storage(data)
            return deleted

    return None
