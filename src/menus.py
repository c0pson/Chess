from fontTools.ttLib import TTFont
import customtkinter as ctk
import subprocess
import platform
import os
import re

from tools import get_from_config, change_config, load_menu_image, resource_path, change_color
from properties import COLOR, STRING, refresh_color_enum
from notifications import Notification
from color_picker import ColorPicker
from piece import Piece, Knight

class MovesRecord(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.create_frames()
        self.moves: list[list[str]] = []

    def record_move(self, moved_piece: Piece, previous_coords: tuple[int, int] | None = None, capture: bool = False, castle: str | None = None, check: bool = False, checkmate: bool = False, promotion: str = '') -> None:
        y_axis: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        x, y = 8 - moved_piece.position[0], y_axis[moved_piece.position[1]]
        prev_x = 8 - previous_coords[0] if previous_coords else ''
        prev_y = y_axis[previous_coords[1]] if previous_coords else ''
        if not isinstance(moved_piece, Knight):
            piece_name = moved_piece.__class__.__name__[0] if not moved_piece.__class__.__name__ == 'Pawn' else ''
        else:
            piece_name = 'N'
        if not castle:
            notation = f' {'+' if check and not checkmate else ''}{'#' if checkmate else ''}{'x' if capture else ''}{piece_name}{prev_y}{prev_x}-{y}{x}{promotion if promotion != 'K' else 'N'}'
        else:
            notation = f' {'+' if check and not checkmate else''}{'#' if checkmate else ''}{'0-0-0' if castle == 'queenside' else '0-0'}'
        current_frame = self.white_scroll_frame if moved_piece.color == 'w' else self.black_scroll_frame
        ctk.CTkLabel(current_frame, text=notation, font=ctk.CTkFont(str(get_from_config('font_name')), 32)).pack(side=ctk.BOTTOM)

    def create_frames(self) -> None:
        black_label = ctk.CTkLabel(self, text='Black', font=ctk.CTkFont(str(get_from_config('font_name')), 32), text_color=COLOR.DARK_TEXT)
        black_label.pack(side=ctk.TOP, padx=1, pady=1)
        additional_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT, corner_radius=0,
                                        border_color=COLOR.DARK_TEXT, border_width=7)
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.black_scroll_frame = ctk.CTkScrollableFrame(additional_frame, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_B,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_B, corner_radius=0,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_B,)
        self.black_scroll_frame.pack(side=ctk.TOP, padx=6, pady=7, fill=ctk.Y, expand=True)
        white_label = ctk.CTkLabel(self, text='White', font=ctk.CTkFont(str(get_from_config('font_name')), 32), text_color=COLOR.TEXT)
        white_label.pack(side=ctk.TOP, padx=0, pady=0)
        additional_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT, corner_radius=0,
                                        border_color=COLOR.DARK_TEXT, border_width=7)
        additional_frame.pack(side=ctk.TOP, padx=15, expand=True, fill=ctk.Y)
        self.white_scroll_frame = ctk.CTkScrollableFrame(additional_frame, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_W,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_W, corner_radius=0,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_W)
        self.white_scroll_frame.pack(side=ctk.TOP, padx=6, pady=7, fill=ctk.Y, expand=True)
        space_label = ctk.CTkLabel(self, text='\n')
        space_label.pack()

    def restart(self) -> None:
        for child in self.white_scroll_frame.winfo_children():
            child.destroy()
        for child in self.black_scroll_frame.winfo_children():
            child.destroy()

class Options(ctk.CTkFrame):
    def __init__(self, master, restart_func, update_assets_func, update_font_func):
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.restart_func = restart_func
        self.update_assets_func = update_assets_func
        self.update_font_func = update_font_func
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
        self.settings = Settings(self.master, self.restart_func, self.update_assets_func, self.update_font_func)

    def replay(self, event) -> None:
        self.r_icon_label.unbind('<Button-1>')
        self.restart_func()
        self.r_icon_label.bind('<Button-1>', self.cooldown)
        self.master.after(1990, lambda: self.r_icon_label.unbind('<Button-1>'))
        self.master.after(2000, lambda: self.r_icon_label.bind('<Button-1>', self.replay))

    def cooldown(self, event) -> None:
        self.notification = Notification(self.master, 'Not so fast', 1, 'top')

