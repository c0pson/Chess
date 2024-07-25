import customtkinter as ctk
import subprocess
import platform
import os

from tools import get_from_config, change_config, load_menu_image, resource_path
from notifications import Notification
from properties import COLOR, STRING
from piece import Piece

class MovesRecord(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.font = ctk.CTkFont('Tiny5', 32)
        self.create_frames()
        self.moves: list[list[str]] = []

    def record_move(self, moved_piece: Piece, previous_coords: tuple[int, int] | None = None, capture: bool = False, castle: str | None = None, check: bool = False, checkmate: bool = False, promotion: str = '') -> None:
        y_axis: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        x, y = 8 - moved_piece.position[0], y_axis[moved_piece.position[1]]
        prev_x = 8 - previous_coords[0] if previous_coords else ''
        prev_y = y_axis[previous_coords[1]] if previous_coords else ''
        piece_name = moved_piece.__class__.__name__[0] if not moved_piece.__class__.__name__ == 'Pawn' else ''
        if not castle:
            notation = f' {'+' if check and not checkmate else ''}{'#' if checkmate else ''}{'x' if capture else ''}{piece_name}{prev_y}{prev_x}-{y}{x}{promotion if promotion else ''}'
        else:
            notation = f' {'+' if check and not checkmate else''}{'#' if checkmate else ''}{'0-0-0' if castle == 'queenside' else '0-0'}'
        current_frame = self.white_scroll_frame if moved_piece.color == 'w' else self.black_scroll_frame
        ctk.CTkLabel(current_frame, text=notation, font=self.font).pack(side=ctk.BOTTOM)

    def create_frames(self) -> None:
        black_label = ctk.CTkLabel(self, text='Black', font=self.font, text_color=COLOR.DARK_TEXT)
        black_label.pack(side=ctk.TOP, padx=1, pady=1)
        additional_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT, corner_radius=0,
                                        border_color=COLOR.DARK_TEXT, border_width=4)
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.black_scroll_frame = ctk.CTkScrollableFrame(additional_frame, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_B,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_B, corner_radius=0,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_B,)
        self.black_scroll_frame.pack(side=ctk.TOP, padx=3, pady=4, fill=ctk.Y, expand=True)
        white_label = ctk.CTkLabel(self, text='White', font=self.font, text_color=COLOR.TEXT)
        white_label.pack(side=ctk.TOP, padx=0, pady=0)
        additional_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT, corner_radius=0,
                                        border_color=COLOR.DARK_TEXT, border_width=4)
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.white_scroll_frame = ctk.CTkScrollableFrame(additional_frame, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_W,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_W, corner_radius=0,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_W)
        self.white_scroll_frame.pack(side=ctk.TOP, padx=3, pady=4, fill=ctk.Y, expand=True)
        space_label = ctk.CTkLabel(self, text='\n')
        space_label.pack()

    def restart(self) -> None:
        for child in self.white_scroll_frame.winfo_children():
            child.destroy()
        for child in self.black_scroll_frame.winfo_children():
            child.destroy()

class Options(ctk.CTkFrame):
    def __init__(self, master, restart_func, update_assets_func):
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.restart_func = restart_func
        self.update_assets_func = update_assets_func
        self.setting_icon = load_menu_image('settings')
        self.replay_icon = load_menu_image('replay')
        self.setting_button()
        self.space_label()
        self.replay_button()

    def setting_button(self) -> None:
        self.s_icon_label = ctk.CTkLabel(self, text='', image=self.setting_icon)
        self.s_icon_label.pack(side=ctk.TOP, padx=10, pady=5)
        self.s_icon_label.bind('<Button-1>', self.open_settings)

    def replay_button(self) -> None:
        self.r_icon_label = ctk.CTkLabel(self, text='', image=self.replay_icon)
        self.r_icon_label.pack(side=ctk.TOP, padx=10, pady=0)
        self.r_icon_label.bind('<Button-1>', self.replay)

    def space_label(self) -> None:
        space = ctk.CTkLabel(self, text='\n')
        space.pack(padx=2, pady=2)

    def open_settings(self, event) -> None:
        self.settings = Settings(self.master, self.restart_func, self.update_assets_func)

    def replay(self, event) -> None:
        self.r_icon_label.unbind('<Button-1>')
        self.restart_func()
        self.r_icon_label.bind('<Button-1>', self.cooldown)
        self.master.after(1990, lambda: self.r_icon_label.unbind('<Button-1>'))
        self.master.after(2000, lambda: self.r_icon_label.bind('<Button-1>', self.replay))

    def cooldown(self, event) -> None:
        self.notification = Notification(self.master, 'Not so fast', 1, 'top')

