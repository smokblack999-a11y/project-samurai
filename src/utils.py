from datetime import datetime


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def banner(name):
    return f"{name} :: ready"


def normalize_text(value):
    return value.strip().lower()
