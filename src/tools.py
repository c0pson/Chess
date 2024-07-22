import configparser
import sys
import os

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS2 # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_from_config(variable: str) -> str | int:
    config = configparser.ConfigParser()
    config.read(resource_path('assets\\config.ini'))
    db_variable = config['database'][variable]
    if variable == 'size':
        return int(db_variable)
    return db_variable
