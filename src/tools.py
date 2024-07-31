import customtkinter as ctk
from PIL import Image
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

def change_config(change_variable: str, value: str | int) -> None:
    config = configparser.ConfigParser()
    config.read(resource_path('assets\\config.ini'))
    if isinstance(value, int):
        value = str(value)
    config['database'][change_variable] = value    
    with open(resource_path('assets\\config.ini'), 'w') as configfile:
        config.write(configfile)

def load_menu_image(option: str, resize: float = 1.5) -> ctk.CTkImage | None:
    setting_icon_path = resource_path(f'assets\\menu\\{option}.png')
    try:
        size = int(get_from_config('size')) // resize
        setting_icon = Image.open(setting_icon_path).convert('RGBA')
        return ctk.CTkImage(light_image=setting_icon, dark_image=setting_icon, size=(size, size))
    except (FileNotFoundError, FileExistsError) as e:
        print(f'Couldn`t load image for due to error: {e}')
    return None

def get_colors() -> dict:
    config = configparser.ConfigParser()
    config.read(resource_path('assets/config.ini'))
    colors = dict(config['Colors'])
    return colors

def change_color(color_name: str, color_value: str) -> None:
    config = configparser.ConfigParser()
    config.read(resource_path('assets\\config.ini'))
    config['Colors'][color_name] = color_value    
    with open(resource_path('assets\\config.ini'), 'w') as configfile:
        config.write(configfile)
