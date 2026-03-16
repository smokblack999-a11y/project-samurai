from flask import Flask, jsonify, request

from src.config import Config
from src.utils import now_str
from src.storage import (
    ensure_storage_file,
    load_storage,
    add_item,
    get_item_by_id,
    update_item,
    delete_item,
)
from src.logger import log_info, log_error

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "app": Config.APP_NAME,
        "env": Config.APP_ENV,
        "time": now_str(),
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "debug": Config.DEBUG,
    })


@app.get("/info")
def info():
    data = load_storage()
    items = data.get("items", [])

    return jsonify({
        "ok": True,
        "app": Config.APP_NAME,
        "env": Config.APP_ENV,
        "debug": Config.DEBUG,
        "host": Config.API_HOST,
        "port": Config.API_PORT,
        "storage_file": Config.STORAGE_FILE,
        "log_file": Config.APP_LOG_FILE,
        "items_count": len(items),
        "time": now_str(),
    })


@app.get("/data")
def get_data():
    ensure_storage_file()
    return jsonify(load_storage())


@app.post("/data")
def post_data():
    ensure_storage_file()
    payload = request.get_json(silent=True) or {}

    item = add_item(payload=payload, created_at=now_str())

    return jsonify({
        "ok": True,
        "item": item,
    }), 201


@app.get("/data/<int:item_id>")
def get_data_item(item_id: int):
    ensure_storage_file()
    item = get_item_by_id(item_id)

    if not item:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "item": item,
    })


@app.put("/data/<int:item_id>")
def put_data_item(item_id: int):
    ensure_storage_file()
    payload = request.get_json(silent=True) or {}

    item = update_item(
        item_id=item_id,
        payload=payload,
        updated_at=now_str(),
    )

    if not item:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "item": item,
    })


@app.delete("/data/<int:item_id>")
def delete_data_item(item_id: int):
    ensure_storage_file()
    deleted = delete_item(item_id)

    if not deleted:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "deleted": deleted,
    })


def run_api() -> None:
    ensure_storage_file()
    log_info(f"Storage file: {Config.STORAGE_FILE}")
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    try:
        run_api()
    except Exception as e:
        log_error(f"API crashed: {e}")
        raise
from flask import Flask, jsonify, request

from src.config import Config
from src.utils import now_str
from src.storage import (
    ensure_storage_file,
    load_storage,
    add_item,
    get_item_by_id,
    update_item,
    delete_item,
)
from src.logger import log_info, log_error

app = Flask(__name__)


def require_api_key() -> bool:
    provided = request.headers.get("X-API-Key", "")
    return provided == Config.API_KEY


@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "app": Config.APP_NAME,
        "env": Config.APP_ENV,
        "time": now_str(),
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "debug": Config.DEBUG,
    })


@app.get("/info")
def info():
    data = load_storage()
    items = data.get("items", [])

    return jsonify({
        "ok": True,
        "app": Config.APP_NAME,
        "env": Config.APP_ENV,
        "debug": Config.DEBUG,
        "items_count": len(items),
        "time": now_str(),
    })


@app.get("/admin/info")
def admin_info():
    if not require_api_key():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = load_storage()
    items = data.get("items", [])

    return jsonify({
        "ok": True,
        "app": Config.APP_NAME,
        "env": Config.APP_ENV,
        "host": Config.API_HOST,
        "port": Config.API_PORT,
        "storage_file": Config.STORAGE_FILE,
        "log_file": Config.APP_LOG_FILE,
        "telegram_enabled": bool(Config.TELEGRAM_BOT_TOKEN),
        "items_count": len(items),
        "time": now_str(),
    })


@app.get("/data")
def get_data():
    ensure_storage_file()
    return jsonify(load_storage())


@app.post("/data")
def post_data():
    ensure_storage_file()
    payload = request.get_json(silent=True) or {}

    item = add_item(payload=payload, created_at=now_str())

    return jsonify({
        "ok": True,
        "item": item,
    }), 201


@app.get("/data/<int:item_id>")
def get_data_item(item_id: int):
    ensure_storage_file()
    item = get_item_by_id(item_id)

    if not item:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "item": item,
    })


@app.put("/data/<int:item_id>")
def put_data_item(item_id: int):
    ensure_storage_file()
    payload = request.get_json(silent=True) or {}

    item = update_item(
        item_id=item_id,
        payload=payload,
        updated_at=now_str(),
    )

    if not item:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "item": item,
    })


@app.delete("/data/<int:item_id>")
def delete_data_item(item_id: int):
    ensure_storage_file()
    deleted = delete_item(item_id)

    if not deleted:
        return jsonify({
            "ok": False,
            "error": "Item not found",
            "id": item_id,
        }), 404

    return jsonify({
        "ok": True,
        "deleted": deleted,
    })


def run_api() -> None:
    ensure_storage_file()
    log_info(f"Starting API on {Config.API_HOST}:{Config.API_PORT}")
    log_info(f"Storage file: {Config.STORAGE_FILE}")
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    try:
        run_api()
    except Exception as e:
        log_error(f"API crashed: {e}")
        raise
