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
        self.first_move = False
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
        possible_moves: list[tuple[int, int]] = []
        if self.position[0] in {0, 7}:
            return possible_moves
        forward_one = (self.position[0] + move, self.position[1])
        forward_two = (self.position[0] + move * 2, self.position[1])
        if not self.board.board[forward_one[0]][forward_one[1]].figure:
            possible_moves.append(forward_one)
            if self.first_move and not self.board.board[forward_two[0]][forward_two[1]].figure:
                possible_moves.append(forward_two)
        for offset in [-1, 1]:
            if 0 <= self.position[1] + offset < 8:
                capture_position = (self.position[0] + move, self.position[1] + offset)
                target_square = self.board.board[capture_position[0]][capture_position[1]]
                if target_square.figure and target_square.figure.color != self.color:
                    possible_moves.append(capture_position)
        return possible_moves

    def upgrade(self):
        pass

class Knight(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()

    def check_moves(self, exceptions: list[int]) -> list[tuple[int, int]]:
        possible_moves: list[tuple[int, int]] = []
        moves = [   (-2,-1), (-2, 1),
                    (-1,-2), (-1, 2),
                    ( 1,-2), ( 1, 2),
                    ( 2,-1), ( 2, 1)   ] 
        for i, move in enumerate(moves):
            if i in exceptions:
                print(i, move)
                continue
            new_position = (self.position[0] + move[0], self.position[1] + move[1])
            if 0 <= new_position[0] <= 7 and 0 <= new_position[1] <= 7:
                target_square = self.board.board[new_position[0]][new_position[1]]
                if not target_square.figure or target_square.figure.color != self.color:
                    possible_moves.append(new_position)
        return possible_moves

    def check_possible_moves(self) -> list[tuple[int, int]]:
        special_cases = {
            (1, 1): [0, 1, 2, 4],
            (1, 6): [0, 1, 3, 5],
            (6, 6): [3, 5, 6, 7],
            (6, 1): [2, 4, 3, 5],
            (0, 0): [0, 1, 2, 3, 4, 6],
            (0, 1): [0, 1, 2, 3, 4],
            (1, 0): [0, 1, 2, 4, 7]
        }
        if 2 <= self.position[0] <= 5 and self.position[1] in {1, 6} and self.position not in special_cases:
            if self.position[1] == 1:
                return self.check_moves([2, 4])
            if self.position[1] == 6:
                return self.check_moves([3, 5])
        if 2 <= self.position[1] <= 5 and self.position[0] in {1, 6} and self.position not in special_cases:
            if self.position[0] == 1:
                return self.check_moves([0, 1])
            if self.position[0] == 6:
                return self.check_moves([6, 7])
        if self.position in special_cases:
            return self.check_moves(special_cases[self.position])
        return self.check_moves([])

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
