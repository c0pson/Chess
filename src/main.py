import customtkinter as ctk

from properties import COLOR, SIZE

from cell import Board

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=COLOR.BACKGROUND)
        self.title('Chess')
        self.geometry(self.set_window_size())
        self.board = Board(self)
        self.board.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

    def set_window_size(self) -> str:
        center_pos: str = f'+{(self.winfo_screenwidth()-SIZE.WIDTH)//2}+150'
        return f'{int(SIZE.WIDTH)}x{int(SIZE.HEIGHT)}{center_pos}'

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
