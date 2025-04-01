"""Module with tools used all across the project. They are implemented in a way to be as reusable as possible.
"""

import customtkinter as ctk
from PIL import Image
import configparser
import sys
import os
from datetime import datetime
import sounddevice
from typing import Any
import json
from properties import SYSTEM

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
    elif variable == 'font_name':
        if SYSTEM == 'Linux':
            db_variable = list(db_variable.split(' '))[0]
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
        ctk.CTkImage | None: Image object.
    """
    setting_icon_path = resource_path(os.path.join('assets', 'menu', f'{option}.png'))
    try:
        size = int(get_from_config('size')) // resize
        setting_icon = Image.open(setting_icon_path).convert('RGBA')
        return ctk.CTkImage(light_image=setting_icon, dark_image=setting_icon, size=(size, size))
    except (FileNotFoundError, FileExistsError) as e:
        update_error_log(e)
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

def update_error_log(error: Exception) -> None:
    """Appends new error to error log.

    Args:
        error (Exception): Error to append log file with.
    """
    now: str = str(datetime.now())
    with open(resource_path('error.log'), 'a') as file:
        file.write(f'[{now}]: Error occurred: {error} in {os.path.relpath(__file__)}\n')

def play_sound(data: Any) -> None:
    """Plays sound.

    Args:
        data (Any): Array like with raw sound data.
    """
    try:
        sounddevice.play(data)
    except Exception as e:
        update_error_log(e)

def create_save_file(save_info: dict[tuple[int, int] | str, tuple[str, str, bool] | list[str]], current_turn: str, white_moves: list[str], black_moves: list[str], game_over: bool, save_name: str | None=None) -> None:
    """Creates save file in saves directory. Save is .json file with all positions, current turn information, previous notation and game over information.

    Args:
        save_info (dict[tuple[int, int]  |  str, tuple[str, str, bool]  |  list[str]]): Information to be saved in file.
        current_turn (str): Information about color of the current player.
        white_moves (list[str]): Notation from previous white moves.
        black_moves (list[str]): Notation from previous black moves.
        game_over (bool): Information about general state of the game. 
        save_name (str | None, optional): Name of the save file. Defaults to None.
    """
    save_info_serialized = {f"{k[0]},{k[1]}": v for k, v in save_info.items()}
    save_data = {
        'current_turn': current_turn,
        'board_state': save_info_serialized,
        'white_moves': white_moves,
        'black_moves': black_moves,
        'game_over': game_over
    }
    if not save_name:
        files: list[str] = [f for f in os.listdir(resource_path('saves')) if 'chess_game_' in f]
        if files:
            new_file: str = f'chess_game_{len(files)+1}.json'
            with open(resource_path(os.path.join('saves', new_file)), 'w') as file:
                json.dump(save_data, file, indent=2)
        else:
            new_file = 'chess_game_1.json'
            with open(resource_path(os.path.join('saves', new_file)), 'w') as file:
                json.dump(save_data, file, indent=2)
    else:
        new_file = f'{save_name}.json'
        with open(resource_path(os.path.join('saves', new_file)), 'w') as file:
                json.dump(save_data, file, indent=2)

def delete_save_file(file_name: str) -> bool:
    """Removes save .json file from saves directory.

    Args:
        file_name (str): Name of the file to delete.

    Returns:
        bool: Returns True if file was removed successfully, False otherwise.
    """
    file_path: str = resource_path(os.path.join('saves', file_name))
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def get_save_info(file_name: str) -> dict:
    """Gathers data from .json save file.

    Args:
        file_name (str): Name of the save to be loaded.

    Returns:
        dict: All needed information to load the game state.
    """
    with open(resource_path(os.path.join('saves', file_name)), "r") as file:
        data: dict = json.load(file)
    return data