class Settings(ctk.CTkFrame):
    def __init__(self, master, restart_func, update_assets_func, update_font_func) -> None:
        super().__init__(master, fg_color=COLOR.BACKGROUND, corner_radius=0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.close_image = load_menu_image('close')
        self.color_picker_image = load_menu_image('colorpicker', resize=2)
        self.close_button()
        self.scrollable_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color=COLOR.BACKGROUND,
                                                        scrollbar_button_color=COLOR.DARK_TEXT)
        self.scrollable_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.BOTH, expand=True)
        self.font_name: str = str(get_from_config('font_name'))
        self.choose_theme()
        self.choose_font()
        self.open_assets_folder()
        self.change_colors()
        self.previous_theme: None | str = None
        self.choice: None | str = None
        self.restart_func = restart_func
        self.update_assets_func = update_assets_func
        self.update_font_func = update_font_func
        ctk.CTkLabel(self, text='', height=18, fg_color=COLOR.BACKGROUND).pack(padx=0, pady=0)

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
        settings_text = ctk.CTkLabel(top_frame, text='Settings', font=ctk.CTkFont(str(get_from_config('font_name')), 38),
                                    text_color=COLOR.DARK_TEXT, anchor=ctk.N)
        settings_text.pack(side=ctk.LEFT, padx=20, anchor=ctk.NW)
        close_button = ctk.CTkLabel(top_frame, text='', font=ctk.CTkFont(str(get_from_config('font_name')), 24),
                                    image=self.close_image, anchor=ctk.S)
        close_button.bind('<Button-1>', self.on_close)
        close_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10, pady=10)

    def create_theme_button(self, frame, theme: str) -> None:
        theme_button = ctk.CTkButton(frame, text=theme, command=lambda: self.select_theme(theme),
                                        font=ctk.CTkFont(str(get_from_config('font_name')), 30), corner_radius=0,
                                        fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_1,
                                        text_color=COLOR.TEXT)
        theme_button.pack(side=ctk.LEFT, padx=4, pady=4, expand=True)

    def choose_theme(self) -> None:
        self.previous_theme = str(get_from_config('theme'))
        themes = self.list_directories_os('assets')
        if not themes:
            return
        text = ctk.CTkLabel(self.scrollable_frame, text='Themes: ', font=ctk.CTkFont(str(get_from_config('font_name')), 32), text_color=COLOR.TEXT)
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        themes.remove('menu') if 'menu' in themes else themes
        frame = ctk.CTkScrollableFrame(self.scrollable_frame, fg_color=COLOR.TILE_2, scrollbar_button_color=COLOR.DARK_TEXT,
                                        orientation=ctk.HORIZONTAL,
                                        height=70, corner_radius=0)
        frame.pack(side=ctk.TOP, padx=80, pady=5, anchor=ctk.W, fill=ctk.X)
        for theme in themes:
            self.create_theme_button(frame, theme)
        warning_text = ctk.CTkLabel(self.scrollable_frame, text=STRING.ASSETS_WARNING, font=ctk.CTkFont(str(get_from_config('font_name')), 18),
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

    @staticmethod
    def get_all_files(path: str) -> list[str]:
        path = resource_path(path)
        try:
            all_files = [os.path.join((path), f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return all_files
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @staticmethod
    def get_font_name(ttf_path) -> str | None:
        try:
            font = TTFont(ttf_path)
            name = ""
            for record in font['name'].names:
                if record.nameID == 4:
                    if b'\000' in record.string:
                        name = record.string.decode('utf-16-be')
                    else:
                        name = record.string.decode('utf-8')
                    break
            return name
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def open_assets_folder(self) -> None:
        text_label = ctk.CTkLabel(self.scrollable_frame, text='Open assets folder', text_color=COLOR.TEXT,
                                    font=ctk.CTkFont(str(get_from_config('font_name')), 32))
        text_label.pack(side=ctk.TOP, padx=75, pady=4, anchor=ctk.NW)
        additional_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=COLOR.TILE_2, corner_radius=0)
        additional_frame.pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)
        open_button = ctk.CTkButton(additional_frame, text='OPEN', font=ctk.CTkFont(str(get_from_config('font_name')), 20),
                                    text_color=COLOR.TEXT, command=lambda: self.open_file_explorer('assets'),
                                    fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_2,
                                    corner_radius=0)
        open_button.pack(side=ctk.RIGHT, padx=10, pady=4, anchor=ctk.E)
        path_text = ctk.CTkLabel(additional_frame, text=resource_path('assets'), text_color=COLOR.DARK_TEXT,
                                font=ctk.CTkFont(str(get_from_config('font_name')), 18))
        path_text.pack(side=ctk.LEFT, padx=15, pady=15)
        ctk.CTkLabel(self.scrollable_frame, fg_color=COLOR.DARK_TEXT, text='', corner_radius=0, height=16).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)

    def choose_font(self) -> None:
        self.previous_font = str(get_from_config('font_file_name'))
        fonts = self.get_all_files('fonts')
        if not fonts:
            return
        text = ctk.CTkLabel(self.scrollable_frame, text='Fonts: ', font=ctk.CTkFont(str(get_from_config('font_name')), 32), text_color=COLOR.TEXT)
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        frame = ctk.CTkScrollableFrame(self.scrollable_frame, fg_color=COLOR.TILE_2, scrollbar_button_color=COLOR.DARK_TEXT,
                                        orientation=ctk.HORIZONTAL, height=70, corner_radius=0, scrollbar_fg_color=COLOR.DARK_TEXT)
        frame.pack(side=ctk.TOP, padx=80, pady=5, anchor=ctk.W, fill=ctk.X)
        for font in fonts:
            self.create_font_button(frame, font)

    def create_font_button(self, frame, font) -> None:
        font_button = ctk.CTkButton(frame, text=self.get_font_name(font),
                                        command=lambda: self.select_font(font),
                                        font=ctk.CTkFont(str(get_from_config('font_name')), 30), corner_radius=0,
                                        fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_1,
                                        text_color=COLOR.TEXT)
        font_button.pack(side=ctk.LEFT, padx=4, pady=4, expand=True)

    def select_font(self, font) -> None:
        if os.path.basename(font) == self.previous_font:
            return
        if new_font := self.get_font_name(font):
            change_config('font_name', new_font)
            change_config('font_file_name', os.path.basename(font))
            self.update_font_func()
            self.previous_font = str(get_from_config('font_file_name'))

    @staticmethod
    def is_valid_color(color):
        hex_color_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        return bool(hex_color_pattern.match(color))

    @staticmethod
    def validate_length(new_value):
        return len(new_value) <= 7

    def change_colors(self) -> None:
        text = ctk.CTkLabel(self.scrollable_frame, text='Colors: ', font=ctk.CTkFont(str(get_from_config('font_name')), 32), text_color=COLOR.TEXT)
        text.pack(side=ctk.TOP, anchor=ctk.SW, padx=75, pady=0)
        warning_text = ctk.CTkLabel(self.scrollable_frame, text=STRING.COLORS_WARNING, font=ctk.CTkFont(str(get_from_config('font_name')), 18),
                                    text_color=COLOR.CLOSE)
        warning_text.pack(side=ctk.TOP, anchor=ctk.SW, padx=100, pady=0)
        frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=0, fg_color=COLOR.TILE_2)
        frame.pack(side=ctk.TOP, padx=80, pady=0, anchor=ctk.W, fill=ctk.X)
        ctk.CTkLabel(frame, text='', height=2).pack(padx=0, pady=0)
        for color in COLOR:
            self.color_label(frame, color) if color != 'transparent' else ...
        ctk.CTkLabel(frame, text='', height=2).pack(padx=0, pady=0)
        ctk.CTkLabel(self.scrollable_frame, fg_color=COLOR.DARK_TEXT, text='', corner_radius=0, height=16).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)
        ctk.CTkLabel(self.scrollable_frame, fg_color=COLOR.TRANSPARENT, text='', corner_radius=0, height=16).pack(side=ctk.TOP, padx=80, pady=0, fill=ctk.X)

    def color_label(self, frame, color: str) -> None:
        for color_name , color_str in COLOR.__members__.items():
            if color_str == color:
                name_of_color = color_name
                break
        color_frame = ctk.CTkFrame(frame, fg_color=COLOR.NOTATION_BACKGROUND_B, corner_radius=0)
        color_frame.pack(side=ctk.TOP, padx=10, pady=4, fill=ctk.X)
        vcmd = (self.register(self.validate_length), '%P')
        color_entry = ctk.CTkEntry(color_frame, border_width=0, corner_radius=0, fg_color=color,
                                                font=ctk.CTkFont(get_from_config('font_name'), 20),
                                                validate='key', validatecommand=vcmd,
                                                text_color=COLOR.TEXT if color != COLOR.TEXT else COLOR.DARK_TEXT)
        color_entry.insert(0, color)
        rgb_color = color.lstrip('#')
        r = int(rgb_color[0:2], 16)
        g = int(rgb_color[2:4], 16)
        b = int(rgb_color[4:6], 16)
        color_picker = ctk.CTkLabel(color_frame, text='', image=self.color_picker_image)
        color_picker.pack(side=ctk.LEFT, padx=5, pady=4)
        color_picker.bind('<Button-1>', lambda e: self.ask_for_color(r, g, b, color_entry, color_name))
        color_entry.pack(side=ctk.LEFT, padx=10, pady=4)
        ok_button = ctk.CTkButton(color_frame, text='OK', font=ctk.CTkFont(get_from_config('font_name'), 20),
                                    command=lambda: self.save_color(color_name, color_entry, color_entry),width=50,
                                    corner_radius=0, fg_color=COLOR.TILE_1, hover_color=COLOR.HIGH_TILE_2,
                                    text_color=COLOR.TEXT)
        ok_button.pack(side=ctk.LEFT, padx=10, pady=4)
        cancel_button = ctk.CTkButton(color_frame, text='CANCEL', font=ctk.CTkFont(get_from_config('font_name'), 20),
                                    command=lambda: self.cancel(color_name, color_entry, color), width=50,
                                    corner_radius=0, fg_color=COLOR.CLOSE, hover_color=COLOR.CLOSE_HOVER,
                                    text_color=COLOR.TEXT)
        cancel_button.pack(side=ctk.LEFT, padx=10, pady=4)
        color_name_label = ctk.CTkLabel(color_frame, text=name_of_color, text_color=COLOR.TEXT,
                                        font=ctk.CTkFont(get_from_config('font_name'), 22))
        color_name_label.pack(side=ctk.RIGHT, padx=4, pady=4)

    def save_color(self, color_name: str, entry: ctk.CTkEntry, color_label: ctk.CTkLabel) -> None:
        new_color = entry.get()
        if self.is_valid_color(new_color):
            change_color(color_name, new_color)
            color_label.configure(fg_color=new_color)

    def ask_for_color(self, r, g, b, entry: ctk.CTkEntry, color_name: str) -> None:
        picker = ColorPicker(fg_color=COLOR.BACKGROUND, r=r, g=g, b=b, font=ctk.CTkFont(self.font_name, 15))
        # self.master.after(201, lambda: picker.iconbitmap(resource_path('assets\\logo.ico')))
        color = picker.get_color()
        if color:
            entry.delete(0, ctk.END)
            entry.insert(0, color)
            change_color(color_name, color)
            entry.configure(fg_color=color)

    def cancel(self, color_name: str, entry: ctk.CTkEntry, color: str) -> None:
        entry.delete(0, ctk.END)
        entry.insert(0, color)
        change_color(color_name, color)
        entry.configure(fg_color=color)
