import customtkinter as ctk
from PIL import Image
import configparser
import sys
import os

def resource_path(relative_path: str) -> str:
    """Function obtaining the absolute path to desired relative path.
    Ensures That pyinstaller executable will work properly.

    Args:
        relative_path (str): Relative or absolute path to resource.

    Returns:
        str: Absolute path to resource.
    """
    try:
        base_path = sys._MEIPASS2 # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_from_config(variable: str) -> str | int:
    """Functions reading specific value from the config file.

    Args:
        variable (str): variable name from config file.

    Returns:
        str | int: Color, size or font name
    """
    config = configparser.ConfigParser()
    config.read(resource_path(os.path.join('assets', 'config.ini')))
    db_variable = config['database'][variable]
    if variable == 'size':
        return int(db_variable)
    return db_variable

def change_config(change_variable: str, value: str | int) -> None:
    """Updates specific variable in config file.

    Args:
        change_variable (str): Variable name to change
        value (str | int): Value to which the variable will be updated.
    """
    config = configparser.ConfigParser()
    config.read(resource_path(os.path.join('assets', 'config.ini')))
    if isinstance(value, int):
        value = str(value)
    config['database'][change_variable] = value    
    with open(resource_path(os.path.join('assets', 'config.ini')), 'w') as configfile:
        config.write(configfile)

def load_menu_image(option: str, resize: float = 1.5) -> ctk.CTkImage | None:
    """Function loading images for menu.

    Args:
        option (str): Option image name.
        resize (float, optional): Resize value [original_val // resize]. Defaults to 1.5.

    Returns:
        ctk.CTkImage | None: _description_
    """
    setting_icon_path = resource_path(os.path.join('assets', 'menu', f'{option}.png'))
    try:
        size = int(get_from_config('size')) // resize
        setting_icon = Image.open(setting_icon_path).convert('RGBA')
        return ctk.CTkImage(light_image=setting_icon, dark_image=setting_icon, size=(size, size))
    except (FileNotFoundError, FileExistsError) as e:
        print(f'Couldn`t load image for due to error: {e}')
    return None

def get_colors() -> dict:
    """Function loading colors from config file.

    Returns:
        dict: Dictionary (later enum) of color name : color code.
    """
    config = configparser.ConfigParser()
    config.read(resource_path(os.path.join('assets', 'config.ini')))
    colors = dict(config['Colors'])
    return colors

def change_color(color_name: str, color_value: str) -> None:
    """Function changing color value in config file.

    Args:
        color_name (str): Color name to change.
        color_value (str): New color value.
    """
    config = configparser.ConfigParser()
    config.read(resource_path(os.path.join('assets', 'config.ini')))
    config['Colors'][color_name] = color_value    
    with open(resource_path(os.path.join('assets', 'config.ini')), 'w') as configfile:
        config.write(configfile)
