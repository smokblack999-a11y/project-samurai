import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "Samurai Project")
    APP_ENV = os.getenv("APP_ENV", "dev")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    BASE_DIR = os.getcwd()

    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

    STORAGE_FILE = os.path.join(DATA_DIR, "storage.json")
    APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "Samurai Project")
    APP_ENV = os.getenv("APP_ENV", "dev")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    API_KEY = os.getenv("API_KEY", "samurai-secret-key")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    BASE_DIR = os.getcwd()
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

    STORAGE_FILE = os.path.join(DATA_DIR, "storage.json")
    APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
