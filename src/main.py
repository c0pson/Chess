"""Main file of Chess game entirely made in python with properly working game engine. Contains a lot of customization option for user.
App allows using custom assets, fonts and colors. Comes with easy to use menu to change the properties and readable config file.

Libraries used: 
 - customtkinter
 - threading
 - os
 - sys
 - platform
 - configparser
 - Pillow [PIL]
 - re [regex]
 - fontTools
 - subprocess
 - pywinstyles
 - built in libraries
 - sounddevice
 - soundfile

Link to full documentation: http://chess-documentation.ct.ws/
"""

import customtkinter as ctk
import os
import threading
from concurrent.futures import ThreadPoolExecutor

from tools import resource_path, get_from_config
from properties import COLOR, SYSTEM
from menus import MovesRecord, Options
from board import Board

class MainWindow(ctk.CTk):
    """Main class handling the app. Setting size, minimum size, font loading, icon setting,
    updating font, updating assets and restarting the game all happens here.

    Args:
        ctk.CTk : Main app window of customtkinter library (master).
    """
    def __init__(self) -> None:
        """Constructor for the MainWindow class: 
             - sets title
             - sets geometry
             - sets minimum size of the window
             - loads font
             - Creates instances of the classes:
              - MoveRecord
              - Options
              - Board
             - loads theme of the app from the config: get_from_config
        """
        super().__init__(fg_color=COLOR.BACKGROUND)
        self.title('Chess')
        self.geometry(self.set_window_size())
        size: int = int(get_from_config('size'))
        self.minsize(((size + 2) * 10 + 40)+ 400, ((size + 2) * 10 + 40))
        self.load_font()
        self.moves_record: MovesRecord = MovesRecord(self)
        self.moves_record.pack(side=ctk.RIGHT, padx=10, pady=10, fill=ctk.Y)
        self.options: Options = Options(self, self.restart_game, self.update_assets, self.update_font, self.get_board)
        self.options.pack(side=ctk.LEFT, padx=10, pady=10, fill=ctk.Y)
        self.board: Board = Board(self, self.moves_record, size)
        self.theme: str = str(get_from_config('theme'))
        self.set_icon()

    def load_font(self) -> None:
        """Function loads font independently on the users operating system.
        """
        font: str = str(get_from_config('font_file_name'))
        if SYSTEM == 'Windows':
            ctk.FontManager.windows_load_font(resource_path(os.path.join('fonts', font)))
        else:
            ctk.FontManager.load_font(resource_path(os.path.join('fonts', font)))

    def set_icon(self) -> None:
        """Only for windows machines logo icon will be set due to lack of implementation for linux and mac.
        """
        if SYSTEM == 'Windows':
            self.iconbitmap(resource_path(os.path.join('assets', 'logo.ico')))

    def set_window_size(self) -> str:
        """Calculates the size necessary to display all elements of the app on the screen.

        Returns:
            str: f'{width}x{height]}' because customtkinter uses f'{width}x{height]}' to set the size of the window.
        """
        size: int = int(get_from_config('size'))
        size = (size+2) * 10 + 40
        center_pos: str = f'+{(self.winfo_screenwidth()-(int(size*1.5)))//2}+{(self.winfo_screenheight()-(int(size)*1.1))//2}'
        return f'{size + 300}x{size}{center_pos}'

    def restart_game(self) -> None:
        """Helper function for game restart just by calling functions from Board and MoveRecord classes.
        """
        self.board.restart_game()
        self.moves_record.restart()

    def update_assets(self) -> None:
        """Updates asset on the Board using thread to avoid window freezing.
        """
        for row in self.board.board:
            for cell in row:
                if cell.figure:
                    threading.Thread(target=cell.figure.update_image).start()

    def get_board(self) -> Board:
        """Getter for board object.

        Returns:
            Board: Board object.
        """
        return self.board

    def update_font(self, widget=None) -> None:
        """Helper function updating the font during app runtime without freezing the window.

        Args:
            widget (Any, optional): Child of the widget. Defaults to None as master widget doesn't have any parents.
        """
        if widget is None:
            widget = self
            self.load_font()
        def thread_task():
            widgets = []
            queue = [widget]
            while queue:
                current_widget = queue.pop()
                widgets.append(current_widget)
                queue.extend(current_widget.winfo_children())
            with ThreadPoolExecutor() as executor:
                for child in widgets:
                    if isinstance(child, ctk.CTkLabel | ctk.CTkButton):
                        size = child.cget('font').cget('size')
                        executor.submit(self.__update_font_on_main_thread, child, size)
        threading.Thread(target=thread_task, daemon=True).start()

    def __update_font_on_main_thread(self, widget, size: int) -> None:
        self.after(0, lambda: widget.configure(font=ctk.CTkFont(get_from_config('font_name'), size)))

if __name__ == "__main__":
    ctk.deactivate_automatic_dpi_awareness()
    app = MainWindow()
    app.mainloop()