class Settings(ctk.CTkFrame):
    def __init__(self, master, restart_func, update_assets_func) -> None:
        super().__init__(master, fg_color=COLOR.BACKGROUND, corner_radius=0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.close_image = load_menu_image('close')
        self.close_button()
        self.choose_theme()
        self.open_assets_folder()
        self.previous_theme: None | str = None
        self.choice: None | str = None
        self.restart_func = restart_func
        self.update_assets_func = update_assets_func

    @staticmethod
    def list_directories_os(path) -> list:
        try:
            entries = os.listdir(path)
            directories = [
                entry for entry in entries
                if os.path.isdir(os.path.join(path, entry)) and os.listdir(os.path.join(path, entry))
            ]
            return directories
        except FileNotFoundError:
            return []

    def close_button(self) -> None:
        top_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT)
        top_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.X)
        settings_text = ctk.CTkLabel(top_frame, text='Settings', font=ctk.CTkFont('Tiny5', 38),
                                    text_color=COLOR.DARK_TEXT, anchor=ctk.N)
        settings_text.pack(side=ctk.LEFT, padx=20, anchor=ctk.NW)
        close_button = ctk.CTkLabel(top_frame, text='', font=ctk.CTkFont('Tiny5', 24),
                                    image=self.close_image, anchor=ctk.S)
        close_button.bind('<Button-1>', self.on_close)
        close_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10, pady=10)

    def create_theme_button(self, frame, theme: str) -> None:
        theme_button = ctk.CTkButton(frame, text=theme, command=lambda: self.select_theme(theme),
                                        font=ctk.CTkFont('Tiny5', 30), corner_radius=0,
                                        fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_1)
        theme_button.pack(side=ctk.LEFT, padx=4, pady=4, expand=True)

    def choose_theme(self) -> None:
        self.previous_theme = str(get_from_config('theme'))
        themes = self.list_directories_os('assets')
        if not themes:
            return
        text = ctk.CTkLabel(self, text='Themes: ', font=ctk.CTkFont('Tiny5', 32), text_color=COLOR.TEXT)
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        themes.remove('menu') if 'menu' in themes else themes
        frame = ctk.CTkScrollableFrame(self, fg_color=COLOR.TILE_2, scrollbar_button_color=COLOR.DARK_TEXT,
                                        scrollbar_button_hover_color=COLOR.DARK_TEXT, orientation=ctk.HORIZONTAL,
                                        height=70, corner_radius=0, scrollbar_fg_color=COLOR.DARK_TEXT)
        frame.pack(side=ctk.TOP, padx=80, pady=5, anchor=ctk.W, fill=ctk.X)
        for theme in themes:
            self.create_theme_button(frame, theme)
        warning_text = ctk.CTkLabel(self, text=STRING.ASSETS_WARNING, font=ctk.CTkFont('Tiny5', 18),
                                    text_color=COLOR.CLOSE)
        warning_text.pack(side=ctk.TOP, anchor=ctk.SW, padx=100, pady=0)

    def select_theme(self, choice: str) -> None:
        self.choice = choice
        change_config('theme', choice)

    def on_close(self, event) -> None:
        if not self.previous_theme and not self.choice:
            self.destroy()
            return
        if self.previous_theme == self.choice:
            self.restart_func
        self.update_assets_func()
        self.destroy()

    @staticmethod
    def open_file_explorer(path: str):
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':
            subprocess.run(['open', path])
        elif system == 'Linux':
            subprocess.run(['xdg-open', path])

    def open_assets_folder(self) -> None:
        additional_frame = ctk.CTkFrame(self, fg_color=COLOR.TILE_2, corner_radius=0)
        additional_frame.pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)
        text_label = ctk.CTkLabel(additional_frame, text='Open assets folder', text_color=COLOR.TEXT,
                                    font=ctk.CTkFont('Tiny5', 32))
        text_label.pack(side=ctk.LEFT, padx=10, pady=4, anchor=ctk.NW)
        open_button = ctk.CTkButton(additional_frame, text='OPEN', font=ctk.CTkFont('Tiny5', 20),
                                    text_color=COLOR.TEXT, command=lambda: self.open_file_explorer('assets'),
                                    fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_2,
                                    corner_radius=0)
        open_button.pack(side=ctk.RIGHT, padx=10, pady=4, anchor=ctk.E)
        path_text = ctk.CTkLabel(additional_frame, text=resource_path('assets'), text_color=COLOR.DARK_TEXT,
                                font=ctk.CTkFont('Tiny5', 18))
        path_text.pack(side=ctk.TOP, anchor=ctk.CENTER, padx=100, pady=15)
