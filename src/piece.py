"""File containing implementation for each figure in the game. Code structure allows to easily add new Figures for more game variants.
"""

import customtkinter as ctk
from typing import Callable, Any
from PIL import Image
import platform
import os
if platform.system() == 'Windows':
    import pywinstyles

from tools import resource_path, get_from_config, update_error_log
from properties import COLOR

class Piece:
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Main class used to implement all figures. Contains all essential methods for every figure such as:
         - loading assets
         - virtual function for checking possible moves
         - checking turns
         - updating assets
         - representation of the class for easier debugging

        Args:
            color (str): Color of the figure.
            board : Board object on which figures will be placed.
            position (tuple[int, int]): Position on the board.
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
                return ctk.CTkImage(
                    light_image=loaded_image,
                    dark_image=loaded_image,
                    size=(int(get_from_config('size'))-10, int(get_from_config('size'))-10))
            self.image = ctk.CTkImage(
                light_image=loaded_image,
                dark_image=loaded_image,
                size=(int(get_from_config('size'))-10, int(get_from_config('size'))-10))
        except (FileExistsError, FileNotFoundError) as e:
            update_error_log(e)
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
    """Implementation of the pawn. Supports en passant, promotions, moving and capturing.

    Args:

     - Piece (Piece): Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int], notation_func: Callable) -> None:
        """Constructor:

         - basic setup of master class Piece
         - loads additional flags necessary for correct pawn implementation

        Args:

         - color (str): Color of the pawn.
         - board : Board object on which the pawn will be placed. 
         - position (tuple[int, int]): Position of the pawn on the board.
         - notation_func (Callable): Callable function from notation module used to note the move.
        """
        super().__init__(color, board, position)
        self.color: str = color # b | w
        self.position: tuple[int, int] = position
        self.board = board # Board object (import loop occurs if imported for type annotation)
        self.load_image()
        self.first_move: bool = True
        self.moved_by_two: bool = False
        self.can_en_passant: bool = False
        self.move: int = 1 if self.color == 'b' else -1
        self.notation_func: Callable = notation_func

    def check_possible_moves(self, color: str, checking: bool=False) -> list[tuple[int, int]]:
        """Function checking all possible moves for the Pawn.

        Args:
         - color (str): Color of the pawn.
         - checking (bool, optional): Flag to know when player makes move and when algorithm checks possible moves. Defaults to False.

        Returns:

         - list[tuple[int, int]]: Returns list of all legal positions to which pawn can move.
        """
        possible_moves: list[tuple[int, int]] = []
        if self.check_turn(color):
            return possible_moves
        move = self.move
        x, y = self.position[0], self.position[1]
        forward_one = (x + move, y)
        forward_two = (x + move * 2, y)
        if not self.board.board[forward_one[0]][forward_one[1]].figure:
            possible_moves.append(forward_one)
            if self.first_move and not self.board.board[forward_two[0]][forward_two[1]].figure:
                possible_moves.append(forward_two)
        for offset in [-1, 1]:
            if 0 <= y + offset < 8:
                capture_position = (x + move, y + offset)
                target_square = self.board.board[capture_position[0]][capture_position[1]]
                if target_square.figure and target_square.figure.color != self.color:
                    possible_moves.append(capture_position)
                adjacent_pawn_position = (x, y + offset)
                adjacent_pawn = self.board.board[adjacent_pawn_position[0]][adjacent_pawn_position[1]].figure
                if isinstance(adjacent_pawn, Pawn) and adjacent_pawn.color != self.color and adjacent_pawn.moved_by_two:
                    possible_moves.append((x + move, y + offset))
                    self.can_en_passant = True
        return possible_moves

    def choose_figure(self, event: Any, figure, choose_piece_menu: ctk.CTkLabel, choose_piece_menu_1: ctk.CTkFrame) -> None:
        """Function responsible of promoting the pawn to other figure.

        Args:

         - event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
         - figure : Figure chosen by the player.
         - choose_piece_menu (ctk.CTkLabel): Label widget.
         - choose_piece_menu_1 (ctk.CTkFrame): Frame widget.
        """
        x, y = self.position[0], self.position[1]
        self.board.board[x][y].figure = figure(self.color, self.board, self.position)
        self.board.board[x][y].update()
        self.notation_func(self.board.board[x][y].figure.__class__.__name__)
        choose_piece_menu.destroy()
        choose_piece_menu_1.destroy()

    def create_button(self, choose_piece_menu: ctk.CTkLabel, figure, choose_piece_menu_1: ctk.CTkFrame) -> None:
        """Function creating the button for one of the figure possible to choose from the menu.

        Args:

         - choose_piece_menu (ctk.CTkLabel): Label in which button will be created.
         - figure : Figure that will be possible to choose by clicking the button.
         - choose_piece_menu_1 (ctk.CTkFrame): Frame widget.
        """
        piece_image: ctk.CTkImage | None = self.load_image(str(figure.__name__))
        button_figure: ctk.CTkLabel = ctk.CTkLabel(
            master        = choose_piece_menu,
            text          = '',
            image         = piece_image,
            corner_radius = 0
        )
        button_figure.pack(side=ctk.LEFT, padx=10, pady=10)
        button_figure.bind('<Button-1>', lambda e: self.choose_figure(e, figure, choose_piece_menu, choose_piece_menu_1))

    def promote(self) -> bool:
        """Function checking if pawn is ont the end of the board. If so it force the player to choose the figure they want to promote to.

        Returns:

         - bool: True if pawn was promoted. False otherwise.
        """
        if self.position[0] in {0, 7}:
            choose_piece_menu_1: ctk.CTkFrame = ctk.CTkFrame(
                master   = self.board, corner_radius=0,
                fg_color = COLOR.BACKGROUND
            )
            choose_piece_menu_1.place(relx=0, rely=0, relwidth=1, relheight=1)
            if platform.system() == 'Windows':
                pywinstyles.set_opacity(choose_piece_menu_1, value=0.01, color="#000001")
            choose_piece_menu: ctk.CTkFrame = ctk.CTkFrame(
                master        = self.board,
                fg_color      = COLOR.BACKGROUND,
                corner_radius = 0,
                border_color  = COLOR.DARK_TEXT,
                border_width  = 4
            )
            choose_piece_menu.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
            if platform.system() == 'Windows':
                pywinstyles.set_opacity(choose_piece_menu, color="#000001")
            possible_figures = [Knight, Bishop, Rook, Queen]
            for i, figure in enumerate(possible_figures):
                self.create_button(choose_piece_menu, figure, choose_piece_menu_1)
            return True
        return False

    def notate(self, figure_name: Piece, moves_record, capture: bool, check: bool, checkmate: bool) -> None:
        """Helper function to note the move of the pawn.

        Args:

         - figure_name (Piece): Name of the figure.
         - moves_record : Object of MovesRecord. Cannot specify type due to circular imports.
         - capture (bool): Flag to check if capture occurred.
         - check (bool): Flag to check if after pawn move check occurred.
         - checkmate (bool): Flag to check if after pawn move checkmate occurred.
        """
        moves_record.record_move(figure_name,
            capture=capture, castle=None, check=check, checkmate=checkmate,
            promotion=f'{self.board.board[self.position[0]][self.position[1]].figure.__class__.__name__[0]}'
        )

class Knight(Piece):
    """Implementation of the Knight.

    Args:

     - Piece : Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Constructor is really basic. Setups master class and setups board, color and loads asset. 

        Args:

         - color (str): Color of the Knight.
         - board : Board object on which figures will be placed.
         - position (tuple[int, int]): Position on the board.
        """
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.moves: list[tuple[int, int]] = [   
            (-2,-1), (-2, 1),
            (-1,-2), (-1, 2),
            ( 1,-2), ( 1, 2),
            ( 2,-1), ( 2, 1)   
        ]
        self.special_cases: dict[tuple[int, int], list[int]] = {
            (1, 1): [0, 1, 2, 4],
            (1, 6): [0, 1, 3, 5],
            (6, 6): [3, 5, 6, 7],
            (6, 1): [2, 4, 3, 5],
            (0, 0): [0, 1, 2, 3, 4, 6],
            (0, 1): [0, 1, 2, 3, 4],
            (1, 0): [0, 1, 2, 4, 7]
        }

    def check_moves(self, exceptions: list[int]) -> list[tuple[int, int]]:
        """Function checking possible moves for the Knight.

        Args:

         - exceptions (list[int]): List of position that are not legal.

        Returns:

         - list[tuple[int, int]]: List of all legal moves.
        """
        possible_moves: list[tuple[int, int]] = []
        for i, move in enumerate(self.moves):
            if i in exceptions:
                continue
            new_position = (self.position[0] + move[0], self.position[1] + move[1])
            if 0 <= new_position[0] <= 7 and 0 <= new_position[1] <= 7:
                target_square = self.board.board[new_position[0]][new_position[1]]
                if not target_square.figure or target_square.figure.color != self.color:
                    possible_moves.append(new_position)
        return possible_moves

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        """Function checking all possible moves for the Knight.

        Args:

         - color (str): Color of the Knight.
         - checking (bool, optional): Flag to recognize between human making a move and algorithm checking if after move check doesn't occurs. Defaults to False.

        Returns:

         - list[tuple[int, int]]: List of all legal position to which Knight can move.
        """
        if self.check_turn(color) and not checking:
            return []
        if 2 <= self.position[0] <= 5 and self.position[1] in {1, 6} and self.position not in self.special_cases:
            if self.position[1] == 1:
                return self.check_moves([2, 4])
            if self.position[1] == 6:
                return self.check_moves([3, 5])
        if 2 <= self.position[1] <= 5 and self.position[0] in {1, 6} and self.position not in self.special_cases:
            if self.position[0] == 1:
                return self.check_moves([0, 1])
            if self.position[0] == 6:
                return self.check_moves([6, 7])
        if self.position in self.special_cases:
            return self.check_moves(self.special_cases[self.position])
        return self.check_moves([])

class Bishop(Piece):
    """Implementation of the Bishop.

    Args:

     - Piece : Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Constructor is really basic. Setups master class and setups board, color and loads asset. 

        Args:

         - color (str): Color of the Bishop.
         - board : Board object on which figures will be placed.
         - position (tuple[int, int]): Position on the board.
        """
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.moves_vec = [
            (-1, -1), (-1, 1),
            ( 1, -1), (1,  1)
        ]

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        """Function checking all possible moves of the Bishop.

        Args:

         - color (str): Color of the Bishop.
         - checking (bool, optional): Flag to recognize between human making a move and algorithm checking if after move check doesn't occurs. Defaults to False.

        Returns:

         - list[tuple[int, int]]: List of all legal position to which Bishop can move.
        """
        possible_moves: list[tuple[int, int]] = []
        if self.check_turn(color) and not checking:
            return possible_moves
        for move in self.moves_vec:
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
    """Implementation of the Rook.

    Args:
     - Piece : Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Constructor is really basic. Setups master class and setups board, color and loads asset. 

        Args:

         - color (str): Color of the Rook.
         - board : Board object on which figures will be placed.
         - position (tuple[int, int]): Position on the board.
        """
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move: bool = True
        self.moves_vec = [
            (-1, 0), (0,-1),
            ( 1, 0), (0, 1)
        ]

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        """Function checking all possible moves of the Rook.

        Args:

         - color (str): Color of the Rook.
         - checking (bool, optional): Flag to recognize between human making a move and algorithm checking if after move check doesn't occurs. Defaults to False.

        Returns:

         - list[tuple[int, int]]: List of all legal position to which Rook can move.
        """
        possible_moves: list[tuple[int, int]] = []
        if self.check_turn(color) and not checking:
            return possible_moves
        for move in self.moves_vec:
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
    """Implementation of the Queen.

    Args:

     - Piece : Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Constructor is really basic. Setups master class and setups board, color and loads asset. 

        Args:

         - color (str): Color of the Queen.
         - board : Board object on which figures will be placed.
         - position (tuple[int, int]): Position on the board.
        """
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.moves_vec = [
            (-1, 0), (0,-1),
            ( 1, 0), (0, 1),
            (-1, -1), (-1, 1),
            ( 1, -1), (1,  1)
        ]

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        """Function checking all possible moves of the Queen.

        Args:

         - color (str): Color of the Queen.
         - checking (bool, optional): Flag to recognize between human making a move and algorithm checking if after move check doesn't occurs. Defaults to False.

        Returns:

         - list[tuple[int, int]]: List of all legal position to which Queen can move.
        """
        possible_moves: list[tuple[int, int]] = []
        if self.check_turn(color) and not checking:
            return possible_moves
        for move in self.moves_vec:
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
    """Implementation of the King.

    Args:

     - Piece : Inheritance from the master class Piece to access general functions of the figures.
    """
    def __init__(self, color: str, board, position: tuple[int, int]) -> None:
        """Constructor is really basic. Setups master class and setups board, color and loads asset. 

        Args:

         - color (str): Color of the King.
         - board : Board object on which figures will be placed.
         - position (tuple[int, int]): Position on the board.
        """
        super().__init__(color, board, position)
        self.color: str = color
        self.board = board
        self.load_image()
        self.first_move: bool = True
        self.can_castle: bool = False

    def check_possible_moves(self, color: str, checking: bool = False) -> list[tuple[int, int]]:
        """Function checking all possible moves of the King.

        Args:

         - color (str): Color of the King.
         - checking (bool, optional): Flag to recognize between human making a move and algorithm checking if after move check doesn't occurs. Defaults to False.

        Returns:

         - list[tuple[int, int]]: List of all legal position to which King can move.
        """
        possible_moves: list[tuple[int, int]] = []
        if self.check_turn(color) and not checking:
            return possible_moves
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
        """Function checking moves for castle.

        Returns:
            list[tuple[int, int]]: List of legal positions.
        """
        castling_moves = []
        row = self.position[0]
        if self.can_castle_kingside():
            castling_moves.append((row, 6))
        if self.can_castle_queenside():
            castling_moves.append((row, 2))
        return castling_moves

    def can_castle_kingside(self) -> bool:
        """Function checking if King can perform castle from King side.

        Returns:

         - bool: True if King can castle. False otherwise.
        """
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
        """Function checking if King can perform castle from Queen side.

        Returns:

         - bool: True if King can castle. False otherwise.
        """
        row, col = self.position
        if isinstance(self.board.board[row][0].figure, Rook) and self.board.board[row][0].figure.first_move:
            for i in range(col - 1, 0, -1):
                if self.board.board[row][i].figure or self.board.is_under_attack((row, i), self.color):
                    return False
            if self.board.is_under_attack((row, 2), self.color) or self.board.is_under_attack((row, col), self.color):
                return False
            return True
        return False
