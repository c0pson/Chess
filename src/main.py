import customtkinter as ctk
import os
import threading

from tools import resource_path, get_from_config
from properties import COLOR

from menus import MovesRecord, Options
from cell import Board

class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=COLOR.BACKGROUND)
        self.title('Chess')
        self.geometry(self.set_window_size())
        size = int(get_from_config('size'))
        self.minsize(((size + 2) * 10 + 40)+ 400, ((size + 2) * 10 + 40))
        self.load_font()
        self.moves_record = MovesRecord(self)
        self.moves_record.pack(side=ctk.RIGHT, padx=10, pady=10, fill=ctk.Y)
        self.options = Options(self, self.restart_game, self.update_assets, self.update_font)
        self.options.pack(side=ctk.LEFT, padx=10, pady=10, fill=ctk.Y)
        self.board = Board(self, self.moves_record, size)
        self.board.pack(side=ctk.RIGHT, padx=10, pady=10, expand=True, ipadx=5, ipady=5, anchor=ctk.CENTER)
        self.theme: str = str(get_from_config('theme'))
        self.set_icon()

    def load_font(self) -> None:
        font = get_from_config('font_file_name')
        if os.name == 'nt':
            ctk.FontManager.windows_load_font(resource_path(f'fonts\\{font}'))
        else:
            ctk.FontManager.load_font(resource_path(f'fonts/{font}'))

    def set_icon(self) -> None:
        if os.name == 'nt':
            self.iconbitmap(resource_path('assets\\logo.ico'))

    def set_window_size(self) -> str:
        size: int = int(get_from_config('size'))
        size = (size+2) * 10 + 40
        center_pos: str = f'+{(self.winfo_screenwidth()-(int(size*1.5)))//2}+75'
        return f'{size + 300}x{size}{center_pos}'

    def restart_game(self) -> None:
        self.board.restart_game()
        self.moves_record.restart()

    def update_assets(self) -> None:
        for row in self.board.board:
            for cell in row:
                if cell.figure:
                    cell.figure.update_image()

    def update_font(self, widget=None):
        if widget is None:
            widget = self
            self.load_font()

        def thread_task():
            children = widget.winfo_children()
            for child in children:
                if isinstance(child, ctk.CTkLabel) or isinstance(child, ctk.CTkButton):
                    size = child.cget('font').cget('size')
                    self.update_font_on_main_thread(child, size)

                self.update_font(child)

        threading.Thread(target=thread_task).start()

    def update_font_on_main_thread(self, widget, size):
        self.after(0, lambda: widget.configure(font=ctk.CTkFont(get_from_config('font_name'), size)))

if __name__ == "__main__":
    ctk.deactivate_automatic_dpi_awareness()
    app = MainWindow()
    app.mainloop()
