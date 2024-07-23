import customtkinter as ctk
import os

from tools import resource_path, get_from_config
from properties import COLOR

from menus import MovesRecord
from cell import Board

class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=COLOR.BACKGROUND)
        self.title('Chess')
        self.geometry(self.set_window_size())
        size = (int(get_from_config('size'))+2) * 9 + 40
        self.minsize(size, size)
        self.load_font()
        self.moves_record = MovesRecord(self)
        self.moves_record.pack(side=ctk.RIGHT, padx=10, pady=10, fill=ctk.Y)
        self.board = Board(self, self.moves_record)
        self.board.pack(side=ctk.RIGHT, padx=10, pady=10, expand=True)
        self.theme: str = 'casual'

    def load_font(self) -> None:
        if os.name == 'nt':
            ctk.FontManager.windows_load_font(resource_path('fonts\\Tiny5-Regular.ttf'))
        else:
            ctk.FontManager.windows_load_font(resource_path('fonts/Tiny5-Regular.ttf'))

    def set_window_size(self) -> str:
        size: int = int(get_from_config('size'))
        size = (size+2) * 9 + 40
        center_pos: str = f'+{(self.winfo_screenwidth()-size)//2}+75'
        return f'{size}x{size}{center_pos}'

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
