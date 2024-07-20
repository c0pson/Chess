import customtkinter as ctk
from PIL import Image
import sys
import os

from properties import SIZE, COLOR

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Piece():
    def __init__(self, color: str, board, position) -> None:
        self.color = color
        self.board = board
        self.position = position
        self.image: ctk.CTkImage | None = None

    def check_possible_moves(self):
        raise NotImplementedError

    def load_image(self) -> None:
        piece_name = (self.__class__.__name__).lower()
        path: str = resource_path(f'assets\\{piece_name}_{self.color}.png')
        try: 
            loaded_image = Image.open(path).convert('RGBA')
            self.image = ctk.CTkImage(light_image=loaded_image, dark_image=loaded_image, size=(SIZE.IMAGE, SIZE.IMAGE))
        except (FileExistsError, FileNotFoundError) as e:
            print(f'Couldn`t load image for due to error: {e}')

    def __str__(self) -> str:
        return f'Piece: {self.__class__.__name__} Color: {'white' if self.color == 'w' else 'black'}'

class Pawn(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color # b | w
        self.position = position
        self.board = board
        self.load_image()
        self.first_move = True

    def check_possible_moves(self) -> list[tuple[int, int]]:
        move = 1 if self.color == 'b' else -1
        possible_moves = []
        if not self.board.board[self.position[0]+move][self.position[1]].is_occupied:
            possible_moves = [(self.position[0]+move, self.position[1])]
            if self.first_move and not self.board.board[self.position[0]+(move*2)][self.position[1]].is_occupied:
                possible_moves.append((self.position[0]+(move*2), self.position[1]))
        if self.position[1] == 0:
            return possible_moves
        if self.board.board[self.position[0]+move][self.position[1]-1].figure:
            if self.board.board[self.position[0]+move][self.position[1]-1].is_occupied and self.board.board[self.position[0]+move][self.position[1]-1].figure.color != self.color:
                possible_moves.append((self.position[0]+move, self.position[1]-1))
        if self.position[1] == 7:
            return possible_moves
        if self.board.board[self.position[0]+move][self.position[1]+1].figure:
            if self.board.board[self.position[0]+move][self.position[1]+1].is_occupied and self.board.board[self.position[0]+move][self.position[1]+1].figure.color != self.color:
                possible_moves.append((self.position[0]+move, self.position[1]+1))
        return possible_moves

class Knight(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()

class Bishop(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()

class Rook(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move = True

class Queen(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()

class King(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move = True
