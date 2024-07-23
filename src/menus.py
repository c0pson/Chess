import customtkinter as ctk

from tools import resource_path, get_from_config
from notifications import Notification
from properties import COLOR
from piece import Piece
from PIL import Image

class MovesRecord(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.font = ctk.CTkFont('Tiny5', 32)
        self.create_frames()
        self.moves: list[list[str]] = []

    def record_move(self, moved_piece: Piece, capture: bool = False, castle: str | None = None, check: bool = False, checkmate: bool = False) -> None:
        """castle: queenside | kingside"""
        x_axis: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        x, y = 8 - moved_piece.position[0], x_axis[moved_piece.position[1]]
        piece_name = moved_piece.__class__.__name__[0] if not moved_piece.__class__.__name__ == 'Pawn' else ''
        if not castle:
            notation = f'{'+' if check and not checkmate else ''}{'#' if checkmate else ''}{'x' if capture else ''}{piece_name}{y}{x}'
        else:
            notation = f'{'+' if check and not checkmate else''}{'#' if checkmate else ''}{'0-0-0' if castle == 'queenside' else '0-0'}'
        current_frame = self.white_scroll_frame if moved_piece.color == 'w' else self.black_scroll_frame
        ctk.CTkLabel(current_frame, text=notation, font=self.font).pack(side=ctk.BOTTOM)

    def create_frames(self) -> None:
        self.white_scroll_frame = ctk.CTkScrollableFrame(self, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_W,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_W,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_W)
        white_label = ctk.CTkLabel(self, text='White', font=self.font, text_color=COLOR.TEXT)
        self.black_scroll_frame = ctk.CTkScrollableFrame(self, scrollbar_button_color=COLOR.NOTATION_BACKGROUND_B,
                                                        fg_color=COLOR.NOTATION_BACKGROUND_B,
                                                        scrollbar_button_hover_color=COLOR.NOTATION_BACKGROUND_B)
        black_label = ctk.CTkLabel(self, text='Black', font=self.font, text_color=COLOR.DARK_TEXT)
        self.black_label = ctk.CTkLabel(self.white_scroll_frame, text='Black', font=self.font)
        black_label.pack(side=ctk.TOP, padx=1, pady=1)
        self.black_scroll_frame.pack(side=ctk.TOP, padx=2, pady=2, fill=ctk.Y, expand=True)
        white_label.pack(side=ctk.TOP, padx=1, pady=1)
        self.white_scroll_frame.pack(side=ctk.TOP, padx=2, pady=2, fill=ctk.Y, expand=True)
        space_label = ctk.CTkLabel(self, text='\n')
        space_label.pack()

    def restart(self) -> None:
        for child in self.white_scroll_frame.winfo_children():
            child.destroy()
        for child in self.black_scroll_frame.winfo_children():
            child.destroy()

class Options(ctk.CTkFrame):
    def __init__(self, master, restart_func):
        super().__init__(master, fg_color=COLOR.BACKGROUND)
        self.restart_func = restart_func
        self.setting_icon = self.load_image('settings')
        self.replay_icon = self.load_image('replay')
        self.setting_button()
        self.space_label()
        self.replay_button()

    def load_image(self, option: str) -> ctk.CTkImage | None:
        setting_icon_path = resource_path(f'assets\\menu\\{option}.png')
        try:
            size = int(get_from_config('size')) // 1.5
            setting_icon = Image.open(setting_icon_path).convert('RGBA')
            return ctk.CTkImage(light_image=setting_icon, dark_image=setting_icon, size=(size, size))
        except (FileNotFoundError, FileExistsError) as e:
            print(f'Couldn`t load image for due to error: {e}')
        return None

    def setting_button(self) -> None:
        self.s_icon_label = ctk.CTkLabel(self, text='', image=self.setting_icon)
        self.s_icon_label.pack()
        self.s_icon_label.bind('<Button-1>', self.open_settings)

    def replay_button(self) -> None:
        self.r_icon_label = ctk.CTkLabel(self, text='', image=self.replay_icon)
        self.r_icon_label.pack()
        self.r_icon_label.bind('<Button-1>', self.replay)

    def space_label(self) -> None:
        space = ctk.CTkLabel(self, text='\n')
        space.pack(padx=2, pady=2)

    def open_settings(self, event) -> None:
        print('settings')

    def replay(self, event) -> None:
        self.r_icon_label.unbind('<Button-1>')
        self.restart_func()
        self.r_icon_label.bind('<Button-1>', self.cooldown)
        self.master.after(1990, lambda: self.r_icon_label.unbind('<Button-1>'))
        self.master.after(2000, lambda: self.r_icon_label.bind('<Button-1>', self.replay))

    def cooldown(self, event) -> None:
        self.notification = Notification(self.master, 'Not so fast', 0.7, 'top')

class Timer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
