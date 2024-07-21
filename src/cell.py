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
        self.previous_coords: tuple[int, int] | None = None
        self.current_turn = 'w'

    @staticmethod
    def determine_tile_color(pos: tuple[int, int]) -> str:
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

    def display_check_message(self):
        pass

    def handle_clicks(self, figure: piece.Piece, position: tuple[int, int]) -> None:
        possible_moves = figure.check_possible_moves(self.current_turn)
        if not possible_moves and self.board[position[0]][position[1]].figure:
            return
        self.clicked_figure = figure if figure else None
        self.previous_coords = position
        if self.highlighted:
            self.remove_highlights()
        if self.board and possible_moves:
            valid_moves = []
            for coords in possible_moves:
                if not self.check_check(position, coords):
                    self.display_check_message()
                    valid_moves.append(coords)
            for coords in valid_moves:
                color = self.board[coords[0]][coords[1]].cget('fg_color')
                new_color = COLOR.HIGH_TILE_1 if color == COLOR.TILE_1 else COLOR.HIGH_TILE_2
                self.board[coords[0]][coords[1]].configure(fg_color=new_color)
                self.highlighted.append(self.board[coords[0]][coords[1]])

    def check_check(self, move_from: tuple[int, int], move_to: tuple[int, int]) -> bool:
        original_from_figure = self.board[move_from[0]][move_from[1]].figure
        original_to_figure = self.board[move_to[0]][move_to[1]].figure
        self.board[move_to[0]][move_to[1]].figure = original_from_figure
        self.board[move_from[0]][move_from[1]].figure = None
        king_position = None
        if isinstance(original_from_figure, piece.King):
            king_position = move_to
        else:
            for row in self.board:
                for cell in row:
                    if isinstance(cell.figure, piece.King) and cell.figure.color == self.current_turn:
                        king_position = cell.figure.position
                        break
                if king_position:
                    break
        is_in_check = False
        for row in self.board:
            for cell in row:
                if cell.figure and cell.figure.color != self.current_turn:
                    possible_moves = cell.figure.check_possible_moves(cell.figure.color)
                    if king_position in possible_moves:
                        is_in_check = True
                        break
            if is_in_check:
                break
        self.board[move_from[0]][move_from[1]].figure = original_from_figure
        self.board[move_to[0]][move_to[1]].figure = original_to_figure
        return is_in_check

    def handle_move(self, position: tuple[int, int]) -> None:
        if self.clicked_figure and self.previous_coords:
            row, col = position
            cell = self.board[row][col]
            if cell in self.highlighted and self.previous_coords != position:
                if not self.check_check(self.previous_coords, position):
                    cell.figure = self.clicked_figure
                    cell.figure.position = position
                    cell.update()
                    self.board[self.previous_coords[0]][self.previous_coords[1]].figure = None
                    self.board[self.previous_coords[0]][self.previous_coords[1]].update()
                    if isinstance(cell.figure, piece.Pawn):
                        cell.figure.promote()
                    if cell.figure.first_move:
                        cell.figure.first_move = False
                    self.current_turn = 'b' if self.current_turn == 'w' else 'w'
                else:
                    print("Move not allowed as it puts the king in check.")
            self.clicked_figure = None
            self.previous_coords = None
        self.remove_highlights()
