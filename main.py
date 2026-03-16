from src.config import Config
from src.logger import log_info, log_ok
from src.utils import now_str, banner


def main() -> None:
    log_info("Starting project...")
    log_ok(banner(Config.APP_NAME))
    log_info(f"Environment: {Config.APP_ENV}")
    log_info(f"Debug: {Config.DEBUG}")
    log_info(f"Time: {now_str()}")
    log_ok("Samurai base scaffold launched successfully.")


if __name__ == "__main__":
    main()from rich import print
from dotenv import load_dotenv
import os

load_dotenv()

print("[bold green]Samurai environment is ready[/bold green]")
print("Project:", os.getcwd())
