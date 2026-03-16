from rich import print
from dotenv import load_dotenv
import os

load_dotenv()

print("[bold green]Samurai environment is ready[/bold green]")
print("Project:", os.getcwd())
