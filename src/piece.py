"""File containing implementation for each figure in the game. Code structure allows to easily add new Figures for more game variants.
"""

import customtkinter as ctk
from typing import Callable
from PIL import Image
import platform
import os
if platform.system() == 'Windows':
    import pywinstyles

from tools import resource_path, get_from_config
from properties import COLOR

class Piece:
    def __init__(self, color: str, board, position) -> None:
        """Main class used to implement all figures. Contains all essential methods for every figure such as:
         - loading assets
         - virtual function for checking possible moves
         - checking turns
         - updating assets
         - representation of the class for easier debugging

        Args:
            color (str): _description_
            board (_type_): _description_
            position (_type_): _description_
        """
        self.color: str = color
        self.board = board
        self.position: tuple[int, int] = position
        self.first_move: bool = False
        self.image: ctk.CTkImage | None = None

    def check_possible_moves(self, color: str, checking: bool=False):
        """Virtual function.

        Args:

         - color (str): Color of the figure to move.
         - checking (bool, optional): Flag indicating search. Defaults to False.

        Raises:

         - NotImplementedError: All Figures have to have this function implemented.
        """
        raise NotImplementedError

    def check_turn(self, current_color: str) -> bool:
        """Checks which player has its right to move.

        Args:

         - current_color (str): Color of the clicked figure.

        Returns:

         - bool: True if its given color turn, False otherwise.
        """
        return False if current_color == self.color else True

    def load_image(self, piece: str | None=None) -> None | ctk.CTkImage:
        """Loads asset for the piece.

        Args:

         - piece (str | None, optional): Piece string representation. Defaults to None.

        Returns:

         - None | ctk.CTkImage: If piece representation passed function will try to load asset. None otherwise.

        Raises:

         - FileExistsError: If file doesn't exist game will crash and give feedback in the console.
         - FileNotFoundError: If file couldn't be found game will crash and give feedback in the console.
        """
        if not piece:
            piece_name = (self.__class__.__name__).lower()
        else:
            piece_name = piece
        path: str = resource_path(os.path.join('assets', f'{get_from_config('theme')}', f'{piece_name}_{self.color}.png'))
        try: 
            loaded_image = Image.open(path).convert('RGBA')
            if piece:
                return ctk.CTkImage(light_image=loaded_image, dark_image=loaded_image, size=(int(get_from_config('size'))-10, int(get_from_config('size'))-10))
            self.image = ctk.CTkImage(light_image=loaded_image, dark_image=loaded_image, size=(int(get_from_config('size'))-10, int(get_from_config('size'))-10))
        except (FileExistsError, FileNotFoundError) as e:
            print(f'Couldn`t load image for due to error: {e}')
        return None

    def update_image(self) -> None:
        """Function updating cell asset.
        """
        self.load_image()
        self.board.board[self.position[0]][self.position[1]].configure(image=self.image)

    def __str__(self) -> str:
        """Overriding string representation of the class used in print() for example.

        Returns:

         - str: Representation of the class Piece: {piece name} Color:{piece color}
        """
        return f'Piece: {self.__class__.__name__} Color: {'white' if self.color == 'w' else 'black'}'

