from rich.console import Console

console = Console()


def log_info(message: str) -> None:
    console.print(f"[bold cyan][INFO][/bold cyan] {message}")


def log_ok(message: str) -> None:
    console.print(f"[bold green][OK][/bold green] {message}")


def log_error(message: str) -> None:
    console.print(f"[bold red][ERROR][/bold red] {message}")
