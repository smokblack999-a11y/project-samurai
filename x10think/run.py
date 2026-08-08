from __future__ import annotations

import argparse
import json
import threading

from .agent import Agent
from .api import serve
from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(prog="x10think")
    parser.add_argument("command", choices=("scan", "serve", "run"), nargs="?", default="scan")
    args = parser.parse_args()

    settings = Settings.load()
    agent = Agent(settings.data_dir)

    if args.command == "scan":
        print(json.dumps(agent.scan_once(), ensure_ascii=False, indent=2))
    elif args.command == "serve":
        agent.scan_once()
        serve(agent, settings.host, settings.port)
    else:
        threading.Thread(target=serve, args=(agent, settings.host, settings.port), daemon=True).start()
        agent.run_forever(settings.interval)


if __name__ == "__main__":
    main()
