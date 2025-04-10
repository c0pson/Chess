"""File with implementation for all menus: MoveRecord, Options and Settings.
"""

from fontTools.ttLib import TTFont
from typing import Callable, Any
import customtkinter as ctk
import subprocess
import os
import re
import pywinstyles

from tools import (
    get_from_config,
    change_config,
    load_menu_image,
    resource_path,
    change_color,
    update_error_log,
    create_save_file,
    delete_save_file,
    get_save_info
)
from properties import COLOR, STRING, SYSTEM
from notifications import Notification
from color_picker import ColorPicker
from piece import Piece, Knight

class MovesRecord(ctk.CTkFrame):
    """Class handling recording the moves during playtime. Class stores both players moves in lists and displays notation in two boxes dedicated for each player.

    Args:
        ctk.CTkFrame : Inheritance from customtkinter CTkFrame widget. 
    """
    def __init__(self, master) -> None:
        """Constructor:
             - calls function create_frames
             - creates 2D vector to record moves

        Args:
            master (Any): Parent widget
        """
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.font: ctk.CTkFont = ctk.CTkFont(str(get_from_config('font_name')), int(int(get_from_config('size')) * 0.4))
        self.create_frames()
        self.moves_white: list[str] = []
        self.moves_black: list[str] = []

    def record_move(self, moved_piece: Piece, previous_coords: tuple[int, int] | None=None, capture: bool=False,
                    castle: str | None=None, check: bool=False, checkmate: bool=False, promotion: str='') -> None:
        """Displays the chess notation of the move on the frame for specific player color.
        Simple if else logic with flags passed to the function is responsible of handling correctness of the notation.

        Args:
            moved_piece (Piece): Figure which was moved
            previous_coords (tuple[int, int] | None, optional): Coordinates of position before moving the figure. Defaults to None.
            capture (bool, optional): Flag to check if figure captured another figure. Defaults to False.
            castle (str | None, optional): Flag to check if castle occurred. Defaults to None.
            check (bool, optional): Checks if move caused the check. Defaults to False.
            checkmate (bool, optional): Checks if move caused the checkmate. Defaults to False.
            promotion (str, optional): Checks if pawn was promoted. Defaults to '' which means the promotion didn't occurred.
        """
        y_axis: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        x, y = 8 - moved_piece.position[0], y_axis[moved_piece.position[1]]
        prev_x = 8 - previous_coords[0] if previous_coords else ''
        prev_y = y_axis[previous_coords[1]] if previous_coords else ''
        if not isinstance(moved_piece, Knight):
            piece_name = moved_piece.__class__.__name__[0] if not moved_piece.__class__.__name__ == 'Pawn' else ''
        else:
            piece_name = 'N'
        check_nota: str = '+' if check and not checkmate else ''
        checkmate_nota: str = '#' if checkmate else ''
        promotion_nota: str = promotion if promotion != 'K' else 'N'
        if not castle:
            notation = f' {check_nota}{checkmate_nota}{'x' if capture else ''}{piece_name}{prev_y}{prev_x}-{y}{x}{promotion_nota}'
        else:
            notation = f' {check_nota}{checkmate_nota}{'0-0-0' if castle == 'queenside' else '0-0'}'
        current_frame = self.white_scroll_frame if moved_piece.color == 'w' else self.black_scroll_frame
        self.moves_white.append(notation) if moved_piece.color == 'w' else self.moves_black.append(notation)
        ctk.CTkLabel(
            master = current_frame,
            text   = notation,
            font   = self.font
        ).pack(side=ctk.BOTTOM)

    def load_notation_from_save(self, white_moves: list[str], black_moves: list[str]) -> None:
        """Loads notation from save file. Function gets already parsed json format to two lists and displays it using record_move() function.

        Args:
            white_moves (list[str]): List of previous white moves.
            black_moves (list[str]): List of previous white moves.
        """
        for notation in white_moves:
            ctk.CTkLabel(
                master = self.white_scroll_frame,
                text   = notation,
                font   = self.font
            ).pack(side=ctk.BOTTOM)
        for notation in black_moves:
            ctk.CTkLabel(
                master = self.black_scroll_frame,
                text   = notation,
                font   = self.font
            ).pack(side=ctk.BOTTOM)
        self.moves_white[:] = white_moves
        self.moves_black[:] = black_moves

    def create_frames(self) -> None:
        """Creates frames to reserve space on main app page for displaying move notations.
        """
        black_label: ctk.CTkLabel = ctk.CTkLabel(
            master     =  self,
            text       = 'Black',
            font       = self.font,
            text_color = COLOR.DARK_TEXT
        )
        black_label.pack(side=ctk.TOP, padx=1, pady=1)
        additional_frame: ctk.CTkFrame = ctk.CTkFrame(
            master        = self, 
            fg_color      = COLOR.TRANSPARENT, 
            corner_radius = 0,
            border_color  = COLOR.DARK_TEXT, 
            border_width  = 7
        )
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.black_scroll_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master                       = additional_frame, 
            scrollbar_button_color       = COLOR.NOTATION_BACKGROUND_B,
            fg_color                     = COLOR.NOTATION_BACKGROUND_B, 
            corner_radius                = 0,
            scrollbar_button_hover_color = COLOR.NOTATION_BACKGROUND_B
        )
        self.black_scroll_frame.pack(side=ctk.TOP, padx=6, pady=7, fill=ctk.Y, expand=True)
        white_label: ctk.CTkLabel = ctk.CTkLabel(
            master     = self, 
            text       = 'White', 
            font       = self.font, 
            text_color = COLOR.TEXT
        )
        white_label.pack(side=ctk.TOP, padx=0, pady=0)
        additional_frame = ctk.CTkFrame(
            master = self,
            fg_color=COLOR.TRANSPARENT,
            corner_radius=0,
            border_color=COLOR.DARK_TEXT,
            border_width=7
        )
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.white_scroll_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master                       = additional_frame,
            scrollbar_button_color       = COLOR.NOTATION_BACKGROUND_W,
            fg_color                     = COLOR.NOTATION_BACKGROUND_W,
            corner_radius                = 0,
            scrollbar_button_hover_color = COLOR.NOTATION_BACKGROUND_W)
        self.white_scroll_frame.pack(side=ctk.TOP, padx=6, pady=7, fill=ctk.Y, expand=True)
        space_label: ctk.CTkLabel = ctk.CTkLabel(
            master =self,
            text='\n'
        )
        space_label.pack()

    def restart(self) -> None:
        """Destroys the old notated moves and clears the lists.
        """
        self.moves_white.clear()
        self.moves_black.clear()
        for child in self.white_scroll_frame.winfo_children():
            child.destroy()
        for child in self.black_scroll_frame.winfo_children():
            child.destroy()

