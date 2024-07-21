import customtkinter as ctk

from properties import COLOR, SIZE

import piece

class Cell(ctk.CTkLabel):
    def __init__(self, frame, figure: piece.Piece | None, position: tuple[int, int], color: str, board) -> None:
        self.frame = frame
        self.position = position
        self.board = board
        self.figure: None | piece.Piece = figure
        figure_asset = self.figure.image if self.figure else None
        super().__init__(master=frame, image=figure_asset, text='', fg_color=color,
                        width=int(SIZE.IMAGE+2), height=int(SIZE.IMAGE+2), bg_color=COLOR.TRANSPARENT)
        self.bind('<Button-1>', self.on_click)
        self.pack(side=ctk.LEFT, padx=0, pady=0)

    def on_click(self, e) -> None:
        if self.figure and not self.board.clicked_figure:
            self.board.handle_clicks(self.figure, self.position)
        else:
            self.board.handle_move(self.position)

    def update(self) -> None:
        figure_asset = self.figure.image if self.figure else ''
        self.configure(image=figure_asset)

class Board(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color=COLOR.TRANSPARENT)
        self.board = self.create_board()
        self.previous_click: tuple[None, None] | tuple[int, int] = (None, None)
        self.highlighted: list[Cell] = []
        self.clicked_figure: piece.Piece | None = None
        self.clicked_coords: tuple[int, int] | None = None
        self.current_turn = 'w'

    def determine_tile_color(self, pos: tuple[int, int]) -> str:
        if (pos[0]%2 and pos[1]%2) or (not pos[0]%2 and not pos[1]%2):
            return COLOR.TILE_1
        else:
            return COLOR.TILE_2

    def create_board(self) -> list[list[Cell]]:
        board: list[list[Cell]] = [[_ for _ in range(8)] for _ in range(8)]
        for i in range(8):
            new_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT)
            new_frame.pack(padx=0, pady=0)
            for j in range(8):
                color = self.determine_tile_color((i, j))
                if (i,j) == (0,0) or (i,j) == (0,7): # im so sorry for this
                    board[i][j] = Cell(new_frame, piece.Rook('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (7,0) or (i,j) == (7,7):
                    board[i][j] = Cell(new_frame, piece.Rook('w', self, (i,j)), (i,j), color, self)
                elif (i,j) == (0,1) or (i,j) == (0,6):
                    board[i][j] = Cell(new_frame, piece.Knight('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (7,1) or (i,j) == (7,6):
                    board[i][j] = Cell(new_frame, piece.Knight('w', self, (i,j)), (i,j), color, self)
                elif (i,j) == (0,2) or (i,j) == (0,5):
                    board[i][j] = Cell(new_frame, piece.Bishop('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (7,2) or (i,j) == (7,5):
                    board[i][j] = Cell(new_frame, piece.Bishop('w', self, (i,j)), (i,j), color, self)
                elif (i,j) == (0,3):
                    board[i][j] = Cell(new_frame, piece.Queen('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (7,3):
                    board[i][j] = Cell(new_frame, piece.Queen('w', self, (i,j)), (i,j), color, self)
                elif (i,j) == (0,4):
                    board[i][j] = Cell(new_frame, piece.King('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (7,4):
                    board[i][j] = Cell(new_frame, piece.King('w', self, (i,j)), (i,j), color, self)
                elif i == 1:
                    board[i][j] = Cell(new_frame, piece.Pawn('b', self, (i,j)), (i,j), color, self)
                elif i == 6:
                    board[i][j] = Cell(new_frame, piece.Pawn('w', self, (i,j)), (i,j), color, self)
                else:
                    board[i][j] = Cell(new_frame, None, (i,j), color, self)
        return board

    def remove_highlights(self) -> None:
        for cell in self.highlighted:
            color = self.determine_tile_color(cell.position)
            cell.configure(fg_color=color)
        self.highlighted = []

    def handle_clicks(self, figure: piece.Piece, position: tuple[int, int]) -> None:
        possible_moves: list[tuple[int, int]] | None = figure.check_possible_moves(self.current_turn)
        if not possible_moves and self.board[position[0]][position[1]].figure:
            return
        self.clicked_figure = figure if figure else None
        self.clicked_coords = position
        if self.board[position[0]][position[1]] in self.highlighted:
            pass
        if self.highlighted:
            self.remove_highlights()
        if self.board and possible_moves:
            for coords in possible_moves:
                self.board[coords[0]][coords[1]].configure(fg_color=COLOR.TEXT)
                self.highlighted.append(self.board[coords[0]][coords[1]])

    def handle_move(self, position: tuple[int, int]) -> None:
        if self.clicked_figure and self.clicked_coords:
            if  self.board[position[0]][position[1]] in self.highlighted and (self.clicked_coords != position):
                self.board[position[0]][position[1]].figure = self.clicked_figure
                self.board[position[0]][position[1]].figure.position = position # type: ignore
                self.board[position[0]][position[1]].update()
                self.board[self.clicked_coords[0]][self.clicked_coords[1]].figure = None
                self.board[self.clicked_coords[0]][self.clicked_coords[1]].update()
                if self.board[position[0]][position[1]].figure.first_move: # type: ignore
                    self.board[position[0]][position[1]].figure.first_move = False # type: ignore
                self.current_turn = 'b' if self.current_turn == 'w' else 'w'
            self.clicked_figure = None
            self.clicked_coords = None
        self.remove_highlights()
