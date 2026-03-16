from flask import Flask, jsonify, request, render_template_string, redirect

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


PANEL_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Samurai Panel</title>
    <style>
        body { font-family: Arial, sans-serif; background:#111; color:#eee; margin:20px; }
        h1, h2, h3 { color:#7ee787; }
        .box { background:#1b1b1b; padding:16px; border-radius:12px; margin-bottom:16px; }
        input, button { padding:10px; border-radius:8px; border:none; margin:4px 0; }
        input { width:100%; background:#222; color:#fff; }
        button { background:#2ea043; color:white; cursor:pointer; }
        .danger { background:#da3633; }
        .item { border:1px solid #333; border-radius:12px; padding:12px; margin-bottom:12px; }
        pre { background:#000; padding:12px; border-radius:8px; overflow:auto; }
        form { margin-top:8px; }
    </style>
</head>
<body>
    <h1>Samurai Panel</h1>

    <div class="box">
        <h2>System Info</h2>
        <p><b>App:</b> {{ app_name }}</p>
        <p><b>Env:</b> {{ env }}</p>
        <p><b>Items count:</b> {{ items_count }}</p>
        <p><b>Time:</b> {{ time }}</p>
    </div>

    <div class="box">
        <h2>Add Item</h2>
        <form method="post" action="/panel/add">
            <input type="text" name="name" placeholder="Name" required>
            <input type="text" name="type" placeholder="Type" required>
            <button type="submit">Add</button>
        </form>
    </div>

    <div class="box">
        <h2>Items</h2>
        {% for item in items %}
            <div class="item">
                <h3>ID {{ item["id"] }}</h3>
                <p><b>Created:</b> {{ item["created_at"] }}</p>
                {% if item.get("updated_at") %}
                    <p><b>Updated:</b> {{ item["updated_at"] }}</p>
                {% endif %}
                <pre>{{ item }}</pre>

                <form method="post" action="/panel/edit/{{ item['id'] }}">
                    <input type="text" name="name" value="{{ item['payload'].get('name', '') }}" required>
                    <input type="text" name="type" value="{{ item['payload'].get('type', '') }}" required>
                    <button type="submit">Update</button>
                </form>

                <form method="post" action="/panel/delete/{{ item['id'] }}">
                    <button type="submit" class="danger">Delete</button>
                </form>
            </div>
        {% else %}
            <p>No items yet.</p>
        {% endfor %}
    </div>
</body>
</html>
"""


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
    return jsonify({"ok": True, "item": item}), 201


@app.get("/data/<int:item_id>")
def get_data_item(item_id: int):
    ensure_storage_file()
    item = get_item_by_id(item_id)

    if not item:
        return jsonify({"ok": False, "error": "Item not found", "id": item_id}), 404

    return jsonify({"ok": True, "item": item})


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
        return jsonify({"ok": False, "error": "Item not found", "id": item_id}), 404

    return jsonify({"ok": True, "item": item})


@app.delete("/data/<int:item_id>")
def delete_data_item(item_id: int):
    ensure_storage_file()
    deleted = delete_item(item_id)

    if not deleted:
        return jsonify({"ok": False, "error": "Item not found", "id": item_id}), 404

    return jsonify({"ok": True, "deleted": deleted})


@app.get("/panel")
def panel():
    ensure_storage_file()
    data = load_storage()
    items = data.get("items", [])

    return render_template_string(
        PANEL_HTML,
        app_name=Config.APP_NAME,
        env=Config.APP_ENV,
        items_count=len(items),
        items=items,
        time=now_str(),
    )


@app.post("/panel/add")
def panel_add():
    name = request.form.get("name", "").strip()
    item_type = request.form.get("type", "").strip()

    if name and item_type:
        add_item(
            payload={"name": name, "type": item_type},
            created_at=now_str(),
        )

    return redirect("/panel")


@app.post("/panel/edit/<int:item_id>")
def panel_edit(item_id: int):
    name = request.form.get("name", "").strip()
    item_type = request.form.get("type", "").strip()

    if name and item_type:
        update_item(
            item_id=item_id,
            payload={"name": name, "type": item_type},
            updated_at=now_str(),
        )

    return redirect("/panel")


@app.post("/panel/delete/<int:item_id>")
def panel_delete(item_id: int):
    delete_item(item_id)
    return redirect("/panel")


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
