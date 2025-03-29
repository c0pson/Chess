"""File containing implementation for Board and Cells on the board. Code structure allows custom sizes of the board but is limited to square boards.
"""

import customtkinter as ctk
from typing import Any
import platform
if platform.system() == 'Windows':
    import pywinstyles
from PIL import Image
import os
import threading
import soundfile

from notifications import Notification
from properties import COLOR
from menus import MovesRecord
from tools import get_from_config, resource_path, play_sound, update_error_log
import piece

class Cell(ctk.CTkLabel):
    """Class handling actions in specific cells.

    Args:
        ctk.CTkLabel : Inheritance from customtkinter CTkLabel widget.
    """
    def __init__(self, frame: ctk.CTkFrame, figure: piece.Piece | None, position: tuple[int, int], color: str, board) -> None:
        """Constructor:
             - binds left button to on_click function.
             - displays itself on the screen.

        Args:
            frame (ctk.CTkFrame): Parent Frame on which cell will be represented.
            figure (piece.Piece | None): Figure on a cell.
            position (tuple[int, int]): Position on a board.
            color (str): Color of the cell white or black.
            board (Board): Parent class handling cell placement.
        """
        self.frame: ctk.CTkFrame = frame
        self.position: tuple[int, int] = position
        self.board: Board = board
        self.figure: None | piece.Piece = figure
        self.frame_around: ctk.CTkLabel | None = None
        figure_asset: ctk.CTkImage | None = self.figure.image if self.figure else None
        super().__init__(
            master   = frame,
            image    = figure_asset,
            text     = '',
            fg_color = color,
            width    = get_from_config('size'),
            height   = get_from_config('size'),
            bg_color = COLOR.BACKGROUND
        )
        self.bind('<Button-1>', self.on_click)
        self.pack(side=ctk.LEFT, padx=2, pady=2)

    def on_click(self, event: Any) -> None:
        """Handles clicks by calling board functions handling game logic.

        Args:
            event (Any): Event type. Doesn't matter but is required parameter by customtkinter.
        """
        if self.board.clicked_figure and self.board.clicked_figure.color:
            if self.board.board[self.position[0]][self.position[1]] not in self.board.highlighted and self.board.clicked_figure != self.figure:
                if self.figure:
                    if self.figure.color != self.board.clicked_figure.color:
                        threading.Thread(target=play_sound, args=(self.board.illegal_sound,)).start()
                else:
                    threading.Thread(target=play_sound, args=(self.board.illegal_sound,)).start()
            self.board.handle_move(self.position)
        if self.figure and not self.board.clicked_figure and self.board.current_turn == self.figure.color:
            self.board.handle_clicks(self.figure, self.position)
        else:
            self.board.handle_move(self.position)

    def update(self) -> None:
        """Updates the asset shown on a cell.
        """
        figure_asset = self.figure.image if self.figure else b''
        self.configure(image=figure_asset, require_redraw=True)