class Saves(ctk.CTkFrame):
    """Class handling saving, showing and loading saves in separate menu.

    Args:
        ctk.CTkFrame : Inheritance from customtkinter CTkFrame widget.
    """
    def __init__(self, master: Any, board) -> None:
        """Constructor:
         - loads fonts
         - calls function showing all saves

        Args:
            master (Any): Parent widget.
            board (Board): Board object.
        """
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.font_32 = ctk.CTkFont(get_from_config('font_name'), 32)
        self.font_26 = ctk.CTkFont(get_from_config('font_name'), 26)
        self.close_image: ctk.CTkImage | None = load_menu_image('close')
        self.show_all_saves(board)
        ctk.CTkLabel(
            master   = self,
            text     = '',
            height   = 18,
            fg_color = COLOR.BACKGROUND
        ).pack(padx=0, pady=0)

    @staticmethod
    def save_game_to_file(board) -> bool:
        """Saves the current game state to the .json file in saves folder.

        Args:
            board (Board): Board object.

        Returns:
            bool: Returns True if save was created successfully, False otherwise.
        """
        save_info: dict[tuple[int, int] | str, tuple[str, str, bool] | list[str]] = dict()
        for row in board.board:
            for cell in row:
                if cell.figure:
                    figure: str = cell.figure.__class__.__name__
                    save_info[cell.position] = (figure, cell.figure.color, cell.figure.first_move)
        if not board.current_save_name:
            save_name: str | None | bool = SaveName().get_save_name()
            board.current_save_name = save_name
        else:
            save_name = board.current_save_name.strip('.json')
        moves_record: MovesRecord = board.moves_record
        if not isinstance(save_name, bool):
            create_save_file(
                save_info,
                board.current_turn,
                moves_record.moves_white,
                moves_record.moves_black,
                board.game_over,
                save_name
            )
            return True
        return False

    def show_all_saves(self, board) -> None:
        """Displays all saves as clickable buttons in saves menu.

        Args:
            board (Board): Board object.
        """
        top_frame: ctk.CTkFrame = ctk.CTkFrame(
            master   = self,
            fg_color = COLOR.TRANSPARENT
        )
        top_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.X)
        settings_text = ctk.CTkLabel(
            master     = top_frame,
            text       = 'Saves',
            font       = ctk.CTkFont(str(get_from_config('font_name')), 38),
            text_color = COLOR.DARK_TEXT,
            anchor     = ctk.N
        )
        settings_text.pack(side=ctk.LEFT, padx=20, anchor=ctk.NW)
        close_button = ctk.CTkLabel(
            master = top_frame,
            text   = '',
            font   = ctk.CTkFont(str(get_from_config('font_name')), 24),
            image  = self.close_image,
            anchor = ctk.S
        )
        close_button.bind('<Button-1>', self.on_close)
        close_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10, pady=10)
        self.scrollable_frame = ctk.CTkScrollableFrame(
            master   = self,
            fg_color = COLOR.BACKGROUND,
            corner_radius = 0,
            scrollbar_button_color = COLOR.DARK_TEXT,
        )
        self.scrollable_frame.pack(side=ctk.TOP, padx=0, pady=0, expand=True, fill=ctk.BOTH)
        files: list[str] = [f for f in os.listdir(resource_path('saves'))]
        for file in files:
            self.create_file_button(self.scrollable_frame, file, board)

    def create_file_button(self, frame: ctk.CTkFrame, file_name: str, board) -> None:
        """Helper function creating single button which will load specific save after clicking.

        Args:
            frame (ctk.CTkFrame): Parent widget.
            file_name (str): Name of the file.
            board (Board): Board object.
        """
        helper_frame = ctk.CTkFrame(
            master        = frame,
            fg_color      = COLOR.TILE_1,
            corner_radius = 0
        )
        helper_frame.pack(side=ctk.TOP, padx=150, pady=10, fill=ctk.X)
        ctk.CTkLabel(
            master   = helper_frame,
            fg_color = COLOR.NOTATION_BACKGROUND_B,
            text     = '',
            width    = 20
        ).pack(side=ctk.LEFT, padx=0, pady=0, fill=ctk.Y)
        file_name_label = ctk.CTkLabel(
            master        = helper_frame,
            text          = f' {file_name.replace('.json', '')}',
            fg_color      = COLOR.TILE_1,
            font          = self.font_32,
            corner_radius = 0,
            anchor        = ctk.W
        )
        file_name_label.bind('<Button-1>', lambda e: self.load_save(e, board, file_name))
        file_name_label.pack(side=ctk.LEFT, padx=15, pady=0, fill=ctk.BOTH, expand=True)
        delete_button = ctk.CTkButton(
            master        = helper_frame,
            fg_color      = COLOR.CLOSE,
            hover_color   = COLOR.CLOSE_HOVER,
            command       = lambda: self.remove_save(file_name, helper_frame),
            text          = 'REMOVE',
            font          = self.font_26,
            corner_radius = 0
        )
        delete_button.pack(side=ctk.RIGHT, padx=10, pady=10, anchor=ctk.N)

    def remove_save(self, file_name: str, frame: ctk.CTkFrame) -> None:
        """Deletes specific save. Button is part of the save button which makes it easier for user to determine which save is being deleted.

        Args:
            file_name (str): Name of the file to be deleted.
            frame (ctk.CTkFrame): Parent widget.
        """
        if delete_save_file(file_name):
            frame.destroy()
            Notification(self.master, f'Save {file_name.replace('.json', '')} has been removed', 2, 'top')
        else:
            Notification(self.master, 'Couldn\'t remove the save', 2, 'top')

    def load_save(self, event: Any, board, file_name: str) -> None:
        """Helper function calling all necessary functions to load the game from save. Notifications will indicate if it was successful or not.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
            board (Board): Board object.
            file_name (str): Name of the file from which the game will be loaded.
        """
        if board.load_board_from_file(get_save_info(file_name), file_name):
            Notification(self.master, 'Save loaded successfully', 3, 'top')
            self.master.after(201, self.on_close)
        else:
            Notification(self.master, 'Couldn\'t load save', 2, 'top')

    def on_close(self, event: Any=None) -> None:
        """Custom close function handling slow fade out animation.

        Args:
            event (Any, optional): Event type. Doesn't matter but is required parameter by customtkinter.. Defaults to None.
        """
        def update_opacity(i: int) -> None:
            if i >= 0:
                pywinstyles.set_opacity(self, value=i*0.005, color='#000001')
                self.master.after(1, lambda: update_opacity(i - 1))
            else:
                self.after(10, self.destroy)
        update_opacity(200)

