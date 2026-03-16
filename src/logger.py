from datetime import datetime
import os

from rich.console import Console
from src.config import Config

console = Console()


def _write_file_log(level: str, message: str) -> None:
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}\n"
    with open(Config.APP_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def log_info(message: str) -> None:
    console.print(f"[bold cyan][INFO][/bold cyan] {message}")
    _write_file_log("INFO", message)


def log_ok(message: str) -> None:
    console.print(f"[bold green][OK][/bold green] {message}")
    _write_file_log("OK", message)


def log_error(message: str) -> None:
    console.print(f"[bold red][ERROR][/bold red] {message}")
    _write_file_log("ERROR", message)

from rich.console import Console
from src.config import Config

console = Console()


def _write_file_log(level: str, message: str) -> None:
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}\n"
    with open(Config.APP_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def log_info(message: str) -> None:
    console.print(f"[bold cyan][INFO][/bold cyan] {message}")
    _write_file_log("INFO", message)


def log_ok(message: str) -> None:
    console.print(f"[bold green][OK][/bold green] {message}")
    _write_file_log("OK", message)


def log_error(message: str) -> None:
    console.print(f"[bold red][ERROR][/bold red] {message}")
    _write_file_log("ERROR", message)
