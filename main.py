import sys

from src.config import Config
from src.logger import log_info, log_ok, log_error
from src.utils import now_str, banner, normalize_text
from src.commands import run_status, run_hello, run_help, run_show_data
from src.api import run_api
from src.storage import ensure_storage_file


def run_default() -> None:
    ensure_storage_file()
    log_info("Starting project...")
    log_ok(banner(Config.APP_NAME))
    log_info(f"Environment: {Config.APP_ENV}")
    log_info(f"Debug: {Config.DEBUG}")
    log_info(f"Time: {now_str()}")
    log_ok("Samurai base scaffold launched successfully.")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        run_default()
        return

    command = normalize_text(args[0])

    if command == "status":
        run_status()
    elif command == "hello":
        name = args[1] if len(args) > 1 else "Samurai"
        run_hello(name)
    elif command == "api":
        log_info(f"Starting API on {Config.API_HOST}:{Config.API_PORT}")
        run_api()
    elif command == "help":
        run_help()
    elif command == "show-data":
        run_show_data()
    else:
        log_error(f"Unknown command: {command}")
        run_help()


if __name__ == "__main__":
    main()
import sys

from src.config import Config
from src.logger import log_info, log_ok, log_error
from src.utils import now_str, banner, normalize_text
from src.commands import run_status, run_hello, run_help, run_show_data
from src.api import run_api
from src.storage import ensure_storage_file


def run_default() -> None:
    ensure_storage_file()
    log_info("Starting project...")
    log_ok(banner(Config.APP_NAME))
    log_info(f"Environment: {Config.APP_ENV}")
    log_info(f"Debug: {Config.DEBUG}")
    log_info(f"Time: {now_str()}")
    log_ok("Samurai base scaffold launched successfully.")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        run_default()
        return

    command = normalize_text(args[0])

    if command == "status":
        run_status()
    elif command == "hello":
        name = args[1] if len(args) > 1 else "Samurai"
        run_hello(name)
    elif command == "api":
        run_api()
    elif command == "help":
        run_help()
    elif command == "show-data":
        run_show_data()
    else:
        log_error(f"Unknown command: {command}")
        run_help()


if __name__ == "__main__":
    main()
