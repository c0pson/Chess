import customtkinter as ctk

from notifications import Notification
from properties import COLOR

from tools import get_from_config

import piece

class Cell(ctk.CTkLabel):
    def __init__(self, frame, figure: piece.Piece | None, position: tuple[int, int], color: str, board) -> None:
        self.frame = frame
        self.position = position
        self.board = board
        self.figure: None | piece.Piece = figure
        figure_asset = self.figure.image if self.figure else None
        super().__init__(master=frame, image=figure_asset, text='', fg_color=color,
                        width=get_from_config('size'), height=get_from_config('size'), bg_color=COLOR.TRANSPARENT)
        self.bind('<Button-1>', self.on_click)
        self.pack(side=ctk.LEFT, padx=2, pady=2)

    def on_click(self, e) -> None:
        if self.figure and not self.board.clicked_figure:
            self.board.handle_clicks(self.figure, self.position)
        else:
            self.board.handle_move(self.position)

    def update(self) -> None:
        figure_asset = self.figure.image if self.figure else ''
        self.configure(image=figure_asset, require_redraw=True)

class Board(ctk.CTkFrame):
    def __init__(self, master, moves_record, size: int) -> None:
        super().__init__(master, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        self.master = master
        self.loading_screen: ctk.CTkLabel | None = None
        self.loading_animation(0)
        self.size = size
        self.board = self.create_board()
        self.previous_click: tuple[None, None] | tuple[int, int] = (None, None)
        self.highlighted: list[Cell] = []
        self.clicked_figure: piece.Piece | None = None
        self.previous_coords: tuple[int, int] | None = None
        self.current_turn = 'w'
        self.notification: None | Notification = None
        self.moves_record = moves_record
        self.capture = False

    @staticmethod
    def determine_tile_color(pos: tuple[int, int]) -> str:
        if (pos[0]%2 and pos[1]%2) or (not pos[0]%2 and not pos[1]%2):
            return COLOR.TILE_1
        else:
            return COLOR.TILE_2

    def create_outline_l_r_t(self):
        new_frame = ctk.CTkFrame(self, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        new_frame.pack(side=ctk.TOP, padx=0, pady=0, fill=ctk.X)
        ctk.CTkLabel(new_frame, text=f' ', font=ctk.CTkFont('Tiny5', self.size//3), text_color=COLOR.DARK_TEXT).pack(padx=1, pady=1)
        new_frame = ctk.CTkFrame(self, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        new_frame.pack(side=ctk.LEFT, padx=0, pady=0, fill=ctk.Y)
        for i in range(8):
            ctk.CTkLabel(new_frame, text=f'   {i+1}  ', font=ctk.CTkFont('Tiny5', self.size//3)).pack(side=ctk.TOP, padx=0, pady=0, expand=True)
        ctk.CTkLabel(new_frame, text='\n', font=ctk.CTkFont('Tiny5', 22)).pack(side=ctk.BOTTOM, padx=0, pady=0)
        new_frame = ctk.CTkFrame(self, fg_color=COLOR.DARK_TEXT, corner_radius=0)
        new_frame.pack(side=ctk.RIGHT, padx=0, pady=0, fill=ctk.Y)
        ctk.CTkLabel(new_frame, text=f'{' ' * 7}', font=ctk.CTkFont('Tiny5', self.size//3), text_color=COLOR.DARK_TEXT).pack(padx=1, pady=1)

    def create_board(self) -> list[list[Cell]]:
        self.create_outline_l_r_t()
        board: list[list[Cell]] = []
        board_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR.DARK_TEXT)
        board_frame.pack(side=ctk.TOP, padx=0, pady=0)
        piece_positions = {
            (0, 0): piece.Rook('b', self, (0, 0)), (0, 7): piece.Rook('b', self, (0, 7)),
            (7, 0): piece.Rook('w', self, (7, 0)), (7, 7): piece.Rook('w', self, (7, 7)),
            (0, 1): piece.Knight('b', self, (0, 1)), (0, 6): piece.Knight('b', self, (0, 6)),
            (7, 1): piece.Knight('w', self, (7, 1)), (7, 6): piece.Knight('w', self, (7, 6)),
            (0, 2): piece.Bishop('b', self, (0, 2)), (0, 5): piece.Bishop('b', self, (0, 5)),
            (7, 2): piece.Bishop('w', self, (7, 2)), (7, 5): piece.Bishop('w', self, (7, 5)),
            (0, 3): piece.Queen('b', self, (0, 3)), (7, 3): piece.Queen('w', self, (7, 3)),
            (0, 4): piece.King('b', self, (0, 4)), (7, 4): piece.King('w', self, (7, 4))
        }
        for i in range(8):
            row = []
            new_frame = ctk.CTkFrame(board_frame, fg_color=COLOR.TRANSPARENT)
            new_frame.pack(padx=0, pady=0)
            for j in range(8):
                if self.loading_screen:
                    self.loading_screen.lift()
                color = self.determine_tile_color((i, j))
                figure = piece_positions.get((i, j)) if (i, j) in piece_positions else (piece.Pawn('b' if i == 1 else 'w', self, (i, j), self.notation_promotion) if i in [1, 6] else None)
                cell = Cell(new_frame, figure, (i, j), color, self)
                row.append(cell)
            board.append(row)
        new_frame = ctk.CTkFrame(self, fg_color=COLOR.TRANSPARENT, corner_radius=0)
        new_frame.pack(padx=2, pady=2, fill=ctk.X)
        for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            ctk.CTkLabel(new_frame, text=letter, font=ctk.CTkFont('Tiny5', self.size//3)).pack(side=ctk.LEFT, padx=0, pady=0, expand=True)
        return board

    def remove_highlights(self) -> None:
        for cell in self.highlighted:
            color = self.determine_tile_color(cell.position)
            cell.configure(fg_color=color)
        self.highlighted = []

    def display_message(self, message: str, duration_sec: int) -> None:
        if self.notification:
            self.notification.destroy()
        self.notification = Notification(self, message=message, duration_sec=duration_sec)

    def is_game_over(self) -> tuple[bool, bool]:
        in_check = False
        for row in self.board:
            for cell in row:
                if cell.figure and cell.figure.color == self.current_turn:
                    possible_moves = cell.figure.check_possible_moves(self.current_turn)
                    for move in possible_moves:
                        if not self.check_check(cell.figure.position, move):
                            return False, False
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.King) and cell.figure.color == self.current_turn:
                    if self.check_check(cell.figure.position, cell.figure.position):
                        in_check = True
                        break
        return True, in_check

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
                check = self.check_check(position, coords)
                if not check:
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

    def is_under_attack(self, position: tuple[int, int], color: str) -> bool:
        for row in self.board:
            for cell in row:
                if cell.figure and cell.figure.color != color:
                    if position in cell.figure.check_possible_moves(cell.figure.color, checking=True):
                        return True
        return False

    def handle_move(self, position: tuple[int, int]) -> None:
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
                    if isinstance(self.clicked_figure, piece.King):
                        if abs(col - self.previous_coords[1]) == 2:
                            if col == 6:
                                self.board[row][5].figure = self.board[row][7].figure
                                self.board[row][7].figure = None
                                self.board[row][5].figure.position = (row, 5) # type: ignore
                                self.board[row][5].update()
                                self.board[row][7].update()
                                self.moves_record.record_move(self.clicked_figure, castle="kingside")
                                castle = True
                            elif col == 2:
                                self.board[row][3].figure = self.board[row][0].figure
                                self.board[row][0].figure = None
                                self.board[row][3].figure.position = (row, 3) # type: ignore
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
                        else:
                            cell.figure.moved_by_two = False
                        if cell.figure.promote():
                            promotion = True
                    self.reset_en_passant_flags(cell.figure.color)
                    if cell.figure.first_move:
                        cell.figure.first_move = False
                    self.current_turn = 'b' if self.current_turn == 'w' else 'w'
                    check = self.is_under_attack(self.get_king_position(self.current_turn), self.current_turn)
                    game_over, in_check = self.is_game_over()
                    if game_over:
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
            if not promotion:
                self.clicked_figure = None
                self.previous_coords = None
        self.remove_highlights()

    def notation_promotion(self, promotion:str) -> None:
        capture = self.capture
        check = self.is_under_attack(self.get_king_position(self.current_turn), self.current_turn)
        game_over, in_check = self.is_game_over()
        if game_over:
            if in_check:
                self.display_message(f'Checkmate  {"White wins!" if self.current_turn == "b" else "Black wins!"}', 9)
                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
            else:
                self.display_message('Stalemate', 9)
                self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        else:
            self.moves_record.record_move(self.clicked_figure, capture=capture, previous_coords=self.previous_coords, check=check, checkmate=game_over and in_check, promotion=promotion[0])
        self.clicked_figure = None
        self.previous_coords = None

    def get_king_position(self, color: str) -> tuple[int, int]:
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.King) and cell.figure.color == color:
                    return cell.figure.position
        return (-1, -1)

    def reset_en_passant_flags(self, current_color):
        for row in self.board:
            for cell in row:
                if isinstance(cell.figure, piece.Pawn) and cell.figure.color != current_color:
                    cell.figure.moved_by_two = False
                    cell.figure.can_en_passant = False

    def restart_game(self) -> None:
        self.loading_animation(0)
        for child in self.winfo_children():
            if child != self.loading_screen:
                child.destroy()
        self.previous_click = (None, None)
        self.highlighted = []
        self.clicked_figure = None
        self.previous_coords = None
        self.current_turn = 'w'
        self.notification = None
        self.board = self.create_board()

    def destroy_loading_screen(self) -> None:
        self.loading_screen.destroy() # type: ignore
        self.loading_screen = None

    def loading_animation(self, i) -> None:
        if not self.loading_screen:
            self.loading_screen = ctk.CTkLabel(self.master, text='Loading   ', font=ctk.CTkFont('Tiny5', 42),
                                                text_color=COLOR.TEXT)
            self.loading_screen.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.loading_screen.lift()
            self.master.after(270, lambda: self.loading_animation(0))
        else:
            self.loading_screen.lift()
            self.loading_screen.configure(text=f'Loading{'.' * i}{' ' * (3 - i)}')
            if i <= 2:
                i += 1
                self.master.after(270, self.loading_animation, i)
            else:
                self.master.after(270, self.destroy_loading_screen)
