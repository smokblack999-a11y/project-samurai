from src.logger import log_info, log_ok
from src.utils import now_str
from src.storage import load_storage, ensure_storage_file


def run_status() -> None:
    ensure_storage_file()
    log_ok("System status: OK")
    log_info(f"Time: {now_str()}")


def run_hello(name: str = "Samurai") -> None:
    log_ok(f"Hello, {name}!")


def run_help() -> None:
    log_info("Available commands:")
    print("  python main.py")
    print("  python main.py status")
    print("  python main.py hello")
    print("  python main.py hello YourName")
    print("  python main.py api")
    print("  python main.py show-data")


def run_show_data() -> None:
    ensure_storage_file()
    data = load_storage()
    log_info("Current storage data:")
    print(data)
from src.logger import log_info, log_ok
from src.utils import now_str
from src.storage import load_storage, ensure_storage_file


def run_status() -> None:
    ensure_storage_file()
    log_ok("System status: OK")
    log_info(f"Time: {now_str()}")


def run_hello(name: str = "Samurai") -> None:
    log_ok(f"Hello, {name}!")


def run_help() -> None:
    log_info("Available commands:")
    print("  python main.py")
    print("  python main.py status")
    print("  python main.py hello")
    print("  python main.py hello YourName")
    print("  python main.py api")
    print("  python main.py show-data")


def run_show_data() -> None:
    ensure_storage_file()
    data = load_storage()
    log_info("Current storage data:")
    print(data)