class Options(ctk.CTkFrame):
    """Class handling user interface with available options on main window frame:
     - customization settings
     - restarting game
     - saving game
     - loading game

    Args:
        ctk.CTkFrame : Inheritance from customtkinter CTkFrame widget.
    """
    def __init__(self, master, restart_func: Callable, update_assets_func: Callable, update_font_func: Callable, get_board_func: Callable):
        """Constructor:
             - places all options buttons
             - loads menu assets
             - calls all necessary setup functions

        Args:
            master (Any): Parent widget.
            restart_func (Callable): Master function to restart the game.
            update_assets_func (Callable): Master function to update assets.
            update_font_func (Callable): Master function to update font.
        """
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.restart_func: Callable = restart_func
        self.update_assets_func: Callable = update_assets_func
        self.update_font_func: Callable = update_font_func
        self.get_board_func: Callable = get_board_func
        self.setting_icon: ctk.CTkImage | None = load_menu_image('settings')
        self.replay_icon: ctk.CTkImage | None = load_menu_image('replay')
        self.saves_image: ctk.CTkImage | None = load_menu_image('saves')
        self.save_as_image: ctk.CTkImage | None = load_menu_image('save_as')
        self.settings: Settings | None = None
        self.saves: Saves | None = None
        self.setting_button()
        self.space_label()
        self.replay_button()
        self.space_label()
        self.save_button()
        self.space_label()
        self.load_saves_button()

    def setting_button(self) -> None:
        """Setup of setting button.
        """
        self.s_icon_label: ctk.CTkLabel = ctk.CTkLabel(self, text='', image=self.setting_icon)
        self.s_icon_label.pack(side=ctk.TOP, padx=10, pady=5)
        self.s_icon_label.bind('<Button-1>', self.open_settings)

    def replay_button(self) -> None:
        """Setup of replay button.
        """
        self.r_icon_label: ctk.CTkLabel = ctk.CTkLabel(
            master =  self,
            text   = '',
            image  = self.replay_icon)
        self.r_icon_label.pack(side=ctk.TOP, padx=10, pady=0)
        self.r_icon_label.bind('<Button-1>', self.replay)

    def save_button(self) -> None:
        """Setup of save button.
        """
        self.save_icon_label: ctk.CTkLabel = ctk.CTkLabel(
            master = self,
            text   = '',
            image  = self.save_as_image
        )
        self.save_icon_label.pack(side=ctk.TOP, padx=10, pady=0)
        self.save_icon_label.bind('<Button-1>', self.save_game)

    def load_saves_button(self) -> None:
        """Setup of button showing all saves.
        """
        self.load_icon_label: ctk.CTkLabel = ctk.CTkLabel(
            master = self,
            text   = '',
            image  = self.saves_image 
        )
        self.load_icon_label.pack(side=ctk.TOP, padx=10, pady=0)
        self.load_icon_label.bind('<Button-1>', self.load_saves)

    def space_label(self) -> None:
        """Setups of space to maintain spacing between the button.
        """
        space: ctk.CTkLabel = ctk.CTkLabel(
            master = self,
            text   = '\n')
        space.pack(padx=2, pady=2)

    def open_settings(self, event: Any) -> None:
        """Function opening settings menu. For optimizations the settings frame is not being destroyed, but is hidden,
        it has no impact on user experience as all changes are dynamic and app restart wont be required to see the changes.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        if self.settings:
            self.settings.place(relx=0, rely=0, relwidth=1, relheight=1)
        else:
            self.settings = Settings(self.master, self.restart_func, self.update_assets_func, self.update_font_func)

    def replay(self, event: Any) -> None:
        """Function restarting the game. Calls function passed from Board to restart state of the game.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        self.after(1, self.restart_func)

    def save_game(self, event: Any) -> None:
        """Saves game to .json file and displays notification if successful.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        if Saves.save_game_to_file(self.get_board_func()):
            Notification(self.master, 'Save was created successfully', 2, 'top')

    def load_saves(self, event: Any) -> None:
        """Function opening saves menu. To always get all saves even these created during app runtime it has to be created every time from scratch to avoid bugs and unintended behavior.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        self.saves = Saves(self.master, self.get_board_func())
        self.saves.place(relx=0, rely=0, relwidth=1, relheight=1)

