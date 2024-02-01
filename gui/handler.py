import pygame
import subprocess
import sys
import os
import time
from helpers import Stack, Colour, Move, InputBuffer


# TODO: debug!


WHITE = (255, 255, 255)
GREEN = (118, 150, 86)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Handler:
    """
    Handler class for the GUI.
    """

    def __init__(self, verbose=0, engine_path=None, engine_directory=None, movetime=1000, engine_color=Colour.BLACK):
        root_path = '/'.join(os.getcwd().split('/')[:-1])
        if engine_path is None:
            engine_path = root_path + "/target/release/rust-chess-bot"
        if engine_directory is None:
            engine_directory = root_path
        assert os.path.exists(engine_path), f"Engine path {engine_path} does not exist."
        assert os.path.exists(engine_directory), f"Engine directory {engine_directory} does not exist."
        self.engine_path = engine_path
        self.engine_directory = engine_directory
        self.verbose = verbose

        self.engine_colour = engine_color
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 800
        self.ROWS, self.COLS = 8, 8
        self.SQUARE_SIZE = self.WIDTH // self.COLS
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess")
        self.images = self.load_images()
        self.board = self.initial_board_state()
        self.engine = None
        self.input_buffer = InputBuffer()
        self.move_stack = Stack()
        self.colour_to_move = Colour.WHITE
        self.base_freq = 0.1
        self.movetime = movetime

    def get_engine_colour(self):
        """
        Prompt the user for the engine colour.
        """
        while True:
            player_colour = input("Choose your colour (w/b): ")
            if player_colour in ["w", "b"]:
                return Colour.WHITE if player_colour == "b" else Colour.BLACK
            print("Invalid input. Please enter 'w' or 'b'.")

    def quit(self):
        """
        Quit the GUI.
        """
        self.engine.kill()
        pygame.quit()
        sys.exit()

    def load_images(self):
        """
        Load the images for the pieces.
        """
        pieces = ["pawn", "bishop", "knight", "rook", "queen", "king"]
        colors = ["white", "black"]
        images = {}
        for piece in pieces:
            for color in colors:
                images[f"{color}-{piece}"] = pygame.transform.scale(
                    pygame.image.load(os.path.join("assets", f"{color}-{piece}.png")),
                    (self.SQUARE_SIZE, self.SQUARE_SIZE))
        return images

    @staticmethod
    def initial_board_state():
        """
        Initialize the board state for a new game.
        """
        board = [[None for _ in range(8)] for _ in range(8)]
        pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        colors = ["white", "black"]
        for i, piece in enumerate(pieces):
            board[0][i] = f"{colors[0]}-{piece}"
            board[7][i] = f"{colors[1]}-{piece}"
        for i in range(8):
            board[1][i] = f"{colors[0]}-pawn"
            board[6][i] = f"{colors[1]}-pawn"
        return board
    
    def color_square(self, row, col, color):
        """
        Color the square at (row, col) with the given color.
        a1 is (0, 0), h8 is (7, 7).
        """
        row = 7 - row
        pygame.draw.rect(self.screen, color, (
            col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
        
    def draw_piece(self, row, col, piece):
        """
        Draw the piece at (row, col).
        a1 is (0, 0), h8 is (7, 7).
        """
        row = 7 - row
        self.screen.blit(self.images[piece],
                         pygame.Rect(col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE,
                                     self.SQUARE_SIZE))

    def highlight_last_move(self):
        if not self.move_stack.is_empty():
            last_move = self.move_stack.peek()
            self.color_square(last_move.from_row, last_move.from_col, YELLOW)
            self.color_square(last_move.to_row, last_move.to_col, YELLOW)

    def highlight_selected_piece(self):
        if self.input_buffer.piece is not None:
            self.color_square(self.input_buffer.row, self.input_buffer.col, RED)

    def draw_board(self):
        """
        Draw the board.
        """
        self.screen.fill(GREEN)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (row + col) % 2 == 0:
                    self.color_square(row, col, WHITE)
        self.highlight_last_move()
        self.highlight_selected_piece()
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = self.board[row][col]
                if piece:
                    self.draw_piece(row, col, piece)
        pygame.display.update()

    def handle_event(self, event):
        """
        Handle an event.
        """
        match event.type:
            case pygame.QUIT:
                self.quit()
            case pygame.MOUSEBUTTONDOWN:
                self.handle_click()
            case _:
                pass
        self.draw_board()

    def handle_click(self):
        """
        Handle a click.
        ignoring promotion for now.
        TODO: allow promotion selection.
        """
        pos = pygame.mouse.get_pos()
        row, col = 7 - (pos[1] // self.SQUARE_SIZE), pos[0] // self.SQUARE_SIZE
        if self.input_buffer.piece is None:
            if self.board[row][col] is not None:
                self.input_buffer.piece = self.board[row][col]
                self.input_buffer.row = row
                self.input_buffer.col = col
            return
        move = Move(self.input_buffer.row, self.input_buffer.col, row, col)
        piece, colour = self.input_buffer.piece.split('-')
        if piece == 'pawn' and row in [0, 7]:
            move.promoted_piece = f'{colour}-queen'
        if not self.is_legal_move(move):
            self.input_buffer.flush()
            return
        move.move_type = self.deduce_move_type(move.from_row, move.from_col, move.to_row, move.to_col)
        self.make_move(move)
        self.check_game_status()
        self.make_engine_move()
        self.check_game_status()

    @staticmethod
    def move_to_string(move: Move):
        """
        Convert a move to a string.
        """
        letters = 'abcdefgh'
        from_col = letters[move.from_col]
        to_col = letters[move.to_col]
        from_row = move.from_row + 1
        to_row = move.to_row + 1
        move_string = f'{from_col}{from_row}{to_col}{to_row}'
        piece_initials = {'knight': 'n', 'bishop': 'b', 'rook': 'r', 'queen': 'q'}
        if move.promoted_piece is not None:
            move_string += piece_initials[move.promoted_piece.split('-')[1]]
        return move_string

    def is_legal_move(self, move: Move):
        """
        Make a call to the engine to check if the move is legal.
        """
        position_command = self.construct_position_command()
        self.send_command(position_command)
        self.send_command(f'islegal {self.move_to_string(move)}')
        while True:
            output = self.read_engine_output()
            if output in ['legal', 'illegal']:
                return output == 'legal'
            time.sleep(self.base_freq)

    def get_game_status(self):
        """
        Make a call to the engine to check if game is over.
        """
        position_command = self.construct_position_command()
        self.send_command(position_command)
        self.send_command('gameover')
        while True:
            output = self.read_engine_output()
            if output in ['checkmate', 'stalemate', 'game not over']:
                return output
            time.sleep(self.base_freq)

    def check_game_status(self):
        game_status = self.get_game_status()
        if game_status != "game not over":
            print(game_status)
            print("Good game!")
            time.sleep(5)
            self.quit()

    def start_engine(self):
        """
        Start the engine.
        """
        self.engine = subprocess.Popen(
            self.engine_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            cwd=self.engine_directory,
        )

    def test_engine(self, timeout=3000):
        """
        param timeout: Timeout in milliseconds.
        """
        ready = False
        self.send_command('uci')
        for i in range(timeout // 100):
            output = self.read_engine_output()
            if output == 'uciok':
                ready = True
                break
            time.sleep(self.base_freq)
        if not ready:
            print("Engine timed out.")
            self.quit()

    def send_command(self, command):
        """
        Send a command to the engine.
        """
        if self.verbose:
            print(f"Sending: {command}")
        self.engine.stdin.write(command + '\n')

    def read_engine_output(self):
        """
        Read the engine output.
        """
        out = self.engine.stdout.readline().strip()
        if out and self.verbose:
            print(f"Received: {out}")
        return out

    def make_engine_move(self):
        """
        Process the move from the engine.
        """
        position_command = self.construct_position_command()
        self.send_command(position_command)
        self.send_command('go movetime {}'.format(self.movetime))
        move_string = self.read_engine_move()
        engine_move = self.build_engine_move(move_string)
        self.make_move(engine_move)

    def construct_position_command(self):
        """
        Construct the position command to send to the engine.
        """
        position_command = 'position startpos moves'
        for move in self.move_stack.stack:
            position_command += (' ' + self.move_to_string(move))
        return position_command

    def read_engine_move(self):
        """
        Read the move from the engine's output.
        """
        while True:
            output = self.read_engine_output()
            if output.startswith('bestmove'):
                _, move = output.split()
                return move
            time.sleep(self.base_freq)

    def build_engine_move(self, engine_move):
        """
        Engine move is in the form 'e2e4'.
        Convert it to a Move object.
        """
        from_row, from_col = 7 - (ord(engine_move[1]) - ord('1')), ord(engine_move[0]) - ord('a')
        to_row, to_col = 7 - (ord(engine_move[3]) - ord('1')), ord(engine_move[2]) - ord('a')
        from_row, to_row = 7 - from_row, 7 - to_row
        if len(engine_move) > 4:
            promoted_piece = engine_move[4]
            move_type = 'promotion'
        else:
            promoted_piece = None
            move_type = self.deduce_move_type(from_row, from_col, to_row, to_col)
        return Move(from_row, from_col, to_row, to_col, move_type=move_type, promoted_piece=promoted_piece)

    def deduce_move_type(self, from_row, from_col, to_row, to_col):
        """
        Deduce the move type, given the move coordinates.
        Possible move types:
            - normal
            - capture
            - long castle
            - short castle
            - promotion
            - en passant
        """
        color, piece = self.board[from_row][from_col].split('-')
        if piece == 'pawn':
            if to_row in [0, 7]:
                return 'promotion'
            if to_col != from_col and self.board[to_row][to_col] is None:
                return 'en passant'
        if piece == 'king':
            if to_col - from_col == 2:
                return 'short castle'
            if to_col - from_col == -2:
                return 'long castle'
        if self.board[to_row][to_col] is not None:
            return 'capture'
        return 'normal'

    def make_move(self, move: Move):
        """
        Make a move on the board.
        Update the board state and move stack, flip the 
        colour to move, and draw the updated board.
        """
        match move.move_type:
            case "normal":
                self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
                self.board[move.from_row][move.from_col] = None
            case "capture":
                self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
                self.board[move.from_row][move.from_col] = None
            case "long castle":
                assert move.from_row == move.to_row
                assert move.to_col == 2
                assert move.from_col == 4
                self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
                self.board[move.from_row][move.from_col] = None
                self.board[move.to_row][move.to_col + 1] = self.board[move.from_row][0]
                self.board[move.from_row][0] = None
            case "short castle":
                assert move.from_row == move.to_row
                assert move.to_col == 6
                assert move.from_col == 4
                self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
                self.board[move.from_row][move.from_col] = None
                self.board[move.to_row][move.to_col - 1] = self.board[move.from_row][7]
                self.board[move.from_row][7] = None
            case "promotion":
                self.board[move.to_row][move.to_col] = move.promoted_piece
                self.board[move.from_row][move.from_col] = None
            case "en passant":
                self.board[move.to_row][move.to_col] = self.board[move.from_row][move.from_col]
                self.board[move.from_row][move.from_col] = None
                self.board[move.from_row][move.to_col] = None
        self.colour_to_move = self.colour_to_move.flipped()
        self.move_stack.push(move)
        self.input_buffer.flush()
        self.draw_board()

    def run(self):
        """
        Fire up the GUI. Let the user play against the engine.
        """
        self.draw_board()
        self.start_engine()
        self.test_engine()
        if self.engine_colour == self.colour_to_move:
            self.make_engine_move()
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
