import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "Samurai Project")
    APP_ENV = os.getenv("APP_ENV", "dev")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Local-only by default. Set an explicit host only behind a trusted proxy/firewall.
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # No built-in credentials: protected routes fail closed until configured.
    API_KEY = os.getenv("API_KEY", "")
    PANEL_USERNAME = os.getenv("PANEL_USERNAME", "")
    PANEL_PASSWORD = os.getenv("PANEL_PASSWORD", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    BASE_DIR = os.getcwd()
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

    STORAGE_FILE = os.path.join(DATA_DIR, "storage.json")
    APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