class Settings(ctk.CTkFrame):
    """Class handling changes in setting such as fonts, assets and colors made by user.
    Handles saving and updating the changes during app runtime except for color changes as they could take too much time for smooth experience.

    Args:
        ctk.CTkFrame : Inheritance from customtkinter CTkFrame widget.
    """
    def __init__(self, master, restart_func: Callable, update_assets_func: Callable, update_font_func: Callable) -> None:
        """Constructor
         - places itself on the screen
         - calls all functions creating frames containing content

        Args:
            master (Any): Parent widget.
            restart_func (Callable): Master function to restart the game.
            update_assets_func (Callable): Master function to update assets.
            update_font_func (Callable): Master function to update font.
        """
        super().__init__(master, fg_color=COLOR.BACKGROUND, corner_radius=0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.close_image: ctk.CTkImage | None = load_menu_image('close')
        self.color_picker_image: ctk.CTkImage | None = load_menu_image('colorpicker', resize=2)
        self.close_button()
        self.font_30: ctk.CTkFont = ctk.CTkFont(str(get_from_config('font_name')), 30)
        self.scrollable_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color=COLOR.BACKGROUND,
                                                        scrollbar_button_color=COLOR.DARK_TEXT)
        self.scrollable_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.BOTH, expand=True)
        self.font_name: str = str(get_from_config('font_name'))
        self.choose_theme()
        self.choose_font()
        self.open_assets_folder()
        self.change_colors()
        self.previous_theme: str | None = None
        self.choice: str | None = None
        self.restart_func: Callable = restart_func
        self.update_assets_func: Callable = update_assets_func
        self.update_font_func: Callable = update_font_func
        ctk.CTkLabel(
            master   = self,
            text     = '',
            height   = 18,
            fg_color = COLOR.BACKGROUND
        ).pack(padx=0, pady=0)

    @staticmethod
    def list_directories_os(path: str) -> list[str]:
        """Lists all directories for given path.

        Args:
            path (str): Desired path.

        Returns:
            list[str]: List of all directories from path.
        """
        try:
            entries: list[str] = os.listdir(path)
            directories: list[str] = [
                entry for entry in entries
                if os.path.isdir(os.path.join(path, entry)) and os.listdir(os.path.join(path, entry))
            ]
            return directories
        except FileNotFoundError as e:
            update_error_log(e)
            return []

    def close_button(self) -> None:
        """Setup of close button.
        """
        top_frame: ctk.CTkFrame = ctk.CTkFrame(
            master   = self,
            fg_color = COLOR.TRANSPARENT
        )
        top_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.X)
        settings_text = ctk.CTkLabel(
            master     = top_frame,
            text       = 'Settings',
            font       = ctk.CTkFont(str(get_from_config('font_name')), 38),
            text_color = COLOR.DARK_TEXT,
            anchor     = ctk.N
        )
        settings_text.pack(side=ctk.LEFT, padx=20, anchor=ctk.NW)
        close_button = ctk.CTkLabel(
            master = top_frame,
            text   = '',
            font   = ctk.CTkFont(str(get_from_config('font_name')), 24),
            image  = self.close_image,
            anchor = ctk.S
        )
        close_button.bind('<Button-1>', self.on_close)
        close_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10, pady=10)

    def create_theme_button(self, frame: ctk.CTkFrame, theme: str) -> None:
        """Setup of theme button.

        Args:
            frame (ctk.CTkFrame): Frame in which button will be placed.
            theme (str): Style of Figures to choose.
        """ 
        current_theme = get_from_config('theme')
        theme_button: ctk.CTkButton = ctk.CTkButton(
            master        = frame,
            text          = theme,
            command       = lambda: self.select_theme(theme, theme_button),
            font          = self.font_30,
            corner_radius = 0,
            fg_color      = COLOR.TILE_1,
            hover_color   = COLOR.HIGH_TILE_2,
            text_color    = COLOR.TEXT,
        )
        theme_button.pack(side=ctk.LEFT, padx=4, pady=4, expand=True)
        if current_theme == theme:
            theme_button.configure(state=ctk.DISABLED)

    def choose_theme(self) -> None:
        """Setup of theme chooser.
        """
        self.previous_theme = str(get_from_config('theme'))
        themes: list[str] = self.list_directories_os('assets')
        if not themes:
            return
        text: ctk.CTkLabel = ctk.CTkLabel(
            master     = self.scrollable_frame,
            text       = 'Themes: ',
            font       = ctk.CTkFont(str(get_from_config('font_name')), 32),
            text_color = COLOR.TEXT
        )
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        themes.remove('menu') if 'menu' in themes else themes
        frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master                 = self.scrollable_frame,
            fg_color               = COLOR.TILE_2,
            scrollbar_button_color = COLOR.DARK_TEXT,
            orientation            = ctk.HORIZONTAL,
            scrollbar_fg_color     = COLOR.DARK_TEXT,
            height                 = 70,
            corner_radius          = 0
        )
        frame.pack(side=ctk.TOP, padx=80, pady=5, anchor=ctk.W, fill=ctk.X)
        for theme in themes:
            self.create_theme_button(frame, theme)
        warning_text: ctk.CTkLabel = ctk.CTkLabel(
            master     = self.scrollable_frame,
            text       = STRING.ASSETS_WARNING,
            font       = ctk.CTkFont(str(get_from_config('font_name')), 18),
            text_color = COLOR.CLOSE
        )
        warning_text.pack(side=ctk.TOP, anchor=ctk.SW, padx=100, pady=0)

    def select_theme(self, choice: str, button: ctk.CTkButton) -> None:
        """Helper function to save theme changes to config file.

        Args:
            choice (str): Name of theme to save.
        """
        self.choice = choice
        theme = get_from_config('theme')
        for child in button.master.winfo_children():
            if isinstance(child, ctk.CTkButton) and child.cget('text') == theme:
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkButton) and child.cget('text') == choice:
                child.configure(state=ctk.DISABLED)
        change_config('theme', choice)

    def on_close(self, event: Any) -> None:
        """Waits for close action to properly destroy the window with fade out animation.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        def update_opacity(i: int) -> None:
            if i >= 0:
                pywinstyles.set_opacity(self, value=i*0.005, color='#000001')
                self.master.after(1, lambda: update_opacity(i - 1))
            else:
                if not self.previous_theme and not self.choice:
                    self.place_forget()
                self.update_assets_func()
                self.place_forget()
                pywinstyles.set_opacity(self, value=1, color='#000001')
        update_opacity(200)

    @staticmethod
    def open_file_explorer(path: str) -> None:
        """Opens file explorer with system call specific to user operating system.

        Args:
            path (str): Path to open.
        """
        if SYSTEM == 'Windows':
            os.startfile(resource_path(path))
        elif SYSTEM == 'Darwin':
            subprocess.run(['open', resource_path(path)])
        elif SYSTEM == 'Linux':
            subprocess.run(['xdg-open', resource_path(path)])

    @staticmethod
    def get_all_files(path: str) -> list[str]:
        """Gathers all files from directory. If error occurs after catching the exception empty list is returned.

        Args:
            path (str): Path of the desired directory.

        Returns:
            list[str]: List of all file names from path directory.

        Exceptions:
            FileNotFoundError: If the directory does not exist.
            PermissionError: If access to the directory is denied.
            OSError: If an OS-related error occurs.
        """
        path = resource_path(path)
        try:
            all_files = [os.path.join((path), f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return all_files
        except (FileNotFoundError, PermissionError, OSError) as e:
            update_error_log(e)
            return []

    @staticmethod
    def get_font_name(ttf_path: str) -> str | None:
        """Gets name of the font from font file.

        Args:
            ttf_path (str): Path to .ttf font file name.

        Returns:
            str | None: Returns font name on success otherwise None.
        """
        try:
            font: TTFont = TTFont(resource_path(ttf_path))
            name: str = ''
            for record in font['name'].names:
                if record.nameID == 4:
                    if b'\000' in record.string:
                        name = record.string.decode('utf-16-be')
                    else:
                        name = record.string.decode('utf-8')
                    break
            return name
        except Exception as e: # dont really know what kind of error might occur here
            update_error_log(e)
            return None

    def open_assets_folder(self) -> None:
        """Setup of open assets button.
        """
        text_label = ctk.CTkLabel(
            master     = self.scrollable_frame,
            text       = 'Open assets folder',
            text_color = COLOR.TEXT,
            font       = ctk.CTkFont(str(get_from_config('font_name')), 32)
        )
        text_label.pack(side=ctk.TOP, padx=75, pady=4, anchor=ctk.NW)
        additional_frame = ctk.CTkFrame(
            master        = self.scrollable_frame,
            fg_color      = COLOR.TILE_2,
            corner_radius = 0
        )
        additional_frame.pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)
        open_button = ctk.CTkButton(
            master        = additional_frame,
            text          = 'OPEN',
            font          = ctk.CTkFont(str(get_from_config('font_name')), 20),
            text_color    = COLOR.TEXT,
            command       = lambda: self.open_file_explorer('assets'),
            fg_color      = COLOR.TILE_1,
            hover_color   = COLOR.HIGH_TILE_2,
            corner_radius = 0
        )
        open_button.pack(side=ctk.RIGHT, padx=10, pady=4, anchor=ctk.E)
        path_text = ctk.CTkLabel(
            master     = additional_frame, 
            text       = resource_path('assets'), 
            text_color = COLOR.DARK_TEXT,
            font       = ctk.CTkFont(str(get_from_config('font_name')), 18)
        )
        path_text.pack(side=ctk.LEFT, padx=15, pady=15)
        ctk.CTkLabel(
            master        = self.scrollable_frame,
            fg_color      = COLOR.DARK_TEXT,
            text          = '',
            corner_radius = 0,
            height        = 16
        ).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)

    def choose_font(self) -> None:
        """setup of choose font.
        """
        self.previous_font = str(get_from_config('font_file_name'))
        fonts = self.get_all_files('fonts')
        if not fonts:
            return
        text = ctk.CTkLabel(
            master     = self.scrollable_frame,
            text       = 'Fonts: ',
            font       = ctk.CTkFont(str(get_from_config('font_name')), 32),
            text_color = COLOR.TEXT
        )
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        frame = ctk.CTkScrollableFrame(
            master                 = self.scrollable_frame,
            fg_color               = COLOR.TILE_2,
            scrollbar_button_color = COLOR.DARK_TEXT,
            orientation            = ctk.HORIZONTAL,
            height                 = 70,
            corner_radius          = 0,
            scrollbar_fg_color     = COLOR.DARK_TEXT
        )
        frame.pack(side=ctk.TOP, padx=80, pady=5, anchor=ctk.W, fill=ctk.X)
        for font in fonts:
            self.create_font_button(frame, font)

    def create_font_button(self, frame: ctk.CTkFrame, font: str) -> None:
        """Setup of font button.

        Args:
            frame (ctk.CTkFrame): Frame in which button will be placed.
            font (str): Font name.
        """
        current_font = get_from_config('font_name')
        font_name = self.get_font_name(font)
        font_button: ctk.CTkButton = ctk.CTkButton(
            master        = frame,
            text          = font_name,
            command       = lambda: self.select_font(font, font_button),
            font          = self.font_30,
            corner_radius = 0,
            fg_color      = COLOR.TILE_1,
            hover_color   = COLOR.HIGH_TILE_2,
            text_color    = COLOR.TEXT
        )
        font_button.pack(side=ctk.LEFT, padx=4, pady=4, expand=True)
        if current_font == font_name:
            font_button.configure(state=ctk.DISABLED)

    def select_font(self, font: str, button: ctk.CTkButton) -> None:
        """Helper function to save change of font name and path to file to config file.

        Args:
            font (str): Font path.
        """
        if os.path.basename(font) == self.previous_font:
            return
        new_font = self.get_font_name(font)
        for child in button.master.winfo_children():
            if isinstance(child, ctk.CTkButton) and child.cget('text') ==  get_from_config('font_name'):
                child.configure(state=ctk.NORMAL)
            elif isinstance(child, ctk.CTkButton) and child.cget('text') == new_font:
                child.configure(state=ctk.DISABLED)
        if new_font:
            change_config('font_name', new_font)
            change_config('font_file_name', os.path.basename(font))
            self.master.board.font_42 = ctk.CTkFont(get_from_config('font_name'), 42)
            self.master.board.board_font = ctk.CTkFont(get_from_config('font_name'), int(get_from_config('size'))//3)
            self.update_font_func()
            self.previous_font = str(get_from_config('font_file_name'))

    @staticmethod
    def is_valid_color(color: str) -> bool:
        """Checks if user passed string is valid with hex color.

        Args:
            color (str): User defined color.

        Returns:
            bool: True if color passes regex pattern for hex color, False otherwise.
        """
        return bool(re.compile(r'^#[0-9a-fA-F]{6}$').match(color))

    @staticmethod
    def validate_length(new_value: str) -> bool:
        """Validation function for color input.

        Args:
            new_value (str): User input from color entry.

        Returns:
            bool: True if length of the string is not longer than 7, False otherwise.
        """
        
        return bool(re.compile(r'^[#\w]{0,7}$').match(new_value))

    def change_colors(self) -> None:
        """Function updating color preview in the theme changer.
        """
        text = ctk.CTkLabel(
            master     = self.scrollable_frame, 
            text       = 'Colors: ', 
            font       = ctk.CTkFont(str(get_from_config('font_name')), 32), 
            text_color = COLOR.TEXT
        )
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        warning_text = ctk.CTkLabel(
            master     = self.scrollable_frame, 
            text       = STRING.COLORS_WARNING, 
            font       = ctk.CTkFont(str(get_from_config('font_name')), 18),
            text_color = COLOR.CLOSE
        )
        warning_text.pack(side=ctk.TOP, anchor=ctk.SW, padx=100, pady=0)
        frame = ctk.CTkFrame(
            master        = self.scrollable_frame,
            corner_radius = 0,
            fg_color      = COLOR.TILE_2
        )
        frame.pack(side=ctk.TOP, padx=80, pady=0, anchor=ctk.W, fill=ctk.X)
        ctk.CTkLabel(
            master = frame,
            text   = '',
            height = 2
        ).pack(padx=0, pady=0)
        for color in COLOR:
            self.color_label(frame, color) if color != 'transparent' else ...
        ctk.CTkLabel(
            master = frame,
            text   = '',
            height = 2
        ).pack(padx=0, pady=0)
        ctk.CTkLabel(
            master        = self.scrollable_frame, 
            fg_color      = COLOR.DARK_TEXT, 
            text          = '', 
            corner_radius = 0, 
            height        = 16
        ).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)
        ctk.CTkLabel(
            master        = self.scrollable_frame, 
            fg_color      = COLOR.TRANSPARENT, 
            text          = '', 
            corner_radius = 0, 
            height        = 16
        ).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)

    def color_label(self, frame: ctk.CTkFrame, color: str) -> None:
        """Function creating color preview frame.

        Args:
            frame (ctk.CTkFrame): Parent frame.
            color (str): New hex color string.
        """
        for color_name , color_str in COLOR.__members__.items():
            if color_str == color:
                name_of_color = color_name
                break
        color_frame = ctk.CTkFrame(
            master = frame,
            fg_color=COLOR.NOTATION_BACKGROUND_B,
            corner_radius=0
        )
        color_frame.pack(side=ctk.TOP, padx=10, pady=4, fill=ctk.X)
        vcmd = (self.register(self.validate_length), '%P')
        color_entry = ctk.CTkEntry(
            master          = color_frame, 
            border_width    = 0, 
            corner_radius   = 0, 
            fg_color        = color,
            font            = ctk.CTkFont(get_from_config('font_name'), 20),
            validate        = 'key',
            validatecommand = vcmd,
            text_color      = COLOR.TEXT if color != COLOR.TEXT else COLOR.DARK_TEXT
        )
        color_entry.insert(0, color)
        rgb_color = color.lstrip('#')
        r = int(rgb_color[0:2], 16)
        g = int(rgb_color[2:4], 16)
        b = int(rgb_color[4:6], 16)
        color_picker = ctk.CTkLabel(
            master = color_frame,
            text   = '',
            image  = self.color_picker_image
        )
        color_picker.pack(side=ctk.LEFT, padx=5, pady=4)
        color_picker.bind('<Button-1>', lambda e: self.ask_for_color(r, g, b, color_entry, color_name))
        color_entry.pack(side=ctk.LEFT, padx=10, pady=4)
        ok_button = ctk.CTkButton(
            master        = color_frame, 
            text          = 'OK', 
            font          = ctk.CTkFont(get_from_config('font_name'), 20),
            command       = lambda: self.save_color(color_name, color_entry, color_entry, color),
            width         = 50,
            corner_radius = 0,
            fg_color      = COLOR.TILE_1,
            hover_color   = COLOR.HIGH_TILE_1,
            text_color    = COLOR.TEXT
        )
        ok_button.pack(side=ctk.LEFT, padx=10, pady=4)
        cancel_button = ctk.CTkButton(
            master        = color_frame,
            text          = 'CANCEL',
            font          = ctk.CTkFont(get_from_config('font_name'), 20),
            command       = lambda: self.cancel(color_name, color_entry, color),
            width         = 50,
            corner_radius = 0,
            fg_color      = COLOR.CLOSE,
            hover_color   = COLOR.CLOSE_HOVER,
            text_color    = COLOR.TEXT
        )
        cancel_button.pack(side=ctk.LEFT, padx=10, pady=4)
        color_name_label = ctk.CTkLabel(
            master     = color_frame,
            text       = name_of_color,
            text_color = COLOR.TEXT,
            font       = ctk.CTkFont(get_from_config('font_name'), 22)
        )
        color_name_label.pack(side=ctk.RIGHT, padx=4, pady=4)

    def save_color(self, color_name: str, entry: ctk.CTkEntry, color_label: ctk.CTkLabel, old_color: str) -> None:
        """Saves new color into config file.

        Args:
            color_name (str): Name of the color to change.
            entry (ctk.CTkEntry): User input with color hex code.
            color_label (ctk.CTkLabel): Parent frame to update.
        """
        new_color = entry.get()
        if self.is_valid_color(new_color):
            change_color(color_name, new_color)
            color_label.configure(fg_color=new_color)
        else:
            entry.delete(0, ctk.END)
            entry.insert(0, old_color)

    def ask_for_color(self, r: int, g: int, b: int, entry: ctk.CTkEntry, color_name: str) -> None:
        """Input dialog with custom color picker for easy use.

        Args:
            r (int): Red color intensity.
            g (int): Green color intensity.
            b (int): Blue color intensity.
            entry (ctk.CTkEntry): Entry frame for user input.
            color_name (str): Color name from config file.
        """
        picker = ColorPicker(
            fg_color              = COLOR.BACKGROUND,
            r                     = r,
            g                     = g,
            b                     = b,
            font                  = ctk.CTkFont(self.font_name, 15),
            border_color          = COLOR.TILE_2,
            slider_button_color   = COLOR.TILE_2,
            slider_progress_color = COLOR.TEXT,
            slider_fg_color       = COLOR.DARK_TEXT,
            preview_border_color  = COLOR.DARK_TEXT,
            button_fg_color       = COLOR.NOTATION_BACKGROUND_B,
            button_hover_color    = COLOR.NOTATION_BACKGROUND_W,
            icon                  = resource_path(os.path.join('assets', 'logo.ico')),
            corner_radius         = 0
        )
        color = picker.get_color()
        if color:
            entry.delete(0, ctk.END)
            entry.insert(0, color)
            change_color(color_name, color)
            entry.configure(fg_color=color)

    def cancel(self, color_name: str, entry: ctk.CTkEntry, color: str) -> None:
        """Helper function to close input dialog without changing any properties in config file.

        Args:
            color_name (str): Color name from config file.
            entry (ctk.CTkEntry): Entry frame for user input.
            color (str): Color to keep.
        """
        entry.delete(0, ctk.END)
        entry.insert(0, color)
        change_color(color_name, color)
        entry.configure(fg_color=color)

class SaveName(ctk.CTkToplevel):
    """Class for asking user for the save name in popup window.

    Args:
        ctk.CTkTopLevel : Inheritance from customtkinter CTkFrame widget.
    """
    def __init__(self) -> None:
        """Constructor:
         - sets window to appear on top
         - loads fonts
         - calls all setup functions
         - centers window
        """
        super().__init__(fg_color=COLOR.BACKGROUND)
        if SYSTEM == 'Windows':
            self.grab_set()
        self.attributes('-topmost', True)
        self.title('Save')
        self.font_21 = ctk.CTkFont(get_from_config('font_name'), 21)
        self.font_28 = ctk.CTkFont(get_from_config('font_name'), 28)
        self.save_name: str | None | bool = None
        self.create_info()
        self.create_name_entry()
        self.create_save_button()
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.center_window()
        self.after(201, lambda: self.iconbitmap(resource_path('assets\\logo.ico')))

    def create_info(self) -> None:
        """Displays warning info.
        """
        self.info_label: ctk.CTkLabel = ctk.CTkLabel(
            master     = self,
            fg_color   = COLOR.BACKGROUND,
            text       = STRING.SAVES_WARNING,
            text_color = COLOR.CLOSE_HOVER,
            font       = self.font_21
        )
        self.info_label.pack(side=ctk.TOP, padx=15, pady=15, fill=ctk.X)

    def create_name_entry(self) -> None:
        """Creates entry for name of the save.
        """
        helper_frame: ctk.CTkFrame = ctk.CTkFrame(
            master   = self,
            fg_color = COLOR.BACKGROUND,

        )
        helper_frame.pack(side=ctk.TOP, padx=15, pady=15, fill=ctk.X)
        self.save_name_entry: ctk.CTkEntry = ctk.CTkEntry(
            master           = helper_frame,
            fg_color         = COLOR.BACKGROUND,
            text_color       = COLOR.TEXT,
            corner_radius    = 0,
            border_color     = COLOR.DARK_TEXT,
            font             = self.font_28,
            border_width     = 3,
            placeholder_text = 'Name'
        )
        self.save_name_entry.pack(side=ctk.LEFT, padx=1, pady=1, fill=ctk.X, expand=True)

    def create_save_button(self) -> None:
        """Setups save button.
        """
        self.save_button: ctk.CTkButton = ctk.CTkButton(
            master        = self,
            fg_color      = COLOR.TILE_1,
            hover_color   = COLOR.HIGH_TILE_1,
            text          = 'SAVE',
            font          = self.font_21,
            command       = self.on_save_button,
            corner_radius = 0,
            width         = ctk.CTkFont.measure(self.font_21, 'SAVE') + 20,
        )
        self.save_button.pack(side=ctk.TOP, padx=15, pady=15, expand=True)

    def center_window(self) -> None:
        """Function centering the TopLevel window. Screen size independent.
        """
        x: int = self.winfo_screenwidth()
        y: int = self.winfo_screenheight()
        app_width: int = self.winfo_width()
        app_height: int = self.winfo_height()
        self.geometry(f'+{(x//2)-(app_width)}+{(y//2)-(app_height)}')

    def get_save_name(self) -> str | None | bool:
        """Getter for user input from the entry widget.

        Returns:
            str | None | bool: String if name is valid, None if user decides to keep default save name and bool if canceled with closing window with ❌.
        """
        self.master.wait_window(self)
        return self.save_name

    def on_save_button(self) -> None:
        """Function checking if user entry is valid after clicking save button.
        """
        self.save_name = self.save_name_entry.get()
        files: list[str] = [f for f in os.listdir(resource_path('saves'))]
        if f'{self.save_name}.json' in files:
            self.save_name = None
        if isinstance(self.save_name, str) and len(self.save_name) < 1:
            self.save_name = None
        if isinstance(self.save_name, str) and self.save_name.startswith('chess_game_'):
            self.save_name = None
        self.destroy()

    def on_close(self) -> None:
        """Custom closing function ensuring proper closing of the window. Sets save_name to False to cancel saving.
        """
        self.save_name = False
        self.grab_release()
        self.destroy()
