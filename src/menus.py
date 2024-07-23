import customtkinter as ctk

from properties import COLOR
from piece import Piece

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

class Options(ctk.CTkFrame):
    def __init__(self, master, board):
        super().__init__(master)

class Timer(ctk.CTkFrame):
    def __init__(self, master, board):
        super().__init__(master)