class Pawn(Piece):
    def __init__(self, color: str, board, position: tuple[int, int], notation_func) -> None:
        super().__init__(color, board, position)
        self.color: str = color # b | w
        self.position: tuple[int, int] = position
        self.board = board
        self.load_image()
        self.first_move: bool = True
        self.moved_by_two: bool = False
        self.can_en_passant: bool = False
        self.move: int = 1 if self.color == 'b' else -1
        self.notation_func: Callable = notation_func

    def check_possible_moves(self, color: str, checking: bool=False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
        move = self.move
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
                adjacent_pawn_position = (self.position[0], self.position[1] + offset)
                adjacent_pawn = self.board.board[adjacent_pawn_position[0]][adjacent_pawn_position[1]].figure
                if isinstance(adjacent_pawn, Pawn) and adjacent_pawn.color != self.color and adjacent_pawn.moved_by_two:
                    possible_moves.append((self.position[0] + move, self.position[1] + offset))
                    self.can_en_passant = True
        return possible_moves

    def choose_figure(self, event, figure, choose_piece_menu, choose_piece_menu_1) -> None:
        self.board.board[self.position[0]][self.position[1]].figure = figure(self.color, self.board, self.position)
        self.board.board[self.position[0]][self.position[1]].update()
        self.notation_func(self.board.board[self.position[0]][self.position[1]].figure.__class__.__name__)
        choose_piece_menu.destroy()
        choose_piece_menu_1.destroy()

    def create_button(self, choose_piece_menu, figure, choose_piece_menu_1) -> None:
        piece_image = self.load_image(str(figure.__name__))
        button_figure = ctk.CTkLabel(choose_piece_menu, text='', image=piece_image,
                                    corner_radius=0)
        button_figure.pack(side=ctk.LEFT, padx=10, pady=10)
        button_figure.bind('<Button-1>', lambda e: self.choose_figure(e, figure, choose_piece_menu, choose_piece_menu_1))

    def promote(self) -> bool:
        if self.position[0] in {0, 7}:
            choose_piece_menu_1 = ctk.CTkFrame(self.board, corner_radius=0,
                                            fg_color=COLOR.BACKGROUND)
            choose_piece_menu_1.place(relx=0, rely=0, relwidth=1, relheight=1)
            if platform.system() == 'Windows':
                pywinstyles.set_opacity(choose_piece_menu_1, value=0.01, color="#000001")
            choose_piece_menu = ctk.CTkFrame(self.board, fg_color=COLOR.BACKGROUND,
                                            corner_radius=0, border_color=COLOR.DARK_TEXT,
                                            border_width=4)
            choose_piece_menu.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
            if platform.system() == 'Windows':
                pywinstyles.set_opacity(choose_piece_menu, color="#000001")
            possible_figures = [Knight, Bishop, Rook, Queen]
            for i, figure in enumerate(possible_figures):
                self.create_button(choose_piece_menu, figure, choose_piece_menu_1)
            return True
        return False

    def notate(self, figure_name, moves_record, capture, check, checkmate) -> None:
        moves_record.record_move(figure_name, capture=capture, castle=None, check = check, checkmate = checkmate, promotion=f'{self.board.board[self.position[0]][self.position[1]].figure.__class__.__name__[0]}')

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
                continue
            new_position = (self.position[0] + move[0], self.position[1] + move[1])
            if 0 <= new_position[0] <= 7 and 0 <= new_position[1] <= 7:
                target_square = self.board.board[new_position[0]][new_position[1]]
                if not target_square.figure or target_square.figure.color != self.color:
                    possible_moves.append(new_position)
        return possible_moves

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
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

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
        possible_moves: list[tuple[int, int]] = []
        moves_vec = [
            (-1, -1), (-1, 1),
            ( 1, -1), (1,  1)
        ]
        for move in moves_vec:
            for i in range(1, 8):
                multiplied_vec = tuple(x * i for x in move)
                x = self.position[0] + multiplied_vec[0]
                y = self.position[1] + multiplied_vec[1]
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if not self.board.board[x][y].figure:
                        possible_moves.append((x, y))
                    elif self.board.board[x][y].figure.color != self.color:
                        possible_moves.append((x, y))
                        break
                    else:
                        break
                else:
                    break
        return possible_moves

class Rook(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move: bool = True

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
        possible_moves: list[tuple[int, int]] = []
        moves_vec = [
            (-1, 0), (0,-1),
            ( 1, 0), (0, 1)
        ]
        for move in moves_vec:
            for i in range(1, 8):
                multiplied_vec = tuple(x * i for x in move)
                x = self.position[0] + multiplied_vec[0]
                y = self.position[1] + multiplied_vec[1]
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if not self.board.board[x][y].figure:
                        possible_moves.append((x, y))
                    elif self.board.board[x][y].figure.color != self.color:
                        possible_moves.append((x, y))
                        break
                    else:
                        break
                else:
                    break
        return possible_moves

class Queen(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
        possible_moves: list[tuple[int, int]] = []
        moves_vec = [
            (-1, 0), (0,-1),
            ( 1, 0), (0, 1),
            (-1, -1), (-1, 1),
            ( 1, -1), (1,  1)
        ]
        for move in moves_vec:
            for i in range(1, 8):
                multiplied_vec = tuple(x * i for x in move)
                x = self.position[0] + multiplied_vec[0]
                y = self.position[1] + multiplied_vec[1]
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if not self.board.board[x][y].figure:
                        possible_moves.append((x, y))
                    elif self.board.board[x][y].figure.color != self.color:
                        possible_moves.append((x, y))
                        break
                    else:
                        break
                else:
                    break
        return possible_moves

class King(Piece):
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move: bool = True
        self.can_castle: bool = False

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        if self.check_turn(color) and not checking:
            return []
        possible_moves: list[tuple[int, int]] = []
        for i in range(max(0, self.position[0] - 1), min(8, self.position[0] + 2)):
            for j in range(max(0, self.position[1] - 1), min(8, self.position[1] + 2)):
                if not self.board.board[i][j].figure:
                    possible_moves.append((i, j))
                if self.board.board[i][j].figure and self.board.board[i][j].figure.color != self.color:
                    possible_moves.append((i, j))
        if self.first_move and not checking:
            possible_moves.extend(self.get_castling_moves())
        return possible_moves

    def get_castling_moves(self) -> list[tuple[int, int]]:
        castling_moves = []
        row = self.position[0]
        if self.can_castle_kingside():
            castling_moves.append((row, 6))
        if self.can_castle_queenside():
            castling_moves.append((row, 2))
        return castling_moves

    def can_castle_kingside(self) -> bool:
        row, col = self.position
        if isinstance(self.board.board[row][7].figure, Rook) and self.board.board[row][7].figure.first_move:
            for i in range(col + 1, 7):
                if self.board.board[row][i].figure or self.board.is_under_attack((row, i), self.color):
                    return False
            if self.board.is_under_attack((row, 6), self.color) or self.board.is_under_attack((row, col), self.color):
                return False
            return True
        return False

    def can_castle_queenside(self) -> bool:
        row, col = self.position
        if isinstance(self.board.board[row][0].figure, Rook) and self.board.board[row][0].figure.first_move:
            for i in range(col - 1, 0, -1):
                if self.board.board[row][i].figure or self.board.is_under_attack((row, i), self.color):
                    return False
            if self.board.is_under_attack((row, 2), self.color) or self.board.is_under_attack((row, col), self.color):
                return False
            return True
        return False
