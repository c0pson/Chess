import sys
import os

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS2 # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_theme() -> str:
    with open(resource_path('assets\\theme.config'), 'r') as config:
        theme = config.readline()
    return theme.strip('\n')
