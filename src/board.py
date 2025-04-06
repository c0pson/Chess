"""File containing implementation for Board and Cells on the board.
"""

import customtkinter as ctk
from typing import Any
from properties import COLOR, SYSTEM
if SYSTEM == 'Windows':
    import pywinstyles
from PIL import Image
import os
import threading
import soundfile
from typing import cast, Generator, NoReturn
import re

from notifications import Notification
from menus import MovesRecord
from tools import get_from_config, resource_path, play_sound, update_error_log
import piece

class Cell(ctk.CTkLabel):
    """Class handling actions inside specific cell.

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
        self.cell_size = get_from_config('size')
        super().__init__(
            master   = frame,
            image    = figure_asset,
            text     = '',
            fg_color = color,
            width    = self.cell_size,
            height   = self.cell_size,
            bg_color = COLOR.BACKGROUND
        )
        self.bind('<Button-1>', self.on_click)
        self.pack(side=ctk.LEFT, padx=2, pady=2)

    def on_click(self, event: Any) -> None:
        """Handles clicks by calling board functions handling game logic. If user clicks wrong cell the illegal move sound effect
        will play. To avoid calling functions more than necessary it checks if the previously clicked figure isn't the same as 
        currently clicked one and if the color of current player turn is the same as figure which is being clicked.

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
             - setups all important variables
             - loads all sound files
             - loads font with different sizes
             - creates board with default figure placement
             - calls loading_animation for better user experience

        Args:
            master (Any): Parent widget.
            moves_record (MovesRecord): class handling move records.
            size (int): Size of the tiles and fonts.
        """
        super().__init__(master, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        self.master: Any = master
        self.loading_screen: ctk.CTkLabel | None = None
        self.font_name: str = str(get_from_config('font_name'))
        self.font_42  = ctk.CTkFont(self.font_name, 42)
        self.master.after(1, lambda: self.loading_animation(0))
        self.pack(side=ctk.RIGHT, padx=10, pady=10, expand=True, ipadx=5, ipady=5, anchor=ctk.CENTER)
        threading.Thread(target=self.load_sound).start()
        self.frame_image: ctk.CTkImage = ctk.CTkImage(Image.open(resource_path(os.path.join('assets', 'menu', 'frame.png'))).convert('RGBA'), size=(80, 80))
        self.size: int = size
        self.turns: Generator[str, None, NoReturn] = self.turn()
        self.current_turn = next(self.turns)
        self.board_font = ctk.CTkFont(self.font_name, self.size // 3)
        self.board: list[list[Cell]] = self.create_board()
        self.highlighted: list[Cell] = []
        self.clicked_figure: piece.Piece | None = None
        self.previous_coords: tuple[int, int] | None = None
        self.notification: None | Notification = None
        self.moves_record: MovesRecord = moves_record
        self.capture: bool = False
        self.game_over: bool = False
        self.destroy_loading_screen()

    def load_sound(self):
        self.move_sound = soundfile.read(resource_path(os.path.join('sounds', 'move-self.wav')), dtype='float32')[0]
        self.capture_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.move_check_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.castle_sound = soundfile.read(resource_path(os.path.join('sounds', 'capture.wav')), dtype='float32')[0]
        self.end_game_sound = soundfile.read(resource_path(os.path.join('sounds', 'game-end.wav')), dtype='float32')[0]
        self.illegal_sound = soundfile.read(resource_path(os.path.join('sounds', 'illegal.wav')), dtype='float32')[0]

    @staticmethod
    def determine_tile_color(pos: tuple[int, int]) -> str:
        """Static method to determine color of the tile on the board.

        Args:
            pos (tuple[int, int]): Position of the cell on the board.

        Returns:
            str: Color of the cell.
        """
        return COLOR.TILE_1 if (pos[0] % 2) == (pos[1] % 2) else COLOR.TILE_2

    def create_outline_l_r_t(self) -> None:
        """Creates outline of the board with coordinates notation.
        """
        ctk.CTkLabel(
            master     = self,
            text       =f' ',
            font       =self.board_font,
            text_color =COLOR.DARK_TEXT
        ).pack(padx=10, pady=1)
        new_frame = ctk.CTkFrame(
            master        = self,
            fg_color      = COLOR.DARK_TEXT,
            corner_radius = 0
        )
        new_frame.pack(side=ctk.LEFT, padx=3, pady=0, fill=ctk.Y)
        for i in range(8, 0, -1):
            ctk.CTkLabel(
                master   = new_frame,
                text     = f' {i}',
                font     = self.board_font,
                fg_color = COLOR.DARK_TEXT,
                anchor   = ctk.W
            ).pack(side=ctk.TOP, padx=10, pady=1, expand=True)
        ctk.CTkLabel(
            master = new_frame,
            text   = ' ',
            font   = ctk.CTkFont(self.font_name, int(int(get_from_config('size')) * 0.4))
        ).pack(side=ctk.BOTTOM, padx=0, pady=0)
        new_frame = ctk.CTkFrame(
            master   = self,
            fg_color = COLOR.DARK_TEXT,
            corner_radius=0
        )
        new_frame.pack(side=ctk.RIGHT, padx=1, pady=0, fill=ctk.Y)
        ctk.CTkLabel(
            master     = new_frame, 
            text       = '',
            font       = self.board_font, 
            text_color = COLOR.DARK_TEXT, 
            fg_color   = COLOR.DARK_TEXT,
            width      = int(int(get_from_config('size')) * 0.4)
        ).pack(padx=10, pady=1)

    def create_board(self) -> list[list[Cell]]:
        """Creates a board filled with colored tiles and figures. Uses prepared dictionary of the correct figures positions to place the Figures.

        Returns:
            list[list[Cell]]: 2D representation of the board.
        """
        self.create_outline_l_r_t()
        board: list[list[Cell]] = cast(list[list[Cell]], [[None] * 8] * 8)
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
            row: list[Cell] = cast(list[Cell], [None] * 8)
            new_frame: ctk.CTkFrame = ctk.CTkFrame(
                master        = board_frame,
                fg_color      = COLOR.DARK_TEXT,
                corner_radius = 0
            )
            new_frame.pack(padx=0, pady=0)
            for j in range(8):
                color: str = self.determine_tile_color((i, j))
                figure: piece.Piece | None = piece_positions.get((i, j)) if (i, j) in piece_positions else (
                    piece.Pawn('b' if i == 1 else 'w', self, (i, j), self.notation_promotion) if i in [1, 6] else None
                )
                cell = Cell(new_frame, figure, (i, j), color, self)
                row[j] = cell
            board[i] = row
        new_frame = ctk.CTkFrame(
            master        = self,
            fg_color      = COLOR.DARK_TEXT,
            corner_radius = 0
        )
        new_frame.pack(padx=0, pady=1, fill=ctk.X)
        for letter in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'):
            ctk.CTkLabel(
                master   = new_frame,
                text     = letter,
                font     = self.board_font,
                fg_color = COLOR.DARK_TEXT
            ).pack(side=ctk.LEFT, padx=2, pady=0, expand=True)
        return board

    def remove_highlights(self) -> None:
        """Removes highlights from the cells. Ensures proper move handling and enhances user experience.
        """
        for cell in self.highlighted:
            cell.configure(fg_color=self.determine_tile_color(cell.position))
        self.highlighted.clear()

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
        """Checks if checkmate or stalemate occurred. Is also used to check if the king is in check in handle_move method.
        Function scans all combinations of moving the King, if found at leas one, loop breaks to check if king is in check.

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
        king_position = self.get_king_position(self.current_turn)
        in_check = self.is_under_attack(king_position, self.current_turn)
        return (not has_legal_moves, in_check)

    def handle_clicks(self, figure: piece.Piece, position: tuple[int, int]) -> None:
        """Handles actions after clicking on a specific cell. Function filter from all possible moves for the figure to only these which are legal.
        After filtering the moves to only legal ones, proper tiles are being highlighted.

        Args:
            figure (piece.Piece): Chosen figure.
            position (tuple[int, int]): Position of that figure.
        """
        if self.game_over:
            return
        self.handle_chosen_figure_highlight(position)
        possible_moves = figure.check_possible_moves(self.current_turn)
        if not possible_moves and self.board[position[0]][position[1]].figure:
            self.previous_coords = position
            return
        self.clicked_figure = figure if figure else None
        self.previous_coords = position
        if self.board and possible_moves:
            valid_moves = []
            for coords in possible_moves:
                if not self.check_check(position, coords):
                    valid_moves.append(coords)
            for coords in valid_moves:
                x_ = coords[0]
                y_ = coords[1]
                color = self.board[x_][y_].cget('fg_color')
                new_color = COLOR.HIGH_TILE_1 if color == COLOR.TILE_1 else COLOR.HIGH_TILE_2
                self.board[x_][y_].configure(fg_color=new_color)
                self.highlighted.append(self.board[x_][y_])

    def hide_clicked_figure_frame(self) -> None:
        """Hides the frame or highlight around the chosen figure.
        """
        if self.previous_coords:
            previous_x = self.previous_coords[0]
            previous_y = self.previous_coords[1]
            if SYSTEM == 'Windows':
                if frame := self.board[previous_x][previous_y].frame_around:
                    frame.destroy()
            else:
                self.board[previous_x][previous_y].configure(fg_color=self.determine_tile_color(self.previous_coords))

    def handle_chosen_figure_highlight(self, position: tuple[int, int]) -> None:
        """Highlights with frame or color under the tile of the figure for better visibility and improved user experience.  

        Args:
            position (tuple[int, int]): _description_
        """
        self.hide_clicked_figure_frame()
        x: int = position[0]
        y: int = position[1]
        if SYSTEM == 'Windows':
            image_test: ctk.CTkLabel = ctk.CTkLabel(
                    fg_color = COLOR.TRANSPARENT_MASK,
                    master   = self.board[x][y],
                    text     = '',
                    image    = self.frame_image
            )
            pywinstyles.set_opacity(image_test, value=1, color=COLOR.TRANSPARENT_MASK)
            image_test.place(relx=0.5, rely=0.5, anchor='center')
            self.board[x][y].frame_around = image_test
        else:
            self.board[x][y].configure(fg_color=COLOR.TEXT)

    def check_check(self, move_from: tuple[int, int], move_to: tuple[int, int]) -> bool:
        """Checks if King is in a check. Checks if any of the opponents figure are causing the check. If any found loop breaks to improve performance.

        Args:
            move_from (tuple[int, int]): Starting position.
            move_to (tuple[int, int]): Desired position.

        Returns:
            bool: _description_
        """
        move_to_x: int = move_to[0]
        move_to_y: int = move_to[1]
        move_from_x: int = move_from[0]
        move_from_y: int = move_from[1]
        original_from_figure: piece.Piece | None = self.board[move_from_x][move_from_y].figure
        original_to_figure: piece.Piece | None = self.board[move_to_x][move_to_y].figure
        self.board[move_to_x][move_to_y].figure = original_from_figure
        self.board[move_from_x][move_from_y].figure = None
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
        self.board[move_from_x][move_from_y].figure = original_from_figure
        self.board[move_to_x][move_to_y].figure = original_to_figure
        return is_in_check

    def is_under_attack(self, position: tuple[int, int], color: str) -> bool:
        """Checks if king is under attack.

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
        """Function handles moving pieces on the board. Calls notations functions, plays sounds appropriately to the move and removes previous highlights.

        Args:
            position (tuple[int, int]): Position of the figure.
        """
        if self.clicked_figure and self.clicked_figure.position == position:
            return
        if self.previous_coords:
            prev_x: int = self.previous_coords[0]
            prev_y: int = self.previous_coords[1]
            if SYSTEM == 'Windows':
                if x := self.board[prev_x][prev_y].frame_around:
                    x.destroy()
            else:
                self.board[prev_x][prev_y].configure(fg_color=self.determine_tile_color(self.previous_coords))
        if self.clicked_figure and self.previous_coords:
            row, col = position
            cell = self.board[row][col]
            self.capture = bool(cell.figure)
            promotion = False
            if cell in self.highlighted:
                castle = False
                if not self.check_check(self.previous_coords, position):
                    if isinstance(self.clicked_figure, piece.Pawn) and self.clicked_figure.can_en_passant and col != prev_y and not cell.figure:
                        self.board[row - self.clicked_figure.move][col].figure = None
                        self.board[row - self.clicked_figure.move][col].update()
                        self.capture = True
                    if isinstance(self.clicked_figure, piece.King):
                        if abs(col - prev_y) == 2:
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
                    self.board[prev_x][prev_y].figure = None
                    self.board[prev_x][prev_y].update()
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
                    self.current_turn = next(self.turns)
                    game_over, in_check = self.is_game_over()
                    if game_over:
                        self.handle_game_over(in_check, promotion, self.capture, in_check)
                    elif not castle and not promotion:
                        self.moves_record.record_move(self.clicked_figure, capture=self.capture, previous_coords=self.previous_coords, check=in_check, checkmate=game_over and in_check)
                threading.Thread(target=lambda: self.play_correct_sound(game_over, self.capture, castle, in_check)).start()
            if not promotion:
                self.clicked_figure = None
                self.previous_coords = None
        if self.highlighted:
            self.remove_highlights()

    def turn(self) -> Generator[str, None, NoReturn]:
        """Simple infinite yielding function for easy turn changing.

        Yields:
            Generator[str, None, NoReturn]: Current turn color representation.
        """
        while True:
            yield 'w'
            yield 'b'

    def play_correct_sound(self, game_over: bool, capture: bool, castle: bool, check: bool) -> None:
        """Plays sound according to the users move.

        Args:
            game_over (bool): Flag corresponding to game over.
            capture (bool): Flag corresponding to capturing other piece.
            castle (bool): Flag corresponding to castle move.
            check (bool): Flag corresponding to check.
        """
        if game_over:
            play_sound(self.end_game_sound)
        elif capture:
            play_sound(self.capture_sound)
        elif castle:
            play_sound(self.castle_sound)
        elif check:
            play_sound(self.move_check_sound)
        else:
            play_sound(self.move_sound)

    def handle_game_over(self, in_check: bool, promotion: bool, capture: bool, check: bool) -> None:
        """Handles displaying notification of who won or if it was a stalemate. Sets game_over flag to True, and notates the end of the game.

        Args:
            in_check (bool): Flag corresponding to check.
            promotion (bool): Flag corresponding to pawn promotion.
            capture (bool): Flag corresponding to capturing other piece.
            check (bool): Flag corresponding to check
        """
        self.game_over = True
        if in_check:
            self.display_message(f'Checkmate  {"White wins!" if self.current_turn == "b" else "Black wins!"}', 9)
            if not promotion and self.clicked_figure:
                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=True, checkmate=check and in_check)
        else:
            self.display_message('Stalemate', 9)
            if not promotion and self.clicked_figure:
                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=False, checkmate=check and in_check)

    def notation_promotion(self, promotion:str) -> None:
        """Helper function to note the promotion of the pawn. Calls pawn functions corresponding to choosing figure to promote to. Notates the promotion

        Args:
            promotion (str): Figure representation to which pawn was promoted.
        """
        check = self.is_under_attack(self.get_king_position(self.current_turn), self.current_turn)
        game_over, in_check = self.is_game_over()
        if game_over:
            if in_check:
                self.display_message(f'Checkmate  {"White wins!" if self.current_turn == "b" else "Black wins!"}', 9)
                if self.clicked_figure:
                    self.moves_record.record_move(self.clicked_figure, capture=self.capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
            else:
                self.display_message('Stalemate', 9)
                if self.clicked_figure:
                    self.moves_record.record_move(self.clicked_figure, capture=self.capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        else:
            if self.clicked_figure:
                self.moves_record.record_move(self.clicked_figure, capture=self.capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        self.clicked_figure = None
        self.previous_coords = None

    def get_king_position(self, color: str) -> tuple[int, int]:
        """Function returning king position on the board. Loop searching for king just breaks after finding king with correct color.

        Args:
            color (str): Color of the king.

        Returns:
            tuple[int, int]: Position of the king.
        """
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.King) and cell.figure.color == color:
                    return cell.figure.position
        update_error_log(Exception('Not enough kings on the board, check the save file'))
        Notification(self.master, 'No king on the board, check save file', 2, 'top')
        self.game_over = True
        self.master.after(2001, self.restart_game)
        raise Exception('Not enough kings on the board, check the save file')

    def reset_en_passant_flags(self, current_color: str) -> None:
        """Helper function to reset en passant and first move flag.

        Args:
            current_color (str): Color of the current player.
        """
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.Pawn) and cell.figure.color != current_color:
                    cell.figure.moved_by_two = False
                    cell.figure.can_en_passant = False

    def restart_game(self) -> None:
        """Function restarting the game with all necessary flags and variables.
        """
        self.loading_animation(0)
        for child in self.winfo_children():
            self.master.after(1, child.destroy)
        self.highlighted.clear()
        self.clicked_figure = None
        self.previous_coords = None
        self.turns = self.turn()
        self.current_turn = next(self.turns)
        self.notification = None
        self.game_over = False
        self.board = self.create_board()

    def destroy_loading_screen(self) -> None:
        """Destroys loading screen widget."""
        def update_opacity(i: int) -> None:
            if i >= 0 and self.loading_screen:
                pywinstyles.set_opacity(self.loading_screen, value=i*0.005, color='#000001')
                self.master.after(1, lambda: update_opacity(i - 1))
            else:
                if self.loading_screen:
                    self.loading_screen.destroy()
                    self.loading_screen = None
        if self.loading_screen:
            update_opacity(200)

    def loading_animation(self, i: int) -> None:
        """Function to animate loading screen.

        Args:
            i (int, optional): Iteration value passed by recursive formula. Defaults to 0.
        """
        if not self.loading_screen:
            self.loading_screen = ctk.CTkFrame(
                master     = self.master,
                fg_color   = COLOR.BACKGROUND
            )
            self.loading_screen.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.loading_text = ctk.CTkLabel(
                master     = self.loading_screen,
                text       = 'Loading   ',
                font       = self.font_42,
                text_color = COLOR.TEXT,
            )
            self.loading_text.pack(side=ctk.TOP, expand=True)
            self.master.after(90, lambda: self.loading_animation(0))
        else:
            self.loading_text.configure(text=f'Loading{'.' * i}{' ' * (3 - i)}')
            if i <= 2:
                i += 1
                self.master.after(90, lambda: self.loading_animation(i))
            else:
                self.master.after(90, self.destroy_loading_screen)

    def update_board(self) -> None:
        """Updates all cells on the board
        """
        for row in self.board:
            for cell in row:
                cell.update()

    def load_board_from_file(self, file_info: dict) -> bool:
        """Updates board to match the state from the save file. Ensures all save information are in the file in correct format.

        Args:
            file_info (dict): All needed information to load save.

        Returns:
            bool: Returns True if load was successful, False otherwise.
        """
        self.master.after(1, lambda: self.loading_animation(0))
        save_keys: set[str] = {'current_turn', 'board_state', 'white_moves', 'black_moves', 'game_over'}
        if not all(key in file_info for key in save_keys):
            update_error_log(KeyError('Save file doesn\'t contain all necessary information'))
            return False
        king_w: int = 0
        king_b: int = 0
        for row in self.board:
            for cell in row:
                if cell.figure:
                    cell.figure = None
                    cell.update()
        for key, value in file_info['board_state'].items():
            if not bool(re.match(r'[0-9]{1},[0-9]{1}', key)):
                self.restart_game()
                update_error_log(KeyError('Save file doesn\'t contain all necessary information'))
                return False
            try:
                value[1]
                value[2]
            except:
                self.restart_game()
                update_error_log(KeyError('Save file doesn\'t contain all necessary information'))
                return False
            if not bool(re.match(r'[wb]{1}', value[1])):
                self.restart_game()
                update_error_log(KeyError('Save file doesn\'t contain all necessary information'))
                return False
            coord: tuple[int, ...] = tuple(map(int, key.split(',')))
            x: int = coord[0]
            y: int = coord[1]
            match value[0]:
                case 'Pawn':
                    pawn = piece.Pawn(value[1], self, (x, y), self.notation_promotion)
                    if not value[2]:
                        pawn.first_move = False
                    self.board[x][y].figure = pawn
                case 'Knight':
                    self.board[x][y].figure = piece.Knight(value[1], self, (x, y))
                case 'Bishop':
                    self.board[x][y].figure = piece.Bishop(value[1], self, (x, y))
                case 'Rook':
                    rook = piece.Rook(value[1], self, (x, y))
                    self.board[x][y].figure = rook
                    if not value[2]:
                        rook.first_move = False
                case 'Queen':
                    self.board[x][y].figure = piece.Queen(value[1], self, (x, y))
                case 'King':
                    king = piece.King(value[1], self, (x, y))
                    self.board[x][y].figure = king
                    if not value[2]:
                        king.first_move = False
                    king_w += 1 if value[1] == 'w' else 0
                    king_b += 1 if value[1] == 'b' else 0
            self.master.after(1, self.board[x][y].update)
        if king_w != 1 or king_b != 1:
            update_error_log(KeyError('Save file doesn\'t contain proper amount of kings'))
            return False
        current_turn = str(file_info['current_turn'])
        self.turns = self.turn()
        if current_turn == 'b':
            self.current_turn = next(self.turns)
            self.current_turn = next(self.turns)
        else:
            self.current_turn = next(self.turns)
        self.master.after(21, lambda: self.moves_record.load_notation_from_save(file_info['white_moves'], file_info['black_moves']))
        self.master.after(21, self.hide_clicked_figure_frame)
        self.master.after(21, self.remove_highlights)
        self.game_over = file_info['game_over']
        self.clicked_figure = None
        return True
