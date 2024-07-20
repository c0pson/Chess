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
        self.is_occupied: bool = True if self.figure else False
        super().__init__(master=frame, image=figure_asset, text='', fg_color=color,
                        width=int(SIZE.IMAGE+2), height=int(SIZE.IMAGE+2), bg_color=COLOR.TRANSPARENT)
        self.bind('<Button-1>', self.on_click)
        self.pack(side=ctk.LEFT, padx=1, pady=1)

    def on_click(self, e):
        if self.figure:
            return self.board.handle_clicks(self.figure, self.position)
        print(self.position)
        return None

class Board(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color=COLOR.TRANSPARENT)
        self.board = self.create_board()
        self.previous_click: tuple[None, None] | tuple[int, int] = (None, None)
        self.clicked = False
        self.highlighted: list[Cell] = []

    def create_board(self) -> list[list[Cell]] | None:
        board: list[list[Cell]] = [[_ for _ in range(8)] for _ in range(8)]
        for i in range(8):
            new_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT)
            new_frame.pack(padx=0, pady=0)
            for j in range(8): # setup starting board
                if (i%2 and j%2) or (not i%2 and not j%2):
                    color = COLOR.TILE_1
                else:
                    color = COLOR.TILE_2
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
                elif (i,j) == (5, 5):
                    board[i][j] = Cell(new_frame, piece.Pawn('b', self, (i,j)), (i,j), color, self)
                elif (i,j) == (4, 2):
                    board[i][j] = Cell(new_frame, piece.Pawn('b', self, (i,j)), (i,j), color, self)
                else:
                    board[i][j] = Cell(new_frame, None, (i,j), color, self)
        return board if not None in board else None

    def handle_clicks(self, figure: piece.Piece, position: tuple[int, int]):
        possible_moves: list[tuple[int, int]] | None = figure.check_possible_moves()
        if possible_moves == []:
            return
        if self.highlighted:
            for cell in self.highlighted:
                if (cell.position[0]%2 and cell.position[1]%2) or (not cell.position[0]%2 and not cell.position[1]%2):
                    color = COLOR.TILE_1
                else:
                    color = COLOR.TILE_2
                cell.configure(fg_color=color)
        if self.board and possible_moves:
            for coords in possible_moves:
                self.board[coords[0]][coords[1]].configure(fg_color=COLOR.TEXT)
                self.highlighted.append(self.board[coords[0]][coords[1]])
