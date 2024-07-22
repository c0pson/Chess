import customtkinter as ctk
import os

from properties import COLOR, SIZE
from tools import resource_path

from cell import Board

class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=COLOR.BACKGROUND)
        self.title('Chess')
        self.geometry(self.set_window_size())
        self.load_font()
        self.board = Board(self)
        self.board.pack(padx=10, pady=10, expand=True)
        self.theme: str = 'casual'

    def load_font(self) -> None:
        if os.name == 'nt':
            ctk.FontManager.windows_load_font(resource_path('fonts\\Tiny5-Regular.ttf'))
        else:
            ctk.FontManager.windows_load_font(resource_path('fonts/Tiny5-Regular.ttf'))

    def set_window_size(self) -> str:
        center_pos: str = f'+{(self.winfo_screenwidth()-SIZE.WIDTH)//2}+150'
        return f'{int(SIZE.WIDTH)}x{int(SIZE.HEIGHT)}{center_pos}'

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