class Board(ctk.CTkFrame):
    """Class handling all cells and move related logic.

    Args:
        ctk.CTkFrame : Inheritance from customtkinter CTkLabel widget.
    """
    def __init__(self, master, moves_record: MovesRecord, size: int) -> None:
        """Constructor:
             - Setups all important variables
             - calls loading_animation(0)

        Args:
            master (Any): Parent widget.
            moves_record (MovesRecord): class handling move records.
            size (int): Size n of the n x n board.
        """
        super().__init__(master, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        self.master: Any = master
        self.loading_screen: ctk.CTkLabel | None = None
        self.font_name: str = str(get_from_config('font_name'))
        self.loading_animation(0)
        self.move_sound = soundfile.read(resource_path(os.path.join('sounds', 'move-self.wav')), dtype='float32')[0]
        self.capture_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.move_check_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.castle_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.end_game_sound = soundfile.read(resource_path(os.path.join('sounds', 'game-end.wav')), dtype='float32')[0]
        self.illegal_sound = soundfile.read(resource_path(os.path.join('sounds', 'illegal.wav')), dtype='float32')[0]
        self.frame_image: ctk.CTkImage = ctk.CTkImage(Image.open(resource_path(os.path.join('assets', 'menu', 'frame.png'))).convert('RGBA'), size=(80,80))
        self.size: int = size
        self.board: list[list[Cell]] = self.create_board()
        self.highlighted: list[Cell] = []
        self.clicked_figure: piece.Piece | None = None
        self.previous_coords: tuple[int, int] | None = None
        self.current_turn: str = 'w'
        self.notification: None | Notification = None
        self.moves_record: MovesRecord = moves_record
        self.capture: bool = False
        self.game_over: bool = False

    @staticmethod
    def determine_tile_color(pos: tuple[int, int]) -> str:
        """Static method to determine color of the piece.

        Args:
            pos (tuple[int, int]): Position of the cell on the board.

        Returns:
            str: Color of the cell.
        """
        if (pos[0]%2 and pos[1]%2) or (not pos[0]%2 and not pos[1]%2):
            return COLOR.TILE_1
        else:
            return COLOR.TILE_2

    def create_outline_l_r_t(self) -> None:
        """Creates outline of the board.
        """
        ctk.CTkLabel(
            master = self,
            text=f' ',
            font=ctk.CTkFont(self.font_name, self.size//3),
            text_color=COLOR.DARK_TEXT
        ).pack(padx=10, pady=1)
        new_frame = ctk.CTkFrame(
            master        = self,
            fg_color      = COLOR.DARK_TEXT,
            corner_radius = 0
        )
        new_frame.pack(side=ctk.LEFT, padx=0, pady=0, fill=ctk.Y)
        for i in range(8):
            ctk.CTkLabel(
                master   = new_frame,
                text     = f' {i+1}',
                font     = ctk.CTkFont(self.font_name, self.size//3),
                fg_color = COLOR.DARK_TEXT,
                anchor   = ctk.E
            ).pack(side=ctk.TOP, padx=10, pady=0, expand=True)
        ctk.CTkLabel(
            master = new_frame,
            text   = '\n',
            font   = ctk.CTkFont(self.font_name, 22)
        ).pack(side=ctk.BOTTOM, padx=0, pady=0)
        new_frame = ctk.CTkFrame(
            master   = self,
            fg_color = COLOR.DARK_TEXT,
            corner_radius=0
        )
        new_frame.pack(side=ctk.RIGHT, padx=0, pady=0, fill=ctk.Y)
        ctk.CTkLabel(
            master     = new_frame, 
            text       = '  ',
            font       = ctk.CTkFont(self.font_name, self.size//3), 
            text_color = COLOR.DARK_TEXT, 
            fg_color   = COLOR.DARK_TEXT
        ).pack(padx=10, pady=1)

    def create_board(self) -> list[list[Cell]]:
        """Creates a board filled with colored cells. Uses prepared dictionary of the correct figures placement to place the Figures.

        Returns:
            list[list[Cell]]: 2D representation of the board.
        """
        self.create_outline_l_r_t()
        board: list[list[Cell]] = []
        board_frame = ctk.CTkFrame(
            master        = self,
            corner_radius = 0,
            fg_color      = COLOR.DARK_TEXT
        )
        board_frame.pack(side=ctk.TOP, padx=0, pady=0)
        piece_positions = {
            (0, 0): piece.Rook('b', self, (0, 0)),   # Black rook
            (0, 7): piece.Rook('b', self, (0, 7)),   # Black rook
            (7, 0): piece.Rook('w', self, (7, 0)),   # White rook
            (7, 7): piece.Rook('w', self, (7, 7)),   # White rook
            (0, 1): piece.Knight('b', self, (0, 1)), # Black knight 
            (0, 6): piece.Knight('b', self, (0, 6)), # Black knight 
            (7, 1): piece.Knight('w', self, (7, 1)), # White knight
            (7, 6): piece.Knight('w', self, (7, 6)), # White knight
            (0, 2): piece.Bishop('b', self, (0, 2)), # Black bishop
            (0, 5): piece.Bishop('b', self, (0, 5)), # Black bishop
            (7, 2): piece.Bishop('w', self, (7, 2)), # White bishop
            (7, 5): piece.Bishop('w', self, (7, 5)), # White bishop
            (0, 3): piece.Queen('b', self, (0, 3)),  # Black Queen
            (7, 3): piece.Queen('w', self, (7, 3)),  # White Queen
            (0, 4): piece.King('b', self, (0, 4)),   # Black King
            (7, 4): piece.King('w', self, (7, 4))    # White King
        }
        for i in range(8):
            row = []
            new_frame: ctk.CTkFrame = ctk.CTkFrame(
                master   = board_frame,
                fg_color = COLOR.DARK_TEXT
            )
            new_frame.pack(padx=0, pady=0)
            for j in range(8):
                if self.loading_screen:
                    self.loading_screen.lift()
                color: str = self.determine_tile_color((i, j))
                figure: piece.Piece | None = piece_positions.get((i, j)) if (i, j) in piece_positions else (piece.Pawn('b' if i == 1 else 'w', self, (i, j), self.notation_promotion) if i in [1, 6] else None)
                cell = Cell(new_frame, figure, (i, j), color, self)
                row.append(cell)
            board.append(row)
        new_frame = ctk.CTkFrame(
            master        = self,
            fg_color      = COLOR.DARK_TEXT,
            corner_radius = 0
        )
        new_frame.pack(padx=2, pady=2, fill=ctk.X)
        for letter in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'):
            ctk.CTkLabel(
                master   = new_frame,
                text     = letter,
                font     = ctk.CTkFont(self.font_name, self.size//3),
                fg_color = COLOR.DARK_TEXT
            ).pack(side=ctk.LEFT, padx=0, pady=0, expand=True)
        return board

    def remove_highlights(self) -> None:
        """Removes highlights from the cell.
        """
        for cell in self.highlighted:
            color = self.determine_tile_color(cell.position)
            cell.configure(fg_color=color)
        self.highlighted = []

    def display_message(self, message: str, duration_sec: int) -> None:
        """Displays message on the screen using Notification class.

        Args:
            message (str): Desired message to display. <br>
            duration_sec (int): Amount of seconds before hiding the notification .
        """
        if self.notification:
            self.notification.destroy()
        self.notification = Notification(self, message=message, duration_sec=duration_sec)

    def is_game_over(self) -> tuple[bool, bool]:
        """Checks if checkmate occurred.

        Returns:
            tuple[bool, bool]: 1st tuple element is game_over and 2nd is in check both True or False.
        """
        in_check = False
        has_legal_moves = False
        for row in self.board:
            for cell in row:
                if cell.figure and cell.figure.color == self.current_turn:
                    possible_moves = cell.figure.check_possible_moves(self.current_turn)
                    for move in possible_moves:
                        if not self.check_check(cell.figure.position, move):
                            has_legal_moves = True
                            break
                    if has_legal_moves:
                        break
            if has_legal_moves:
                break
        if not has_legal_moves:
            king_position = self.get_king_position(self.current_turn)
            in_check = self.is_under_attack(king_position, self.current_turn)
        return (not has_legal_moves, in_check)

    def handle_clicks(self, figure: piece.Piece, position: tuple[int, int]) -> None:
        """Handles actions after clicking on a specific cell.

        Args:
            figure (piece.Piece): Chosen figure.
            position (tuple[int, int]): Position of that figure.
        """
        if self.previous_coords:
            if platform.system() == 'Windows':
                if x := self.board[self.previous_coords[0]][self.previous_coords[1]].frame_around:
                    x.destroy()
            self.board[self.previous_coords[0]][self.previous_coords[1]].configure(fg_color=self.determine_tile_color(self.previous_coords))
        if not self.game_over:
            if platform.system() == 'Windows':
                image_test = ctk.CTkLabel(
                        fg_color = '#97A789',
                        master   = self.board[position[0]][position[1]],
                        text     = '',
                        image    = self.frame_image
                )
                pywinstyles.set_opacity(image_test, value=1, color='#97A789')
                image_test.place(relx=0.5, rely=0.5, anchor='center')
                self.board[position[0]][position[1]].frame_around = image_test
            else:
                self.board[position[0]][position[1]].configure(fg_color=COLOR.TEXT)
        possible_moves = figure.check_possible_moves(self.current_turn)
        if not possible_moves and self.board[position[0]][position[1]].figure:
            self.previous_coords = position
            return
        self.clicked_figure = figure if figure else None
        self.previous_coords = position
        if self.board and possible_moves:
            valid_moves = []
            for coords in possible_moves:
                check = self.check_check(position, coords)
                if not check:
                    valid_moves.append(coords)
            for coords in valid_moves:
                color = self.board[coords[0]][coords[1]].cget('fg_color')
                new_color = COLOR.HIGH_TILE_1 if color == COLOR.TILE_1 else COLOR.HIGH_TILE_2
                self.board[coords[0]][coords[1]].configure(fg_color=new_color)
                self.highlighted.append(self.board[coords[0]][coords[1]])

    def check_check(self, move_from: tuple[int, int], move_to: tuple[int, int]) -> bool:
        """Checks if King is in a check.

        Args:
            move_from (tuple[int, int]): Starting position.
            move_to (tuple[int, int]): Desired position.

        Returns:
            bool: _description_
        """
        original_from_figure: piece.Piece | None = self.board[move_from[0]][move_from[1]].figure
        original_to_figure: piece.Piece | None = self.board[move_to[0]][move_to[1]].figure
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

    def is_under_attack(self, position: tuple[int, int], color: str) -> bool:
        """Checks if path to castle isn't under the attack.

        Args:
            position (tuple[int, int]): Position of the king.
            color (str): Color of the king.

        Returns:
            bool: Returns True if is under attack, False otherwise.
        """
        for row in self.board:
            for cell in row:
                if cell.figure and cell.figure.color != color:
                    if position in cell.figure.check_possible_moves(cell.figure.color, checking=True):
                        return True
        return False

    def handle_move(self, position: tuple[int, int]) -> None:
        """Function handles moving pieces on the board.

        Args:
            position (tuple[int, int]): Position of the figure.
        """
        if self.previous_coords:
            if platform.system() == 'Windows':
                if x := self.board[self.previous_coords[0]][self.previous_coords[1]].frame_around:
                    x.destroy()
            else:
                self.board[self.previous_coords[0]][self.previous_coords[1]].configure(fg_color=self.determine_tile_color(self.previous_coords))
        if self.clicked_figure and self.previous_coords:
            row, col = position
            cell = self.board[row][col]
            capture = bool(cell.figure)
            self.capture = bool(cell.figure)
            promotion = False
            if cell in self.highlighted and self.previous_coords != position:
                castle = False
                if not self.check_check(self.previous_coords, position):
                    if isinstance(self.clicked_figure, piece.Pawn) and self.clicked_figure.can_en_passant and col != self.previous_coords[1] and not cell.figure:
                        self.board[row - self.clicked_figure.move][col].figure = None
                        self.board[row - self.clicked_figure.move][col].update()
                        capture = True
                        self.capture = True
                    if isinstance(self.clicked_figure, piece.King):
                        if abs(col - self.previous_coords[1]) == 2:
                            if col == 6:
                                self.board[row][5].figure = self.board[row][7].figure
                                self.board[row][7].figure = None
                                self.board[row][5].figure.position = (row, 5) # type: ignore # isinstance already checks it but mypy don't understand it
                                self.board[row][5].update()
                                self.board[row][7].update()
                                self.moves_record.record_move(self.clicked_figure, castle="kingside")
                                castle = True
                            elif col == 2:
                                self.board[row][3].figure = self.board[row][0].figure
                                self.board[row][0].figure = None
                                self.board[row][3].figure.position = (row, 3) # type: ignore # isinstance already checks it but mypy don't understand it
                                self.board[row][3].update()
                                self.board[row][0].update()
                                self.moves_record.record_move(self.clicked_figure, castle="queenside")
                                castle =True
                    cell.figure = self.clicked_figure
                    cell.figure.position = position
                    cell.update()
                    self.board[self.previous_coords[0]][self.previous_coords[1]].figure = None
                    self.board[self.previous_coords[0]][self.previous_coords[1]].update()
                    if isinstance(cell.figure, piece.Pawn):
                        if cell.figure.first_move and abs(self.previous_coords[0] - row) == 2:
                            cell.figure.moved_by_two = True
                            self.reset_en_passant_flags(cell.figure.color)
                        else:
                            cell.figure.moved_by_two = False
                        if cell.figure.promote():
                            promotion = True
                    if cell.figure.first_move:
                        cell.figure.first_move = False
                    self.current_turn = 'b' if self.current_turn == 'w' else 'w'
                    check = self.is_under_attack(self.get_king_position(self.current_turn), self.current_turn)
                    game_over, in_check = self.is_game_over()
                    if game_over:
                        self.game_over = True
                        if in_check:
                            self.display_message(f'Checkmate  {"White wins!" if self.current_turn == "b" else "Black wins!"}', 9)
                            if not promotion:
                                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check)
                        else:
                            self.display_message('Stalemate', 9)
                            if not promotion:
                                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check)
                    elif not castle and not promotion:
                        self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check)
                if game_over:
                    threading.Thread(target=play_sound, args=(self.end_game_sound,)).start()
                elif capture:
                    threading.Thread(target=play_sound, args=(self.capture_sound,)).start()
                elif castle:
                    threading.Thread(target=play_sound, args=(self.castle_sound,)).start()
                elif check:
                    threading.Thread(target=play_sound, args=(self.move_check_sound,)).start()
                else:
                    threading.Thread(target=play_sound, args=(self.move_sound,)).start()
            if not promotion:
                self.clicked_figure = None
                self.previous_coords = None
        self.remove_highlights()

    def notation_promotion(self, promotion:str) -> None:
        """Helper function to note the promotion of the pawn.

        Args:
            promotion (str): Figure representation to which pawn was promoted.
        """
        capture = self.capture
        check = self.is_under_attack(self.get_king_position(self.current_turn), self.current_turn)
        game_over, in_check = self.is_game_over()
        if game_over:
            if in_check:
                self.display_message(f'Checkmate  {"White wins!" if self.current_turn == "b" else "Black wins!"}', 9)
                if self.clicked_figure:
                    self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
            else:
                self.display_message('Stalemate', 9)
                if self.clicked_figure:
                    self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        else:
            if self.clicked_figure:
                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        self.clicked_figure = None
        self.previous_coords = None

    def get_king_position(self, color: str) -> tuple[int, int]:
        """Function returning king position on the board.

        Args:
            color (str): Color of the king.

        Returns:
            tuple[int, int]: Position of the king.
        """
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.King) and cell.figure.color == color:
                    return cell.figure.position
        return (-1, -1)

    def reset_en_passant_flags(self, current_color: str) -> None:
        """Helper function to reset en passant flag.

        Args:
            current_color (str): Color of the current player.
        """
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.Pawn) and cell.figure.color != current_color:
                    cell.figure.moved_by_two = False
                    cell.figure.can_en_passant = False

    def restart_game(self) -> None:
        """Function restarting the game.
        """
        self.loading_animation(0)
        for child in self.winfo_children():
            self.master.after(1, child.destroy) # optimized by 0.1s using after
        self.highlighted.clear()
        self.clicked_figure = None
        self.previous_coords = None
        self.current_turn = 'w'
        self.notification = None
        self.game_over = False
        self.board = self.create_board()
        self.destroy_loading_screen()

    def destroy_loading_screen(self) -> None:
        """Destroys loading screen widget.
        """
        if self.loading_screen:
            self.loading_screen.destroy()
        self.loading_screen = None

    def loading_animation(self, i: int) -> None:
        """Function to animate loading screen.

        Args:
            i (int, optional): Iteration value passed by recursive formula. Defaults to 0.
        """
        if not self.loading_screen:
            self.loading_screen = ctk.CTkLabel(
                master     = self.master,
                text       = 'Loading   ',
                font       = ctk.CTkFont(self.font_name, 42),
                text_color = COLOR.TEXT
            )
            self.loading_screen.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.master.after(21, lambda: self.loading_animation(0))
        else:
            self.loading_screen.configure(text=f'Loading{'.' * i}{' ' * (3 - i)}')
            if i <= 2:
                i += 1
                self.master.after(21, lambda: self.loading_animation(i))
            else:
                self.master.after(21, self.destroy_loading_screen)

    def load_board_from_file(self, file_info: dict) -> bool:
        """Updates board to match the state from the save file.

        Args:
            file_info (dict): All needed information to load save.

        Returns:
            bool: Returns True if load was successful, False otherwise.
        """
        try:
            self.current_turn = str(file_info['current_turn'])
            for row in self.board:
                for cell in row:
                    cell.figure = None
                    cell.update()
            for key, value in file_info['board_state'].items():
                coord: tuple[int, ...] = tuple(map(int, key.split(',')))
                match value[0]:
                    case 'Pawn':
                        pawn = piece.Pawn(value[1], self, (coord[0], coord[1]), self.notation_promotion)
                        if not value[2]:
                            pawn.first_move = False
                        self.board[coord[0]][coord[1]].figure = pawn
                    case 'Knight':
                        self.board[coord[0]][coord[1]].figure = piece.Knight(value[1], self, (coord[0], coord[1]))
                    case 'Bishop':
                        self.board[coord[0]][coord[1]].figure = piece.Bishop(value[1], self, (coord[0], coord[1]))
                    case 'Rook':
                        rook = piece.Rook(value[1], self, (coord[0], coord[1]))
                        self.board[coord[0]][coord[1]].figure = rook
                        if not value[2]:
                            rook.first_move = False
                    case 'Queen':
                        self.board[coord[0]][coord[1]].figure = piece.Queen(value[1], self, (coord[0], coord[1]))
                    case 'King':
                        king = piece.King(value[1], self, (coord[0], coord[1]))
                        self.board[coord[0]][coord[1]].figure = king
                        if not value[2]:
                            king.first_move = False
                self.board[coord[0]][coord[1]].update()
            self.moves_record.load_notation_from_save(file_info['white_moves'], file_info['black_moves'])
            self.game_over = file_info['game_over']
            return True
        except (KeyError, ValueError, IndexError) as e:
            return False
